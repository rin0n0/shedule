import { createApp } from "vue";
import { createPinia } from "pinia";
import App from "./App.vue";
import router from "./router";
import { register } from "swiper/element/bundle";

// === V-CALENDAR ===
import VCalendar from "v-calendar";
import "v-calendar/style.css";

register();
import "./assets/main.css";

const app = createApp(App);
const pinia = createPinia();

app.use(pinia);
app.use(router);

// Подключаем календарь
app.use(VCalendar, {});

app.mount("#app");
