// src/types.ts

/**
 * Описывает одну пару (урок).
 * Это самая маленькая единица нашего расписания.
 */
export interface Lesson {
  lesson_number: number;
  subject: string;
  teacher: string;
  subgroup: number;
  is_replacement: boolean;
}

/**
 * Описывает расписание на один конкретный день.
 */
export interface DaySchedule {
  day_name: string;
  lessons: Lesson[];
}

/**
 * Описывает структуру кэша расписания в нашем хранилище.
 * Ключ - это дата в формате "YYYY-MM-DD".
 */
export type ScheduleCache = Record<string, DaySchedule>;

// --- Типы для ответов API ---

/**
 * Ответ от эндпоинта /api/groups/search
 */
export interface SearchGroupsResponse {
  groups: string[];
}

/**
 * Ответ от эндпоинта /api/meta/active_days
 */
export interface ActiveDaysResponse {
  active_days: string[];
}
