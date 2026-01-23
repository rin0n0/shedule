export type LessonStatus = 'ok' | 'replacement' | 'cancellation';

export interface Lesson {
  lesson_number: number;
  subject: string;
  teacher: string;
  group?: string;
  subgroup: number;
  
  is_stream: boolean;
  status: LessonStatus; 
  group_list?: string[];
  
  // Доп поля для истории изменений
  original_subject?: string | null; 
  original_teacher?: string | null; // НОВОЕ ПОЛЕ
}

export interface DaySchedule {
  day_name: string;
  lessons: Lesson[];
  week_number?: number;
  week_type?: string;
}

export type ScheduleCache = Record<string, DaySchedule>;

export interface SearchResponse {
  groups?: string[];
  teachers?: string[];
}

export interface ActiveDaysResponse {
  active_days: string[];
}