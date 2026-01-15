import { defineStore } from "pinia";
import type { ScheduleCache, DaySchedule } from "@/types";
import { apiClient } from "@/index";

const formatDate = (date: Date): string => date.toISOString().substring(0, 10);

export const useMainStore = defineStore("main", {
  state: () => ({
    userGroup: null as string | null,
    userTeacher: null as string | null,
    userSubgroup: 0,

    // КЭШ
    scheduleCache: {} as ScheduleCache,
    activeDays: new Set<string>(),
    isLoading: false,

    // НОВОЕ: Дата, которую сейчас смотрит пользователь (для заголовка)
    viewedDate: new Date().toISOString().substring(0, 10),
  }),

  getters: {
    isRegistered: (state): boolean => !!state.userGroup || !!state.userTeacher,
    getDaySchedule: (state) => (date: string) => state.scheduleCache[date],
    currentModeTitle: (state) =>
      state.userTeacher ? state.userTeacher : state.userGroup,

    // Геттер для заголовка, берет данные из viewedDate
    currentWeekInfo: (state) => {
      const schedule = state.scheduleCache[state.viewedDate];
      if (schedule?.week_type) {
        return `${schedule.week_number}-я нед. (${schedule.week_type})`;
      }
      // Если данных нет, пробуем хотя бы посчитать неделю (тут можно fallback логику, но пока пустая строка)
      return "";
    },
  },

  actions: {
    initializeStore() {
      this.userGroup = localStorage.getItem("userGroup");
      this.userTeacher = localStorage.getItem("userTeacher");
      const sub = localStorage.getItem("userSubgroup");
      this.userSubgroup = sub ? parseInt(sub) : 0;
    },

    setGroup(group: string) {
      this.userGroup = group;
      this.userTeacher = null;
      localStorage.setItem("userGroup", group);
      localStorage.removeItem("userTeacher");
      this.clearCache();
    },

    setTeacher(teacher: string) {
      this.userTeacher = teacher;
      this.userGroup = null;
      localStorage.setItem("userTeacher", teacher);
      localStorage.removeItem("userGroup");
      this.clearCache();
    },

    setSubgroup(subgroup: number) {
      this.userSubgroup = subgroup;
      localStorage.setItem("userSubgroup", subgroup.toString());
    },

    setViewedDate(date: string) {
      this.viewedDate = date;
    },

    clearCache() {
      this.scheduleCache = {};
      this.activeDays.clear();
    },

    async ensureDayLoaded(date: string) {
      if (this.scheduleCache[date]) return;
      if (!this.isRegistered) return;

      try {
        const params = new URLSearchParams();
        params.append("date", date);
        if (this.userGroup) params.append("group", this.userGroup);
        if (this.userTeacher) params.append("teacher", this.userTeacher);

        const data = await apiClient.get<DaySchedule>(
          `/schedule/day?${params.toString()}`
        );
        if (data) {
          this.scheduleCache[date] = data;
        }
      } catch (e) {
        // ignore
      }
    },

    async loadDayWindow(centerDateStr: string) {
      // Logic for swiper preloading if needed
    },

    async fetchActiveDays(month: string) {
      // ... (код календаря без изменений)
      try {
        const params = new URLSearchParams();
        params.append("month", month);
        if (this.userGroup) params.append("group", this.userGroup);
        if (this.userTeacher) params.append("teacher", this.userTeacher);

        const data = await apiClient.get<any>(
          `/meta/active_days?${params.toString()}`
        );
        this.activeDays.clear();
        data.active_days.forEach((day: string) => this.activeDays.add(day));
      } catch (e) {
        console.error(e);
      }
    },

    async search(query: string, type: "group" | "teacher"): Promise<string[]> {
      if (query.length < 2) return [];
      this.isLoading = true;
      try {
        const endpoint =
          type === "group" ? "/groups/search" : "/teachers/search";
        const data = await apiClient.get<any>(`${endpoint}?query=${query}`);
        return type === "group" ? data.groups : data.teachers;
      } catch (e) {
        return [];
      } finally {
        this.isLoading = false;
      }
    },
  },
});
