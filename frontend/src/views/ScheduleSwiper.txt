<template>
    <div class="swiper-wrapper">
        <div v-if="loading" class="loading-screen">
            <div class="spinner"></div>
        </div>

        <swiper-container :class="{ 'hidden-swiper': loading }" :init="false" ref="swiperRef" direction="vertical"
            class="my-swiper">
            <swiper-slide v-for="day in slides" :key="day.date">
                <!-- === ВАЖНО: Слушаем lessonClick и передаем дальше === -->
                <DayCard :schedule="day.schedule" :date="day.date"
                    @lessonClick="(payload) => $emit('lessonClick', payload)" />
            </swiper-slide>
        </swiper-container>
    </div>
</template>

<script setup lang="ts">
import { ref, onMounted, nextTick, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useMainStore } from '@/stores/main_store'
import type { DaySchedule, Lesson } from '@/types' // Импортируем Lesson
import DayCard from './DayCard.vue'
import type { SwiperContainer } from 'swiper/element'

// === ВАЖНО: Объявляем emit ===
defineEmits(['lessonClick']);

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

const formatDate = (date: Date) => {
    const y = date.getFullYear();
    const m = String(date.getMonth() + 1).padStart(2, '0');
    const d = String(date.getDate()).padStart(2, '0');
    return `${y}-${m}-${d}`;
};

const getAcademicToday = (): Date => {
    const now = new Date();
    const hours = now.getHours();
    if (hours >= 18) now.setDate(now.getDate() + 1);
    if (now.getDay() === 0) now.setDate(now.getDate() + 1);
    return now;
};

const addAcademicDays = (date: Date, days: number): Date => {
    const result = new Date(date);
    result.setDate(result.getDate() + days);
    if (result.getDay() === 0) {
        const direction = days > 0 ? 1 : -1;
        result.setDate(result.getDate() + direction);
    }
    return result;
}

const initData = async (dateStr: string) => {
    loading.value = true;
    let centerDate = new Date(dateStr);
    if (centerDate.getDay() === 0) {
        centerDate.setDate(centerDate.getDate() + 1);
    }

    const prevDate = addAcademicDays(centerDate, -1);
    const nextDate = addAcademicDays(centerDate, 1);

    const datesToLoad = [
        formatDate(prevDate),
        formatDate(centerDate),
        formatDate(nextDate)
    ];

    // Используем ensureDayLoaded, который мы починили в прошлом шаге
    await Promise.all(datesToLoad.map(d => mainStore.ensureDayLoaded(d)));

    slides.value = datesToLoad.map(d => ({
        date: d,
        schedule: mainStore.getDaySchedule(d) || null
    }));

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
        initialSlide: 1,
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

    if (activeIndex >= slides.value.length - 1) {
        const lastSlideDate = new Date(slides.value[slides.value.length - 1]!.date);
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
        const firstSlideDate = new Date(slides.value[0]!.date);
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
    let start = formatDate(getAcademicToday());
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