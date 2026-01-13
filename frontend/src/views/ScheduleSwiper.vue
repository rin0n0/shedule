<template>
    <div class="swiper-wrapper">
        <div v-if="loading" class="loading-screen">
            <div class="spinner"></div>
        </div>

        <swiper-container :class="{ 'hidden-swiper': loading }" :init="false" ref="swiperRef" direction="vertical"
            class="my-swiper">
            <swiper-slide v-for="day in slides" :key="day.date">
                <DayCard :schedule="day.schedule" :date="day.date" />
            </swiper-slide>
        </swiper-container>
    </div>
</template>

<script setup lang="ts">
import { ref, onMounted, nextTick, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useMainStore } from '@/stores/main_store'
import type { DaySchedule } from '@/types'
import DayCard from './DayCard.vue'
import type { SwiperContainer } from 'swiper/element'

interface Slide {
    date: string;
    schedule: DaySchedule | null;
}

const mainStore = useMainStore()
const route = useRoute()
const router = useRouter()
const swiperRef = ref<SwiperContainer | null>(null)
const slides = ref<Slide[]>([])
const loading = ref(true)
const isInternalNav = ref(false)

const formatDate = (date: Date) => date.toISOString().substring(0, 10);

// === НОВАЯ ФУНКЦИЯ: ПРОПУСК ВОСКРЕСЕНЬЯ ===
const addAcademicDays = (date: Date, days: number): Date => {
    const result = new Date(date);
    result.setDate(result.getDate() + days);

    // Если попали на Воскресенье (0), двигаемся еще на 1 день в ТУ ЖЕ сторону
    if (result.getDay() === 0) {
        const direction = days > 0 ? 1 : -1;
        result.setDate(result.getDate() + direction);
    }
    return result;
}

const initData = async (dateStr: string) => {
    loading.value = true;

    // Если запросили Воскресенье (например, через URL), сдвигаем на Понедельник
    let centerDate = new Date(dateStr);
    if (centerDate.getDay() === 0) {
        centerDate.setDate(centerDate.getDate() + 1);
    }

    // 1. Генерируем слайды: [Вчера*, Сегодня, Завтра*] (* - с учетом пропуска ВС)
    const prevDate = addAcademicDays(centerDate, -1);
    const nextDate = addAcademicDays(centerDate, 1);

    // Массив дат в правильном порядке
    const datesToLoad = [
        formatDate(prevDate),
        formatDate(centerDate),
        formatDate(nextDate)
    ];

    // 2. Грузим данные из стора (он сам разрулит кэш)
    // Мы не используем loadDayWindow из стора напрямую, так как там логика +1/-1 без учета выходных.
    // Лучше загрузить поштучно с нашей "умной" логикой.

    const promises = datesToLoad.map(async (d) => {
        await mainStore.ensureDayLoaded(d);
        return {
            date: d,
            schedule: mainStore.getDaySchedule(d) || null
        };
    });

    slides.value = await Promise.all(promises);

    await nextTick();
    initSwiper();
    loading.value = false;
};

const initSwiper = () => {
    const el = swiperRef.value;
    if (!el) return;

    if ((el as any).swiper) {
        (el as any).swiper.update();
        return;
    }

    const params = {
        initialSlide: 1, // Центр
        mousewheel: { forceToAxis: true, sensitivity: 1 },
        speed: 400,
        virtual: false,
    };
    Object.assign(el, params);

    el.removeEventListener('swiperslidechange', onSlideChange as EventListener);
    el.addEventListener('swiperslidechange', onSlideChange as EventListener);
    el.initialize();
};

const onSlideChange = async (e: Event) => {
    const swiper = (e.target as any).swiper;
    const activeIndex = swiper.activeIndex;
    const currentSlide = slides.value[activeIndex];

    if (!currentSlide) return;

    if (currentSlide.date !== route.params.date) {
        isInternalNav.value = true;
        await router.replace({ params: { date: currentSlide.date } });
        setTimeout(() => { isInternalNav.value = false }, 50);
    }

    // === БЕСКОНЕЧНАЯ ПРОКРУТКА С ПРОПУСКОМ ВС ===
    if (activeIndex >= slides.value.length - 1) {
        // Идем в будущее
        const lastSlideDate = new Date(slides.value[slides.value.length - 1]!.date);
        // Используем нашу функцию для пропуска
        const nextDate = addAcademicDays(lastSlideDate, 1);
        const nextDateStr = formatDate(nextDate);

        await mainStore.ensureDayLoaded(nextDateStr);

        slides.value.push({
            date: nextDateStr,
            schedule: mainStore.getDaySchedule(nextDateStr) || null
        });

        await nextTick();
        swiper.update();
    }
    else if (activeIndex <= 0) {
        // Идем в прошлое
        const firstSlideDate = new Date(slides.value[0]!.date);
        // Используем нашу функцию для пропуска
        const prevDate = addAcademicDays(firstSlideDate, -1);
        const prevDateStr = formatDate(prevDate);

        await mainStore.ensureDayLoaded(prevDateStr);

        slides.value.unshift({
            date: prevDateStr,
            schedule: mainStore.getDaySchedule(prevDateStr) || null
        });

        await nextTick();
        swiper.update();
        swiper.slideTo(activeIndex + 1, 0, false);
    }
};

watch(
    () => route.params.date,
    async (newDate) => {
        if (isInternalNav.value) return;

        const targetDate = Array.isArray(newDate) ? newDate[0] : newDate;
        if (targetDate && typeof targetDate === 'string') {
            const inSlides = slides.value.some(s => s.date === targetDate);
            if (!inSlides) {
                await initData(targetDate);
            } else {
                const idx = slides.value.findIndex(s => s.date === targetDate);
                if (swiperRef.value && (swiperRef.value as any).swiper) {
                    (swiperRef.value as any).swiper.slideTo(idx);
                }
            }
        }
    }
);

onMounted(() => {
    let start = formatDate(new Date());

    // Если сегодня воскресенье — сразу ставим понедельник как старт
    if (new Date().getDay() === 0) {
        start = formatDate(addAcademicDays(new Date(), 1));
    }

    const rDate = route.params.date;
    if (rDate && typeof rDate === 'string' && !isNaN(Date.parse(rDate))) {
        start = rDate;
    }
    initData(start);
});
</script>

<style scoped>
.swiper-wrapper {
    width: 100%;
    height: 100vh;
    position: relative;
    overflow: hidden;
}

.my-swiper {
    width: 100%;
    height: 100%;
    transition: opacity 0.3s ease;
}

.hidden-swiper {
    opacity: 0;
    pointer-events: none;
}

.loading-screen {
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 10;
}

.spinner {
    width: 40px;
    height: 40px;
    border: 4px solid rgba(255, 255, 255, 0.1);
    border-top-color: var(--accent-color);
    border-radius: 50%;
    animation: spin 1s linear infinite;
}

@keyframes spin {
    to {
        transform: rotate(360deg);
    }
}
</style>