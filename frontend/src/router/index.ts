import { createRouter, createWebHistory } from "vue-router";
import { useMainStore } from "@/stores/main_store";
import ScheduleView from "@/views/ScheduleView.vue";
// УДАЛЯЕМ импорт RegisterView

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: "/:date?",
      name: "Schedule",
      component: ScheduleView,
    },
    // УДАЛЯЕМ роут для /register
  ],
});

router.beforeEach((to, from, next) => {
  const mainStore = useMainStore();

  if (!mainStore.userGroup) {
    // Проверяем userId, который устанавливается при регистрации
    mainStore.initializeStore();
  }

  // Логика переадресации больше не нужна,
  // так как SettingsModal сам откроется, если пользователь не зарегистрирован.
  next();
});

export default router;
