
import asyncio
import hashlib
from datetime import datetime, date
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
import requests
from bs4 import BeautifulSoup
from typing import Dict, Any, Set, Optional


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

app = FastAPI(title="Polytech Schedule API", version="1.4.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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
    
    week_number = (diff_days // 7) + 1
    week_number = max(1, min(20, week_number))
    
    real_week_num = (diff_days // 7) + 1
    week_type = "Числитель" if real_week_num % 2 != 0 else "Знаменатель"
    
    return week_number, week_type

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
    
    raw_buckets_group = {}
    raw_buckets_teacher = {}

    print(f"--- PARSING XML ({len(all_records)} records) ---")

    for record in all_records:
        date_str = get_tag_text(record, 'DAT')
        if not date_str: continue
        
        dt_object = datetime.fromisoformat(date_str)
        formatted_date = dt_object.strftime('%Y-%m-%d')
        
        group_tags = record.find_all('SPGRUP.NAIM')
        groups_in_record = [t.text.strip() for t in group_tags if t.text.strip()]
        
        is_stream_xml = len(groups_in_record) > 1
        
        subgroup = safe_int(get_tag_text(record, 'IDGG'))
        subject_name = get_tag_text(record, 'SPPRED.NAIM')
        teacher_name = get_tag_text(record, 'FAMIO')
        zam_val = get_tag_text(record, 'ZAM', '0')
        
        status = 'ok'
        subj_upper = subject_name.upper().strip()
        
        if "ОТМЕНА" in subj_upper:
            status = 'cancellation'
        elif zam_val != '0':
            status = 'replacement'
            
        lesson_data = {
            'lesson_number': safe_int(get_tag_text(record, 'UR')),
            'subject': subject_name,
            'teacher': teacher_name,
            'subgroup': subgroup,
            'is_stream': is_stream_xml,
            'status': status,
            'group_list': groups_in_record,
            'original_subject': None
        }
        for group_name in groups_in_record:
            all_groups.add(group_name)
            if group_name not in raw_buckets_group: raw_buckets_group[group_name] = {}
            if formatted_date not in raw_buckets_group[group_name]: raw_buckets_group[group_name][formatted_date] = {}
            key = (lesson_data['lesson_number'], subgroup)
            if key not in raw_buckets_group[group_name][formatted_date]: raw_buckets_group[group_name][formatted_date][key] = []
            raw_buckets_group[group_name][formatted_date][key].append(lesson_data)

        if teacher_name:
            all_teachers.add(teacher_name)
            if teacher_name not in raw_buckets_teacher: raw_buckets_teacher[teacher_name] = {}
            if formatted_date not in raw_buckets_teacher[teacher_name]: raw_buckets_teacher[teacher_name][formatted_date] = {}
            key = (lesson_data['lesson_number'], subgroup)
            if key not in raw_buckets_teacher[teacher_name][formatted_date]: raw_buckets_teacher[teacher_name][formatted_date][key] = []
            
            t_lesson = lesson_data.copy()
            t_lesson['group'] = groups_in_record[0] if groups_in_record else ""
            raw_buckets_teacher[teacher_name][formatted_date][key].append(t_lesson)

    def resolve_conflicts(buckets, is_teacher_mode=False):
        final_data = {}
        day_names_ru = ["Понедельник", "Вторник", "Среда", "Четверг", "Пятница", "Суббота", "Воскресенье"]

        for entity, dates in buckets.items():
            final_data[entity] = {}
            for date_str, slots in dates.items():
                dt_obj = datetime.strptime(date_str, '%Y-%m-%d')
                final_lessons = []
                
                for (lesson_num, sub), candidates in slots.items():
                    all_participating_groups = set()
                    for cand in candidates:
                        for g in cand.get('group_list', []):
                            all_participating_groups.add(g)
                    
                    is_calculated_stream = len(all_participating_groups) > 1

                    cancellation = next((x for x in candidates if x['status'] == 'cancellation'), None)
                    replacement = next((x for x in candidates if x['status'] == 'replacement'), None)
                    original = next((x for x in candidates if x['status'] == 'ok'), None)
                    
                    winner = None
                    if cancellation:
                        winner = cancellation.copy()
                        if original:
                            winner['original_subject'] = original['subject']
                            if not winner['teacher']: winner['teacher'] = original['teacher']
                    elif replacement:
                        winner = replacement.copy()
                        if original:
                            winner['original_subject'] = original['subject']
                    elif original:
                        winner = original.copy()
                    else:
                        winner = candidates[-1].copy()

                    winner['is_stream'] = is_calculated_stream
                    if is_calculated_stream:
                        sorted_groups = sorted(list(all_participating_groups))
                        if is_teacher_mode:
                            if len(sorted_groups) > 3:
                                winner['group'] = f"Поток ({len(sorted_groups)} гр.)"
                            else:
                                winner['group'] = ", ".join(sorted_groups)
                    if "ОТМЕНА" in winner['subject'].upper():
                        winner['status'] = 'cancellation'
                        winner['subject'] = "ОТМЕНА"

                    final_lessons.append(winner)

                final_lessons.sort(key=lambda x: x['lesson_number'])
                final_data[entity][date_str] = {
                    'day_name': day_names_ru[dt_obj.weekday()],
                    'lessons': final_lessons
                }
        return final_data

    return {
        "groups": resolve_conflicts(raw_buckets_group, is_teacher_mode=False),
        "teachers": resolve_conflicts(raw_buckets_teacher, is_teacher_mode=True)
    }

async def update_cache_task():
    while True:
        print("CRON: Checking updates...")
        for week_num in range(1, 21): 
            url = f"http://polytech-shedule.ru/{week_num}.xml"
            try:
                response = requests.get(url, timeout=10)
                if response.status_code == 200:
                    content = response.content
                    new_hash = hashlib.md5(content).hexdigest()
                    if file_hashes.get(str(week_num)) != new_hash:
                        print(f"CRON: Week {week_num} updated.")
                        schedule_cache[str(week_num)] = parse_xml_to_json(content.decode('utf-8'))
                        file_hashes[str(week_num)] = new_hash
            except requests.RequestException:
                pass
            await asyncio.sleep(0.1)
        print("CRON: Done. Sleeping 1 hour.")
        await asyncio.sleep(3600)

@app.on_event("startup")
async def on_startup():
    asyncio.create_task(update_cache_task())

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
        raise HTTPException(400, "Group or teacher required")

    date_str = date.strftime('%Y-%m-%d')
    week_idx, week_type = calculate_week_info(date)
    
    found_schedule = None
    
    for week_key, week_data in schedule_cache.items():
        if not week_data: continue
            
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

@app.get("/api/meta/active_days_range")
async def get_active_days_for_range(
    start_date: date,
    end_date: date,
    group: Optional[str] = None,
    teacher: Optional[str] = None
):
    """Отдает активные дни в заданном диапазоне дат."""
    active_days = set()
    for week_data in schedule_cache.values():
        if not week_data: continue
        
        target_dict = week_data["groups"] if group else week_data["teachers"]
        key = group if group else teacher
        
        if key in target_dict:
            for date_str in target_dict[key].keys():
                try:
                    date_obj = date.fromisoformat(date_str)
                    if start_date <= date_obj <= end_date:
                        active_days.add(date_str)
                except ValueError:
                    continue
                    
    return {"active_days": sorted(list(active_days))}

@app.get("/api/meta/active_days")
async def get_active_days(
    month: str = Query(..., regex=r"^\d{4}-\d{2}$"),
    group: Optional[str] = None,
    teacher: Optional[str] = None
):
    active_days = set()
    for week_data in schedule_cache.values():
        if not week_data: continue
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
