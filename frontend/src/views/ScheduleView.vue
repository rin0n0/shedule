<!-- src/views/ScheduleView.vue -->
<template>
    <div class="schedule-view">
        <!-- Панель управления (открывает модалки) -->
        <ResponsiveControls @openCalendar="showCalendar = true" @openSettings="showSettings = true" />

        <div class="content-area">
            <!-- Desktop: Grid -->
            <WeekScheduleView v-if="!isMobile" :center-date="currentDate" @lessonClick="openLessonDetails" />

            <!-- Mobile: Swiper -->
            <ScheduleSwiper v-else @lessonClick="openLessonDetails" />
        </div>

        <!-- Модалки -->
        <Transition name="fade">
            <CalendarModal v-if="showCalendar" @close="showCalendar = false" />
        </Transition>

        <Transition name="fade">
            <SettingsModal v-if="showSettings" @close="showSettings = false" />
        </Transition>

        <Transition name="fade">
            <LessonDetailsModal v-if="selectedLesson" :lesson="selectedLesson" @close="selectedLesson = null" />
        </Transition>
    </div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch } from 'vue';
import { useRoute } from 'vue-router';
import { useMainStore } from '@/stores/main_store';
import type { Lesson } from '@/types';

import ScheduleSwiper from '@/views/ScheduleSwiper.vue';
import WeekScheduleView from '@/views/WeekScheduleView.vue';
import ResponsiveControls from '@/views/ResponsiveControls.vue';
import CalendarModal from '@/views/CalendarModal.vue';
import SettingsModal from '@/views/SettingsModal.vue';
import LessonDetailsModal from '@/views/LessonDetailsModal.vue';

const isMobile = ref(window.innerWidth < 768);
const showCalendar = ref(false);
const showSettings = ref(false);
const selectedLesson = ref<Lesson | null>(null);
const route = useRoute();
const mainStore = useMainStore();

// Текущая дата для Desktop View
const currentDate = ref(new Date().toISOString().substring(0, 10));

const openLessonDetails = (lesson: Lesson) => {
    selectedLesson.value = lesson;
};

// Открываем настройки, если юзер не залогинен
onMounted(() => {
    window.addEventListener('resize', () => {
        isMobile.value = window.innerWidth < 768;
    });
    if (!mainStore.isRegistered) {
        showSettings.value = true;
    }
});

watch(() => route.params.date, (newDate) => {
    if (newDate) currentDate.value = newDate as string;
}, { immediate: true });
</script>

<style scoped>
.schedule-view {
    display: flex;
    flex-direction: column;
    height: 100vh;
    background: var(--bg-color);
}

.content-area {
    flex: 1;
    overflow: hidden;
    position: relative;
}

/* Анимация модалок */
.fade-enter-active,
.fade-leave-active {
    transition: opacity 0.2s;
}

.fade-enter-from,
.fade-leave-to {
    opacity: 0;
}
</style>