import asyncio
import json
import hashlib
from datetime import datetime, date, timedelta
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
import requests
from bs4 import BeautifulSoup
from typing import Dict, Any, List, Set

# --- КОНФИГУРАЦИЯ ---
# Список доменов, с которых фронтенд будет обращаться к этому бекенду
origins = [
    "http://localhost",
    "http://localhost:8080", # Стандартный порт для Vue dev server
    "http://localhost:5173", # Стандартный порт для Vite
    "https://polytech-schedule.ru", # Твой будущий домен
    "http://polytech-schedule.ru",
]

# --- ГЛОБАЛЬНЫЕ ХРАНИЛИЩА (КЭШ) ---
# Здесь мы будем хранить скачанные и обработанные данные, чтобы не парсить их каждый раз
# Ключ - номер недели (строка), значение - распарсенный JSON расписания для ВСЕХ групп
schedule_cache: Dict[str, Dict[str, Any]] = {}
# Хранит хэши скачанных файлов, чтобы проверять, изменились ли они
file_hashes: Dict[str, str] = {}
# Множество всех уникальных групп, найденных в расписании
all_groups: Set[str] = set()


# --- ИНИЦИАЛИЗАЦИЯ FASTAPI ПРИЛОЖЕНИЯ ---
app = FastAPI(
    title="Polytech Schedule API",
    description="Суверенный бекенд для суверенного расписания.",
    version="1.0.0"
)

# Добавляем middleware для CORS, чтобы фронтенд мог делать запросы
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# --- ЛОГИКА ПАРСЕРА И КЭШИРОВАНИЯ (МОЗГ) ---

def get_tag_text(node, tag_name, default=''):
    tag = node.find(tag_name)
    return tag.text.strip() if tag else default

def safe_int(value, default=0):
    try:
        return int(value)
    except (ValueError, TypeError):
        return default

def parse_xml_to_json(xml_content: str) -> Dict[str, Any]:
    """Главная функция парсинга. Превращает сырой XML в структурированный словарь."""
    global all_groups
    soup = BeautifulSoup(xml_content, 'lxml-xml')
    all_records = soup.find_all('My')
    
    # Временный словарь для группировки по группам, а потом по дням
    parsed_data = {}

    for record in all_records:
        date_str = get_tag_text(record, 'DAT')
        if not date_str:
            continue

        dt_object = datetime.fromisoformat(date_str)
        formatted_date = dt_object.strftime('%Y-%m-%d')
        
        lesson_info = {
            'lesson_number': safe_int(get_tag_text(record, 'UR')),
            'subject': get_tag_text(record, 'SPPRED.NAIM'),
            'teacher': get_tag_text(record, 'FAMIO'),
            'subgroup': safe_int(get_tag_text(record, 'IDGG')),
            'is_replacement': get_tag_text(record, 'ZAM', '0') != '0'
        }

        group_tags = record.find_all('SPGRUP.NAIM')
        for tag in group_tags:
            group_name = tag.text.strip()
            if not group_name: continue

            all_groups.add(group_name) # Пополняем общий список групп

            # Создаем записи в нашем словаре, если их нет
            if group_name not in parsed_data:
                parsed_data[group_name] = {}
            if formatted_date not in parsed_data[group_name]:
                parsed_data[group_name][formatted_date] = {'lessons': []}
            
            parsed_data[group_name][formatted_date]['lessons'].append(lesson_info)
            
    # Добавляем дни недели и сортируем пары
    day_names_ru = ["Понедельник", "Вторник", "Среда", "Четверг", "Пятница", "Суббота", "Воскресенье"]
    for group, days in parsed_data.items():
        for date_str, day_data in days.items():
            dt_obj = datetime.strptime(date_str, '%Y-%m-%d')
            day_data['day_name'] = day_names_ru[dt_obj.weekday()]
            day_data['lessons'].sort(key=lambda x: x['lesson_number'])
            
    return parsed_data

async def update_cache_task():
    """Фоновая задача, которая раз в час проверяет и обновляет расписание."""
    while True:
        print("CRON: Запускаю задачу обновления кэша...")
        for week_num in range(1, 21): # Проверяем 20 учебных недель
            url = f"http://polytech-shedule.ru/{week_num}.xml"
            try:
                response = requests.get(url, timeout=10)
                if response.status_code == 200:
                    content = response.content # Берем байты для хэширования
                    new_hash = hashlib.md5(content).hexdigest()
                    
                    if file_hashes.get(str(week_num)) != new_hash:
                        print(f"CRON: Обнаружены изменения для недели {week_num}. Обновляю кэш...")
                        schedule_cache[str(week_num)] = parse_xml_to_json(content.decode('utf-8'))
                        file_hashes[str(week_num)] = new_hash
                    else:
                        # print(f"CRON: Неделя {week_num} без изменений.")
                        pass

            except requests.RequestException:
                # print(f"CRON: Не удалось скачать неделю {week_num}.")
                pass
            await asyncio.sleep(0.1) # Небольшая пауза, чтобы не душить сеть
        
        print("CRON: Задача обновления кэша завершена. Следующий запуск через час.")
        await asyncio.sleep(3600) # Пауза на 1 час

@app.on_event("startup")
async def on_startup():
    """При старте сервера запускаем фоновую задачу обновления кэша."""
    asyncio.create_task(update_cache_task())


# --- API ЭНДПОИНТЫ (то, что будет просить фронтенд) ---

@app.get("/")
def read_root():
    return {"status": "Суверенный бекенд запущен и готов к работе!"}

@app.get("/api/groups/search")
async def search_groups(query: str = Query(..., min_length=2)):
    """Поиск групп по части названия. Нужно для экрана регистрации."""
    if not all_groups:
        raise HTTPException(status_code=404, detail="Список групп еще не загружен. Попробуйте через минуту.")
    
    # Ищем все группы, где есть вхождение query, без учета регистра
    results = [group for group in sorted(list(all_groups)) if query.lower() in group.lower()]
    return {"groups": results[:20]} # Возвращаем не больше 20 совпадений

@app.get("/api/schedule/day")
async def get_schedule_for_day(group: str, date: date):
    """Отдает расписание на один конкретный день."""
    # TODO: Написать логику определения номера недели по дате.
    # Пока для простоты ищем по всем закэшированным неделям.
    
    date_str = date.strftime('%Y-%m-%d')
    
    for week_data in schedule_cache.values():
        if group in week_data and date_str in week_data[group]:
            return week_data[group][date_str]

    # Если ничего не нашли после поиска по всему кэшу
    raise HTTPException(status_code=404, detail=f"Расписание для группы {group} на дату {date_str} не найдено.")

@app.get("/api/meta/active_days")
async def get_active_days_for_month(group: str, month: str = Query(..., regex=r"^\d{4}-\d{2}$")):
    """Отдает список дней в месяце, на которые есть пары. Нужно для календаря."""
    active_days = set()
    
    for week_data in schedule_cache.values():
        if group in week_data:
            for date_str in week_data[group].keys():
                if date_str.startswith(month):
                    active_days.add(date_str)
                    
    if not active_days:
        raise HTTPException(status_code=404, detail=f"В месяце {month} не найдено активных дней для группы {group}.")
        
    return {"active_days": sorted(list(active_days))}

# --- ЗАПУСК СЕРВЕРА (для локальной разработки) ---
# Этот блок выполняется, только если запустить файл напрямую: python main.py
if __name__ == "__main__":
    import uvicorn
    # uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
    # Для Pydroid и других окружений без reload=True может быть стабильнее:
    uvicorn.run(app, host="0.0.0.0", port=8000)