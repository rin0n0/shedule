import { defineStore } from "pinia";
import type {
  ScheduleCache,
  DaySchedule,
  SearchGroupsResponse,
  ActiveDaysResponse,
} from "@/types";

const API_BASE_URL = "/api";

const apiClient = {
  async get<T>(endpoint: string): Promise<T> {
    const response = await fetch(`${endpoint}`);
    if (!response.ok) {
      // Игнорируем 404, чтобы не крашить приложение, если расписания просто нет
      if (response.status === 404) return null as any;
      throw new Error(`Error ${response.status}`);
    }
    return response.json() as Promise<T>;
  },
};

const generateUUID = () => crypto.randomUUID();
// Хелпер для дат
const formatDate = (date: Date): string => date.toISOString().substring(0, 10);

export const useMainStore = defineStore("main", {
  state: () => ({
    userGroup: null as string | null,
    userId: null as string | null,
    userSubgroup: 0,
    scheduleCache: {} as ScheduleCache,
    activeDays: new Set<string>(),
    isLoading: false,
    error: null as string | null,
  }),

  getters: {
    isRegistered: (state): boolean => !!state.userGroup,
    getDaySchedule: (state) => (date: string) => state.scheduleCache[date],
    isRegistredSubgroup: (state): boolean => state.userSubgroup == 0,
  },

  actions: {
    initializeStore() {
      const storedGroup = localStorage.getItem("userGroup");
      const storedSubgroup = localStorage.getItem("userSubgroup");
      const storedUserId = localStorage.getItem("userId");
      if (storedGroup && storedUserId) {
        this.userGroup = storedGroup;
        this.userId = storedUserId;
        this.userSubgroup = storedSubgroup ? parseInt(storedSubgroup) : 0;
      }
    },

    registerGroup(group: string) {
      this.userGroup = group;
      this.userId = generateUUID();
      this.userSubgroup = 0;
      localStorage.setItem("userGroup", this.userGroup);
      localStorage.setItem("userId", this.userId);
      localStorage.setItem("userSubgroup", "0");
    },
    setSubgroup(subgroup: number) {
      this.userSubgroup = subgroup;
      localStorage.setItem("userSubgroup", subgroup.toString());
    },
    // === НОВЫЙ ЭКШН ДЛЯ СВАЙПЕРА ===
    async loadDayWindow(centerDateStr: string) {
      if (!this.userGroup) return [];

      const center = new Date(centerDateStr);
      // Генерируем даты [-1, 0, 1]
      const datesToLoad = [-1, 0, 1].map((offset) => {
        const d = new Date(center);
        d.setDate(d.getDate() + offset);
        return formatDate(d);
      });

      // Грузим параллельно, пропуская те, что уже в кэше
      const promises = datesToLoad.map(async (date) => {
        if (this.scheduleCache[date]) return; // Уже есть

        try {
          const endpoint = `/api/schedule/day?group=${this.userGroup}&date=${date}`;
          const data = await apiClient.get<DaySchedule>(endpoint);
          if (data) {
            this.scheduleCache[date] = data;
          }
        } catch (e) {
          console.warn(`Failed to load ${date}`, e);
        }
      });

      await Promise.all(promises);

      // Возвращаем готовый массив для слайдов
      return datesToLoad.map((date) => ({
        date,
        schedule: this.scheduleCache[date] || null,
      }));
    },

    // Одиночная загрузка (для подгрузки при скролле)
    async ensureDayLoaded(date: string) {
      if (this.scheduleCache[date]) return;
      try {
        const endpoint = `/api/schedule/day?group=${this.userGroup}&date=${date}`;
        const data = await apiClient.get<DaySchedule>(endpoint);
        if (data) this.scheduleCache[date] = data;
      } catch (e) {
        console.warn(e);
      }
    },

    async fetchActiveDays(month: string) {
      if (!this.userGroup) return;
      try {
        const endpoint = `/api/meta/active_days?group=${this.userGroup}&month=${month}`;
        const data = await apiClient.get<ActiveDaysResponse>(endpoint);
        this.activeDays.clear();
        data.active_days.forEach((day: string) => this.activeDays.add(day));
      } catch (e: any) {
        console.error(`Ошибка календаря:`, e);
      }
    },

    async searchGroups(query: string): Promise<string[]> {
      if (query.length < 2) return [];
      this.isLoading = true;
      try {
        const endpoint = `/api/groups/search?query=${query}`;
        const data = await apiClient.get<SearchGroupsResponse>(endpoint);
        return data.groups;
      } catch (e: any) {
        console.error(e);
        return [];
      } finally {
        this.isLoading = false;
      }
    },
  },
});
