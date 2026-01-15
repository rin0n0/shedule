
import asyncio
import hashlib
from datetime import datetime, date
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
import requests
from bs4 import BeautifulSoup
from typing import Dict, Any, Set, Optional

# ... (Конфигурация origins и кэш остаются без изменений) ...
origins = [
    "http://localhost",
    "http://localhost:8080",
    "http://localhost:5173",
    "https://polytech-schedule.ru",
    "http://polytech-schedule.ru",
]

schedule_cache: Dict[str, Dict[str, Any]] = {}
file_hashes: Dict[str, str] = {}
all_groups: Set[str] = set()
all_teachers: Set[str] = set()

app = FastAPI(title="Polytech Schedule API", version="1.2.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ... (Функция calculate_week_info остается без изменений) ...
def calculate_week_info(target_date: date = None):
    if target_date is None:
        target_date = date.today()
    
    current_year = target_date.year
    if target_date.month >= 9:
        academic_year_start = date(current_year, 9, 1)
        academic_year_end = date(current_year + 1, 7, 3)
    else:
        academic_year_start = date(current_year - 1, 9, 1)
        academic_year_end = date(current_year, 7, 3)
        
    if target_date < academic_year_start or target_date > academic_year_end:
        return 1, "Числитель"

    holidays_start = date(current_year, 1, 5)
    holidays_end = date(current_year, 1, 11)
    
    calc_date = target_date
    if holidays_start <= target_date <= holidays_end:
        calc_date = holidays_start 

    diff = calc_date - academic_year_start
    diff_days = diff.days
    
    # Расчет для Legacy API (1-20)
    week_number = (diff_days // 14) + 1
    week_number = max(1, min(20, week_number))
    
    # Расчет для UI (Числитель/Знаменатель)
    real_week_num = (diff_days // 7) + 1
    week_type = "Числитель" if real_week_num % 2 != 0 else "Знаменатель"
    
    return week_number, week_type

# --- НОВАЯ ЛОГИКА ПАРСЕРА ---

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
        
        # 1. Определяем группы и Поток
        group_tags = record.find_all('SPGRUP.NAIM')
        groups_in_record = [t.text.strip() for t in group_tags if t.text.strip()]
        
        # Если групп больше 1 — это поток
        is_stream = len(groups_in_record) > 1
        
        subgroup = safe_int(get_tag_text(record, 'IDGG'))
        subject_name = get_tag_text(record, 'SPPRED.NAIM')
        teacher_name = get_tag_text(record, 'FAMIO')
        zam_val = get_tag_text(record, 'ZAM', '0')
        
        # 2. Определяем статус (Отмена/Замена/Ок)
        status = 'ok'
        if "ОТМЕНА" in subject_name.upper():
            status = 'cancellation'
        elif zam_val != '0':
            status = 'replacement'
            
        lesson_info = {
            'lesson_number': safe_int(get_tag_text(record, 'UR')),
            'subject': subject_name,
            'teacher': teacher_name,
            'subgroup': subgroup,
            'is_stream': is_stream,     # NEW
            'status': status,           # NEW: 'ok' | 'replacement' | 'cancellation'
            'group_list': groups_in_record # NEW: Список всех групп на этой паре
        }

        # Индексация по ГРУППАМ
        for group_name in groups_in_record:
            all_groups.add(group_name)
            if group_name not in data_by_group:
                data_by_group[group_name] = {}
            if formatted_date not in data_by_group[group_name]:
                data_by_group[group_name][formatted_date] = {'lessons': []}
            
            # Копия, чтобы модифицировать (например, скрывать other groups) если нужно
            data_by_group[group_name][formatted_date]['lessons'].append(lesson_info)

        # Индексация по ПРЕПОДАВАТЕЛЯМ
        if teacher_name:
            all_teachers.add(teacher_name)
            if teacher_name not in data_by_teacher:
                data_by_teacher[teacher_name] = {}
            if formatted_date not in data_by_teacher[teacher_name]:
                data_by_teacher[teacher_name][formatted_date] = {'lessons': []}
            
            # Для преподавателя поле group в UI может быть списком
            lesson_for_teacher = lesson_info.copy()
            # Для удобства фронта склеим группы в строку, если их много
            lesson_for_teacher['group'] = ", ".join(groups_in_record) if len(groups_in_record) < 3 else "Поток"
            data_by_teacher[teacher_name][formatted_date]['lessons'].append(lesson_for_teacher)

    # Сортировка
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
        print("CRON: Обновление кэша...")
        for week_num in range(1, 21): 
            url = f"http://polytech-shedule.ru/{week_num}.xml"
            try:
                response = requests.get(url, timeout=10)
                if response.status_code == 200:
                    content = response.content
                    new_hash = hashlib.md5(content).hexdigest()
                    
                    if file_hashes.get(str(week_num)) != new_hash:
                        schedule_cache[str(week_num)] = parse_xml_to_json(content.decode('utf-8'))
                        file_hashes[str(week_num)] = new_hash
            except requests.RequestException:
                pass
            await asyncio.sleep(0.1)
        print("CRON: Готово. Сон 1 час.")
        await asyncio.sleep(3600)

@app.on_event("startup")
async def on_startup():
    asyncio.create_task(update_cache_task())

# ... (Endpoints search_groups, search_teachers, active_days остаются те же) ...

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
    if not group and not teacher:
        raise HTTPException(400, "Укажите group или teacher")

    date_str = date.strftime('%Y-%m-%d')
    week_idx, week_type = calculate_week_info(date)
    
    found_schedule = None
    
    # Ищем в кэше
    for week_data in schedule_cache.values():
        target_dict = week_data["groups"] if group else week_data["teachers"]
        key = group if group else teacher
        
        if key in target_dict and date_str in target_dict[key]:
            found_schedule = target_dict[key][date_str]
            break
            
    response = found_schedule if found_schedule else {
        "day_name": "", 
        "lessons": []
    }
    
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