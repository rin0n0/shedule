import asyncio
import hashlib
from datetime import datetime, date, timedelta
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
import requests
from bs4 import BeautifulSoup
from typing import Dict, Any, List, Set, Optional

# --- КОНФИГУРАЦИЯ ---
origins = [
    "http://localhost",
    "http://localhost:8080",
    "http://localhost:5173",
    "https://polytech-schedule.ru",
    "http://polytech-schedule.ru",
]

# --- ГЛОБАЛЬНЫЕ ХРАНИЛИЩА (КЭШ) ---
# Структура: { "week_num": { "groups": {...}, "teachers": {...} } }
schedule_cache: Dict[str, Dict[str, Any]] = {}
file_hashes: Dict[str, str] = {}
all_groups: Set[str] = set()
all_teachers: Set[str] = set() # Новое: список преподавателей

app = FastAPI(title="Polytech Schedule API", version="1.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- ЛОГИКА НЕДЕЛЬ (ПОРТ LEGACY JS) ---

def calculate_week_info(target_date: date = None):
    """
    Порт функции calculateCurrentWeek из legacy JS.
    Возвращает номер недели и тип (Числитель/Знаменатель).
    """
    if target_date is None:
        target_date = date.today()
    
    current_year = target_date.year
    
    # 1. Определяем границы учебного года
    if target_date.month >= 9: # Сентябрь - Декабрь
        academic_year_start = date(current_year, 9, 1)
        academic_year_end = date(current_year + 1, 7, 3)
    else: # Январь - Август
        academic_year_start = date(current_year - 1, 9, 1)
        academic_year_end = date(current_year, 7, 3)
        
    # Проверка на выход за границы учебного года
    if target_date < academic_year_start or target_date > academic_year_end:
        return 1, "Числитель"

    # 2. Обработка каникул (5-11 января)
    # В legacy: holidaysStart = new Date(currentYear, 0, 5); (месяц 0 = Январь)
    holidays_start = date(current_year, 1, 5)
    holidays_end = date(current_year, 1, 11)
    
    calc_date = target_date
    if holidays_start <= target_date <= holidays_end:
        # Если каникулы, считаем неделю ДО каникул
        calc_date = holidays_start 

    # 3. Расчет номера недели
    # Устанавливаем время на 12:00 чтобы избежать проблем с переходом дат (в JS),
    # но в Python date() это просто разница дней.
    diff = calc_date - academic_year_start
    diff_days = diff.days
    
    # weekNumber = Math.floor(diffDays / 14) + 1;
    # Тут legacy логика считает 14-дневными циклами, но возвращает номер 1-20
    # Это странно для классического расписания, но сохраняем логику "циклов".
    # Обычно (diff_days // 7) + 1 - это календарная учебная неделя.
    # Legacy logic:
    week_number = (diff_days // 14) + 1
    week_number = max(1, min(20, week_number))
    
    # Определяем Числитель/Знаменатель
    # Обычно нечетная = числитель, четная = знаменатель.
    # Но legacy код странно считает weekNumber (раз в 14 дней). 
    # В legacy updateSchedule грузит XML по `currentWeek`.
    # Предполагаем, что XML файлы 1.xml ... 20.xml содержат полные 2 недели?
    # Или weekNumber в legacy - это именно "Учебная неделя" (числитель/знаменатель).
    # Давайте сделаем классический расчет для UI, но для загрузки XML оставим legacy.
    
    # КОРРЕКЦИЯ ДЛЯ UI: Реальный номер недели от начала года
    real_week_num = (diff_days // 7) + 1
    week_type = "Числитель" if real_week_num % 2 != 0 else "Знаменатель"
    
    return week_number, week_type

# --- ЛОГИКА ПАРСЕРА ---

def get_tag_text(node, tag_name, default=''):
    tag = node.find(tag_name)
    return tag.text.strip() if tag else default

def safe_int(value, default=0):
    try:
        return int(value)
    except (ValueError, TypeError):
        return default

def parse_xml_to_json(xml_content: str) -> Dict[str, Any]:
    global all_groups, all_teachers
    soup = BeautifulSoup(xml_content, 'lxml-xml')
    all_records = soup.find_all('My')
    
    data_by_group = {}
    data_by_teacher = {}

    for record in all_records:
        date_str = get_tag_text(record, 'DAT')
        if not date_str: continue

        dt_object = datetime.fromisoformat(date_str)
        formatted_date = dt_object.strftime('%Y-%m-%d')
        
        # Определяем флаги
        subgroup = safe_int(get_tag_text(record, 'IDGG'))
        # Если ZAM != 0, это замена. Также legacy ищет 'ОТМЕНА' в названии
        zam_val = get_tag_text(record, 'ZAM', '0')
        subject_name = get_tag_text(record, 'SPPRED.NAIM')
        
        is_replacement = zam_val != '0' or "ОТМЕНА" in subject_name.upper()
        
        # Данные преподавателя
        teacher_name = get_tag_text(record, 'FAMIO')
        # Данные группы
        group_name = get_tag_text(record, 'SPGRUP.NAIM')

        lesson_info = {
            'lesson_number': safe_int(get_tag_text(record, 'UR')),
            'subject': subject_name,
            'teacher': teacher_name,
            'group': group_name, # Нужно для вида преподавателя
            'subgroup': subgroup,
            'is_replacement': is_replacement
        }

        # --- ИНДЕКСАЦИЯ ПО ГРУППАМ ---
        if group_name:
            all_groups.add(group_name)
            if group_name not in data_by_group:
                data_by_group[group_name] = {}
            if formatted_date not in data_by_group[group_name]:
                data_by_group[group_name][formatted_date] = {'lessons': []}
            data_by_group[group_name][formatted_date]['lessons'].append(lesson_info)

        # --- ИНДЕКСАЦИЯ ПО ПРЕПОДАВАТЕЛЯМ ---
        if teacher_name:
            all_teachers.add(teacher_name)
            if teacher_name not in data_by_teacher:
                data_by_teacher[teacher_name] = {}
            if formatted_date not in data_by_teacher[teacher_name]:
                data_by_teacher[teacher_name][formatted_date] = {'lessons': []}
            data_by_teacher[teacher_name][formatted_date]['lessons'].append(lesson_info)

    # Пост-обработка (сортировка и дни недели)
    day_names_ru = ["Понедельник", "Вторник", "Среда", "Четверг", "Пятница", "Суббота", "Воскресенье"]
    
    def process_dict(d):
        for entity, days in d.items():
            for date_str, day_data in days.items():
                dt_obj = datetime.strptime(date_str, '%Y-%m-%d')
                day_data['day_name'] = day_names_ru[dt_obj.weekday()]
                day_data['lessons'].sort(key=lambda x: x['lesson_number'])
    
    process_dict(data_by_group)
    process_dict(data_by_teacher)

    return {"groups": data_by_group, "teachers": data_by_teacher}

async def update_cache_task():
    while True:
        print("CRON: Запускаю задачу обновления кэша...")
        # Legacy использует 1.xml ... 20.xml. Сканируем их.
        for week_num in range(1, 21): 
            url = f"http://polytech-shedule.ru/{week_num}.xml"
            try:
                response = requests.get(url, timeout=10)
                if response.status_code == 200:
                    content = response.content
                    new_hash = hashlib.md5(content).hexdigest()
                    
                    if file_hashes.get(str(week_num)) != new_hash:
                        print(f"CRON: Обновляю неделю {week_num}...")
                        schedule_cache[str(week_num)] = parse_xml_to_json(content.decode('utf-8'))
                        file_hashes[str(week_num)] = new_hash
            except requests.RequestException:
                pass
            await asyncio.sleep(0.1)
        
        print("CRON: Готово. Сплю 1 час.")
        await asyncio.sleep(3600)

@app.on_event("startup")
async def on_startup():
    asyncio.create_task(update_cache_task())

# --- ENDPOINTS ---

@app.get("/api/groups/search")
async def search_groups(query: str = Query(..., min_length=2)):
    if not all_groups: return {"groups": []}
    results = [g for g in sorted(list(all_groups)) if query.lower() in g.lower()]
    return {"groups": results[:20]}

@app.get("/api/teachers/search")
async def search_teachers(query: str = Query(..., min_length=2)):
    if not all_teachers: return {"teachers": []}
    results = [t for t in sorted(list(all_teachers)) if query.lower() in t.lower()]
    return {"teachers": results[:20]}

@app.get("/api/schedule/day")
async def get_schedule_for_day(
    date: date,
    group: Optional[str] = None,
    teacher: Optional[str] = None
):
    """
    Универсальный эндпоинт. Принимает либо group, либо teacher.
    Возвращает расписание и метаданные недели.
    """
    if not group and not teacher:
        raise HTTPException(400, "Укажите group или teacher")

    date_str = date.strftime('%Y-%m-%d')
    week_idx, week_type = calculate_week_info(date)
    
    # Ищем в кэше (перебираем все загруженные недели, так как дата может быть в любом XML)
    # Оптимизация: в идеале mapping date->week_xml, но пока bruteforce по кэшу
    
    found_schedule = None
    
    for week_data in schedule_cache.values():
        target_dict = week_data["groups"] if group else week_data["teachers"]
        key = group if group else teacher
        
        if key in target_dict and date_str in target_dict[key]:
            found_schedule = target_dict[key][date_str]
            break
            
    # Если расписания нет, возвращаем пустую структуру, но с метаданными
    response = found_schedule if found_schedule else {
        "day_name": "", # Фронт сам вычислит
        "lessons": []
    }
    
    # Оборачиваем ответ
    return {
        **response,
        "week_number": week_idx,
        "week_type": week_type
    }

@app.get("/api/meta/active_days")
async def get_active_days(
    month: str = Query(..., regex=r"^\d{4}-\d{2}$"),
    group: Optional[str] = None,
    teacher: Optional[str] = None
):
    active_days = set()
    for week_data in schedule_cache.values():
        target_dict = week_data["groups"] if group else week_data["teachers"]
        key = group if group else teacher
        
        if key in target_dict:
            for date_str in target_dict[key].keys():
                if date_str.startswith(month):
                    active_days.add(date_str)
    return {"active_days": sorted(list(active_days))}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)