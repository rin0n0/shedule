export interface Lesson {
  lesson_number: number;
  subject: string;
  teacher: string;
  group: string; // Новое: чтобы видеть, у какой группы пара (для режима преподавателя)
  subgroup: number;
  is_replacement: boolean;
}

export interface DaySchedule {
  day_name: string;
  lessons: Lesson[];
  week_number?: number; // Новое
  week_type?: string; // Новое: "Числитель" | "Знаменатель"
}

export type ScheduleCache = Record<string, DaySchedule>;

export interface SearchResponse {
  groups?: string[];
  teachers?: string[];
}

export interface ActiveDaysResponse {
  active_days: string[];
}
