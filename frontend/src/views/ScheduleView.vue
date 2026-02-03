<template>
    <div class="schedule-view">
        <!-- ПОКАЗЫВАЕМ ТОЛЬКО НА МОБИЛКЕ -->
        <ResponsiveControls 
            v-if="isMobile"
            @openCalendar="showCalendar = true" 
            @openSettings="showSettings = true"
        />

        <div class="content-area">
             <!-- Desktop: Grid (добавляем прослушку событий) -->
             <WeekScheduleView 
               v-if="!isMobile" 
               :center-date="currentDate"
               @lessonClick="openLessonDetails"
               @openCalendar="showCalendar = true"
               @openSettings="showSettings = true"
             />
             
             <!-- Mobile: Swiper -->
             <ScheduleSwiper 
               v-else 
               @lessonClick="openLessonDetails"
             />
        </div>

        <!-- ... модалки (CalendarModal, SettingsModal, LessonDetailsModal) без изменений ... -->
        <Transition name="fade">
            <CalendarModal 
                v-if="showCalendar" 
                :show="showCalendar" 
                @close="showCalendar = false" 
            />
        </Transition>

        <Transition name="fade">
            <SettingsModal 
                v-if="showSettings" 
                @close="showSettings = false" 
            />
        </Transition>
        
        <Transition name="fade">
            <LessonDetailsModal 
                v-if="selectedLesson && selectedLessonDate"
                :lesson="selectedLesson" 
                :date="selectedLessonDate" 
                @close="closeLessonDetails" 
            />
        </Transition>
    </div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch } from 'vue';
import { useRoute } from 'vue-router';
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
const route = useRoute();
const currentDate = ref(new Date().toISOString().substring(0, 10));

const selectedLesson = ref<Lesson | null>(null);
const selectedLessonDate = ref<string | null>(null);

const openLessonDetails = (payload: { lesson: Lesson, date: string }) => {
    selectedLesson.value = payload.lesson;
    selectedLessonDate.value = payload.date;
};

const closeLessonDetails = () => {
    selectedLesson.value = null;
    selectedLessonDate.value = null;
};

onMounted(() => {
    window.addEventListener('resize', () => {
        isMobile.value = window.innerWidth < 768;
    });
});

watch(() => route.params.date, (newDate) => {
    if (newDate) {
        currentDate.value = newDate as string;
    }
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

.fade-enter-active,
.fade-leave-active {
    transition: opacity 0.2s ease;
}

.fade-enter-from,
.fade-leave-to {
    opacity: 0;
}

@media (min-width:788px) {
    .content-area {
    overflow-y: auto;
}
}
</style>