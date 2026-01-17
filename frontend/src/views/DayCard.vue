<template>
    <div class="day-card-container">
        <div class="day-content">
            <header class="day-header">
                <h2 class="day-name">{{ schedule?.day_name || getDayName(date) }}</h2>
                <span class="day-date">{{ formatDateReadable(date) }}</span>
            </header>

            <div class="lessons-block">
                <div v-if="!schedule || !schedule.lessons || schedule.lessons.length === 0" class="empty-state">
                    <!-- Можно добавить заглушку "Пар нет" -->
                </div>

                <div v-else class="lessons-grid">
                    <template v-for="(slot, index) in filledSchedule" :key="slot.num">

                        <div class="grid-row">
                            <!-- Время/Номер -->
                            <div class="time-cell">{{ slot.num }}</div>

                            <!-- Контент -->
                            <div class="content-cell">
                                <div v-if="slot.isEmpty" class="empty-text"></div>

                                <!-- ОДНА ПАРА -->
                                <LessonCard v-if="slot.lessons.length === 1" :lesson="slot.lessons[0]!"
                                    :date="props.date" @lessonClick="(payload) => $emit('lessonClick', payload)" />
                                <div v-else class="split-content">
                                    <LessonCard v-for="(lesson, i) in slot.lessons" :key="i" :lesson="lesson"
                                        :date="props.date" is-compact
                                        @lessonClick="(payload) => $emit('lessonClick', payload)" />
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

// === ВАЖНО: Объявляем, что этот компонент может испускать событие ===
defineEmits(['lessonClick']);

interface ScheduleSlot {
    num: number;
    isEmpty: boolean;
    lessons: Lesson[];
}

const filteredLessons = computed(() => {
    if (!props.schedule?.lessons) return [];
    return props.schedule.lessons.filter(lesson => {
        if (mainStore.userSubgroup === 0) return true;
        return lesson.subgroup === 0 || lesson.subgroup === mainStore.userSubgroup;
    });
});

const isEffectivelyEmpty = computed(() => {
    return !props.schedule || filteredLessons.value.length === 0;
});

const filledSchedule = computed<ScheduleSlot[]>(() => {
    if (isEffectivelyEmpty.value) return [];

    const groups: Record<number, Lesson[]> = {};
    let maxPairNum = 0;
    filteredLessons.value.forEach(lesson => {
        const num = lesson.lesson_number;
        if (num > maxPairNum) maxPairNum = num;
        if (!groups[num]) groups[num] = [];
        groups[num]!.push(lesson);
    });

    // Ограничим 5 парами, как договорились, или динамически
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
/* Стили оставляем те же, что и были в предыдущих шагах */
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
    /* Используем переменную темы */
    backdrop-filter: blur(20px);
    -webkit-backdrop-filter: blur(20px);
    border: 1px solid var(--card-border);
    border-radius: 20px;
    overflow: hidden;
}

.lessons-grid {
    display: grid;
    grid-template-columns: 50px 1fr;
    /* Чуть уже колонка времени для мобилок */
}

.grid-row {
    grid-column: 1 / -1;
    display: contents;
}

.time-cell,
.content-cell {
    padding: 10px;
    display: flex;
    align-items: center;
    border-bottom: 1px solid var(--row-border);
    min-height: 80px;
}

.lessons-grid>.grid-row:last-of-type>.time-cell,
.lessons-grid>.grid-row:last-of-type>.content-cell {
    border-bottom: none;
}

.time-cell {
    justify-content: center;
    font-size: 16px;
    font-weight: 600;
    color: var(--text-tertiary);
    border-right: 1px solid var(--row-border);
}

.content-cell {
    padding-left: 10px;
}

.split-content {
    display: flex;
    width: 100%;
    gap: 8px;
}

.split-content>.lesson-card {
    flex: 1;
    min-width: 0;
}
</style>