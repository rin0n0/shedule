<!-- src/views/WeekScheduleView.vue -->
<script setup lang="ts">
/* ...imports... */
import { computed, watch } from 'vue';
import { useRouter } from 'vue-router';
import { useMainStore } from '@/stores/main_store';
import LessonCard from '@/views/LessonCard.vue';
import type { Lesson } from '@/types';

const props = defineProps<{ centerDate: string }>();
const emit = defineEmits(['lessonClick']);
const mainStore = useMainStore();
const router = useRouter();

// ... (weekDays calculation тот же) ...
const weekDays = computed(() => {
    const current = new Date(props.centerDate);
    const day = current.getDay() || 7;
    const monday = new Date(current);
    monday.setDate(current.getDate() - (day - 1));

    const days = [];
    for (let i = 0; i < 6; i++) {
        const d = new Date(monday);
        d.setDate(monday.getDate() + i);
        const dateStr = d.toISOString().substring(0, 10);
        days.push({
            date: dateStr,
            name: ['ПН', 'ВТ', 'СР', 'ЧТ', 'ПТ', 'СБ'][i],
            displayDate: d.toLocaleDateString('ru', { day: 'numeric', month: 'short' }),
            isToday: dateStr === new Date().toISOString().substring(0, 10)
        });
    }
    return days;
});

const weekDateRange = computed(() => {
    if (!weekDays.value.length) return '';
    const start = weekDays.value[0]!.displayDate;
    const end = weekDays.value[5]!.displayDate;
    return `${start} — ${end}`;
});

const changeWeek = (days: number) => {
    const current = new Date(props.centerDate);
    current.setDate(current.getDate() + days);
    router.push({ params: { date: current.toISOString().substring(0, 10) } });
};

const getLesson = (date: string, num: number): Lesson | undefined => {
    const schedule = mainStore.getDaySchedule(date);
    if (!schedule) return undefined;

    // Улучшенный поиск пары
    return schedule.lessons.find(l =>
        l.lesson_number === num &&
        (mainStore.userSubgroup === 0 || l.subgroup === 0 || l.subgroup === mainStore.userSubgroup)
    );
};

// === ВАЖНО: Обновляем Store при смене недели ===
watch(() => props.centerDate, (newDate) => {
    weekDays.value.forEach(d => mainStore.ensureDayLoaded(d.date));
    mainStore.setViewedDate(newDate); // Сообщаем стору, что мы смотрим эту дату
}, { immediate: true });
</script>

<!-- Template оставляем тот же, что в прошлом ответе, он был ок -->
<template>
    <div class="week-view-container">
        <div class="week-nav">
            <button class="nav-arrow" @click="changeWeek(-7)">←</button>
            <span class="week-label">{{ weekDateRange }}</span>
            <button class="nav-arrow" @click="changeWeek(7)">→</button>
        </div>

        <div class="grid-header">
            <div v-for="day in weekDays" :key="day.date" class="header-cell" :class="{ 'is-today': day.isToday }">
                <span class="weekday">{{ day.name }}</span>
                <span class="date">{{ day.displayDate }}</span>
            </div>
        </div>

        <div class="grid-body">
            <div v-for="day in weekDays" :key="day.date" class="day-column">
                <!-- Фиксируем 5 пар -->
                <div v-for="slot in 5" :key="slot" class="slot-cell">
                    <div class="slot-num">{{ slot }}</div>
                    <div class="lesson-content">
                        <template v-if="getLesson(day.date, slot)">
                            <LessonCard :lesson="getLesson(day.date, slot)!"
                                @click="$emit('lessonClick', getLesson(day.date, slot)!)" />
                        </template>
                    </div>
                </div>
            </div>
        </div>
    </div>
</template>

<style scoped>
/* CSS из прошлого ответа, можно оставить */
.week-view-container {
    height: 100%;
    overflow-y: auto;
    padding: 20px;
    display: flex;
    flex-direction: column;
}

.week-nav {
    display: flex;
    justify-content: center;
    align-items: center;
    margin-bottom: 20px;
    gap: 20px;
}

.nav-arrow {
    background: rgba(255, 255, 255, 0.1);
    border: none;
    color: var(--text-primary);
    width: 32px;
    height: 32px;
    border-radius: 50%;
    cursor: pointer;
}

.week-label {
    font-weight: 600;
    color: var(--text-primary);
}

.grid-header {
    display: grid;
    grid-template-columns: repeat(6, 1fr);
    gap: 10px;
    margin-bottom: 10px;
}

.header-cell {
    background: rgba(255, 255, 255, 0.03);
    padding: 10px;
    border-radius: 12px;
    text-align: center;
}

.header-cell.is-today {
    background: rgba(10, 132, 255, 0.1);
    color: var(--accent-color);
}

.weekday {
    font-weight: 900;
    display: block;
    font-size: 14px;
    margin-bottom: 4px;
}

.date {
    font-size: 12px;
    opacity: 0.6;
}

.grid-body {
    display: grid;
    grid-template-columns: repeat(6, 1fr);
    gap: 10px;
    flex: 1;
}

.day-column {
    display: flex;
    flex-direction: column;
    gap: 10px;
}

.slot-cell {
    background: var(--card-bg);
    border: 1px solid var(--card-border);
    border-radius: 12px;
    height: 110px;
    /* Фиксированная высота */
    padding: 5px;
    position: relative;
    overflow: hidden;
    /* Гарантия того, что не вылезет */
}

.slot-num {
    position: absolute;
    top: 5px;
    left: 8px;
    font-size: 10px;
    opacity: 0.2;
    font-weight: bold;
}

.lesson-content {
    height: 100%;
    padding-left: 15px;
}
</style>