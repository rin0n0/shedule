<template>
    <div class="week-grid-container">
        <div class="week-header">
            <h2>{{ weekLabel }}</h2>
        </div>

        <div class="grid">
            <!-- Рендерим колонки дней -->
            <div v-for="date in weekDates" :key="date" class="day-column" :class="{ 'is-today': isToday(date) }">
                <!-- Используем уже существующий DayCard, но немного стилизуем -->
                <DayCard :schedule="scheduleMap[date] || null" :date="date" class="compact-day-card" />
            </div>
        </div>
    </div>
</template>

<script setup lang="ts">
import { computed } from 'vue';
import type { DaySchedule } from '@/types';
import DayCard from './DayCard.vue';

const props = defineProps<{
    weekStart: string, // Дата понедельника
    scheduleMap: Record<string, DaySchedule> // Словарь { дата: расписание }
}>();

// Генерируем массив дат недели (ПН-СБ)
const weekDates = computed(() => {
    const dates = [];
    const start = new Date(props.weekStart);
    for (let i = 0; i < 6; i++) {
        const d = new Date(start);
        d.setDate(d.getDate() + i);
        dates.push(d.toISOString().substring(0, 10));
    }
    return dates;
});

const weekLabel = computed(() => {
    const start = new Date(props.weekStart);
    const end = new Date(start);
    end.setDate(end.getDate() + 5);

    const opts: Intl.DateTimeFormatOptions = { day: 'numeric', month: 'long' };
    return `${start.toLocaleDateString('ru', opts)} — ${end.toLocaleDateString('ru', opts)}`;
});

const isToday = (dateStr: string) => {
    return dateStr === new Date().toISOString().substring(0, 10);
};
</script>

<style scoped>
.week-grid-container {
    width: 100%;
    height: 100%;
    display: flex;
    flex-direction: column;
    padding: 20px;
    box-sizing: border-box;
}

.week-header {
    text-align: center;
}

.week-header h2 {
    font-size: 24px;
    color: var(--text-secondary);
}

.grid {
    display: grid;
    grid-template-columns: repeat(6, 1fr);
    /* 6 колонок */
    gap: 15px;
    height: 100%;
    overflow: hidden;
}

.day-column {
    background: rgba(255, 255, 255, 0.03);
    border-radius: 16px;
    overflow: hidden;
    height: 100%;
    border: 1px solid transparent;
}

.day-column.is-today {
    background: rgba(59, 44, 192, 0.05);
    border-color: rgba(69, 72, 233, 0.3);
}

/* Хак: прокидываем стили внутрь DayCard, чтобы он влез в колонку */
:deep(.day-card-container) {
    padding: 10px;
}

:deep(.day-header) {
    margin-bottom: 10px;
}

:deep(.day-name) {
    font-size: 18px;
    /* Уменьшаем заголовок дня */
}

:deep(.day-date) {
    font-size: 12px;
}

:deep(.lesson-row) {
    height: 80px;
    /* Чуть компактнее строки */
}
</style>