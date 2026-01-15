import { defineStore } from "pinia";
import type {
  ScheduleCache,
  DaySchedule,
  SearchResponse,
  ActiveDaysResponse,
} from "@/types";
import { apiClient } from "@/api/index";

const formatDate = (date: Date): string => date.toISOString().substring(0, 10);

export const useMainStore = defineStore("main", {
  state: () => ({
    userGroup: null as string | null,
    userTeacher: null as string | null,
    userSubgroup: 0,
    scheduleCache: {} as ScheduleCache,
    activeDays: new Set<string>(),
    isLoading: false,
  }),

  getters: {
    // Зарегистрирован, если есть группа ИЛИ учитель
    isRegistered: (state): boolean => !!state.userGroup || !!state.userTeacher,
    getDaySchedule: (state) => (date: string) => state.scheduleCache[date],
    // Текстовое описание текущего режима
    currentModeTitle: (state) =>
      state.userTeacher ? state.userTeacher : state.userGroup,
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

    clearCache() {
      this.scheduleCache = {};
      this.activeDays.clear();
    },

    // --- ИСПРАВЛЕНО: Добавлен метод ensureDayLoaded ---
    async ensureDayLoaded(date: string) {
      if (this.scheduleCache[date]) return; // Если уже в кэше, не грузим
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
        console.warn(`ensureDayLoaded error for ${date}`, e);
      }
    },
    // --------------------------------------------------

    async loadDayWindow(centerDateStr: string) {
      if (!this.isRegistered) return [];

      const center = new Date(centerDateStr);
      // Грузим [-1, 0, 1] дни
      const datesToLoad = [-1, 0, 1].map((offset) => {
        const d = new Date(center);
        d.setDate(d.getDate() + offset);
        return formatDate(d);
      });

      // Используем ensureDayLoaded для загрузки каждого дня
      await Promise.all(datesToLoad.map((date) => this.ensureDayLoaded(date)));

      return datesToLoad.map((date) => ({
        date,
        schedule: this.scheduleCache[date] || null,
      }));
    },

    async fetchActiveDays(month: string) {
      if (!this.isRegistered) return;
      try {
        const params = new URLSearchParams();
        params.append("month", month);
        if (this.userGroup) params.append("group", this.userGroup);
        if (this.userTeacher) params.append("teacher", this.userTeacher);

        const data = await apiClient.get<ActiveDaysResponse>(
          `/meta/active_days?${params.toString()}`
        );
        this.activeDays.clear();
        data.active_days.forEach((day) => this.activeDays.add(day));
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
