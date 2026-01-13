import { createRouter, createWebHistory } from "vue-router";
import { useMainStore } from "@/stores/main_store";
import ScheduleView from "@/views/ScheduleView.vue";
import RegisterView from "@/views/RegisterView.vue";

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: "/:date?", // :date? - опциональный параметр даты
      name: "Schedule",
      component: ScheduleView,
    },
    {
      path: "/register",
      name: "Register",
      component: RegisterView,
    },
  ],
});

// Навигационный страж
router.beforeEach((to, from, next) => {
  // Pinia store нужно получать внутри, т.к. он инициализируется после роутера
  const mainStore = useMainStore();

  // Инициализируем хранилище, если этого еще не сделали
  if (!mainStore.userId) {
    mainStore.initializeStore();
  }

  if (!mainStore.isRegistered && to.name !== "Register") {
    next({ name: "Register" });
  } else if (mainStore.isRegistered && to.name === "Register") {
    next({ name: "Schedule" });
  } else {
    next();
  }
});

export default router;
