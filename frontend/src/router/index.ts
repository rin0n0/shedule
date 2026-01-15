// src/router/index.ts
import { createRouter, createWebHistory } from "vue-router";
import { useMainStore } from "@/stores/main_store";
import ScheduleView from "@/views/ScheduleView.vue";
// RegisterView удаляем, так как поиск будет внутри SettingsModal

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: "/:date?", // Н
      name: "Schedule",
      component: ScheduleView,
    },
  ],
});

router.beforeEach((to, from, next) => {
  const mainStore = useMainStore();

  if (!(mainStore.userGroup || mainStore.userTeacher)) {
    mainStore.initializeStore();
  }
  next();
});

export default router;
