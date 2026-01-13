<template>
    <div class="day-card-container">
        <div class="day-content">
            <header class="day-header">
                <h2 class="day-name">{{ schedule?.day_name || getDayName(date) }}</h2>
                <span class="day-date">{{ formatDateReadable(date) }}</span>
            </header>

            <!-- ЕДИНЫЙ МОНОЛИТНЫЙ БЛОК ДЛЯ ПАР -->
            <div class="lessons-block">
                <div v-if="!schedule || !schedule.lessons || schedule.lessons.length === 0" class="empty-state">

                </div>

                <!-- Используем ЧИСТЫЙ CSS GRID -->
                <div v-else class="lessons-grid">
                    <template v-for="(slot, index) in filledSchedule" :key="slot.num">

                        <!-- Ряд в гриде -->
                        <div class="grid-row">
                            <!-- Ячейка 1: Номер -->
                            <div class="time-cell">{{ slot.num }}</div>

                            <!-- Ячейка 2: Контент -->
                            <div class="content-cell">
                                <div v-if="slot.isEmpty" class="empty-text"></div>
                                <LessonCard v-else-if="slot.lessons.length === 1" :lesson="slot.lessons[0]!" />
                                <div v-else class="split-content">
                                    <LessonCard v-for="(lesson, i) in slot.lessons" :key="i" :lesson="lesson"
                                        is-compact />
                                </div>
                            </div>
                        </div>

                    </template>
                </div>
            </div>
        </div>
    </div>
</template>

<script setup lang="ts">
import { computed } from 'vue';
import type { DaySchedule, Lesson } from '@/types';
import LessonCard from './LessonCard.vue';
import { useMainStore } from '@/stores/main_store';

const mainStore = useMainStore();
const props = defineProps<{ schedule: DaySchedule | null, date: string }>();

interface ScheduleSlot {
    num: number;
    isEmpty: boolean;
    lessons: Lesson[];
}

// === УЛУЧШЕННАЯ ЛОГИКА ===

// 1. Сначала фильтруем уроки по подгруппе
const filteredLessons = computed(() => {
    if (!props.schedule?.lessons) return [];
    return props.schedule.lessons.filter(lesson => {
        if (mainStore.userSubgroup === 0) return true;
        return lesson.subgroup === 0 || lesson.subgroup === mainStore.userSubgroup;
    });
});

// 2. Проверяем, пустой ли день ПОСЛЕ фильтрации
const isEffectivelyEmpty = computed(() => {
    // Если расписания нет ИЛИ отфильтрованный список пуст
    return !props.schedule || filteredLessons.value.length === 0;
});

// 3. Заполняем сетку на основе отфильтрованных данных
const filledSchedule = computed<ScheduleSlot[]>(() => {
    if (isEffectivelyEmpty.value) return []; // Если день пуст, нечего и заполнять

    const groups: Record<number, Lesson[]> = {};
    let maxPairNum = 0;
    filteredLessons.value.forEach(lesson => {
        const num = lesson.lesson_number;
        if (num > maxPairNum) maxPairNum = num;
        if (!groups[num]) groups[num] = [];
        groups[num]!.push(lesson);
    });

    const totalSlots = Math.max(maxPairNum, 5);
    const result: ScheduleSlot[] = [];

    for (let i = 1; i <= totalSlots; i++) {
        if (groups[i] && groups[i]!.length > 0) {
            result.push({ num: i, isEmpty: false, lessons: groups[i]! });
        } else {
            result.push({ num: i, isEmpty: true, lessons: [] });
        }
    }
    return result;
});

const formatDateReadable = (dateStr: string) => new Date(dateStr).toLocaleDateString('ru-RU', { day: 'numeric', month: 'long' });
const getDayName = (dateStr: string) => {
    const days = ["Воскресенье", "Понедельник", "Вторник", "Среда", "Четверг", "Пятница", "Суббота"];
    return days[new Date(dateStr).getDay()];
};
</script>

<style scoped>
.day-card-container {
    width: 100%;
    height: 100%;
    display: flex;
    justify-content: center;
    align-items: flex-start;
    padding: 20px 15px;
    box-sizing: border-box;
    overflow-y: auto;
}

.day-content {
    width: 100%;
    max-width: 600px;
    display: flex;
    flex-direction: column;
}

.day-header {
    margin-bottom: 20px;
    text-align: center;
}

.day-name {
    font-size: 28px;
    font-weight: 800;
    color: var(--text-primary);
    margin: 0;
}

.day-date {
    font-size: 14px;
    color: var(--accent-color);
    font-weight: 600;
}

.lessons-block {
    background: var(--card-bg);
    backdrop-filter: blur(20px);
    -webkit-backdrop-filter: blur(20px);
    border: 1px solid var(--card-border);
    border-radius: 20px;
    overflow: hidden;
}

/* === НОВЫЙ CSS GRID === */
.lessons-grid {
    display: grid;
    /* Две колонки: узкая для времени, остальное - контент */
    grid-template-columns: 60px 1fr;
}

.grid-row {
    /* Говорим, что ряд занимает все 2 колонки */
    grid-column: 1 / -1;
    display: contents;
    /* "Растворяет" этот div, делая его детей прямыми элементами грида */
}

/* Стилизуем ячейки грида */
.time-cell,
.content-cell {
    padding: 15px 10px;
    display: flex;
    align-items: center;
    /* Выравнивание по центру по вертикали */
    border-bottom: 1px solid var(--row-border);
    min-height: 80px;
    /* Минимальная высота для мобилок */
}

/* Убираем рамку у последних ячеек */
.lessons-grid>.grid-row:last-of-type>.time-cell,
.lessons-grid>.grid-row:last-of-type>.content-cell {
    border-bottom: none;
}

.time-cell {
    justify-content: center;
    font-size: 18px;
    font-weight: 600;
    color: var(--text-tertiary);
    border-right: 1px solid var(--row-border);
    /* Сплошная линия */
}

.content-cell {
    padding-left: 15px;
}

.empty-text {
    color: var(--text-tertiary);
    font-style: italic;
}

.split-content {
    display: flex;
    width: 100%;
    gap: 10px;
}

.split-content>.lesson-card {
    flex: 1;
    min-width: 0;
}

@media (min-width: 768px) {
    .lessons-grid {
        grid-template-columns: 70px 1fr;
    }

    .time-cell,
    .content-cell {
        min-height: 105px;
        /* Больше места на ПК */
    }
}
</style>