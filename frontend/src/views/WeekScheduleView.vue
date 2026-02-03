<!-- src/views/WeekScheduleView.vue -->
<script setup lang="ts">
/* ...imports... */
import { computed, watch } from 'vue';
import { useRouter } from 'vue-router';
import { useMainStore } from '@/stores/main_store';
import LessonCard from '@/views/LessonCard.vue';
import type { Lesson } from '@/types';

const props = defineProps<{ centerDate: string }>();
const emit = defineEmits(['lessonClick', 'openCalendar', 'openSettings']);
const mainStore = useMainStore();
const router = useRouter();

const getLessonsForSlot = (date: string, num: number): Lesson[] => {
    const schedule = mainStore.getDaySchedule(date);
    if (!schedule) return [];

    return schedule.lessons.filter(l =>
        l.lesson_number === num &&
        (mainStore.userSubgroup === 0 || l.subgroup === 0 || l.subgroup === mainStore.userSubgroup)
    );
};

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
    <div class="week-nav-sticky">
        <button class="nav-btn" @click="$emit('openCalendar')">
            📅 <span class="label">Дата</span>
        </button>
            <button class="nav-arrow" @click="changeWeek(-7)">←</button>
            <div v-for="day in weekDays" :key="day.date" class="header-cell" :class="{ 'is-today': day.isToday }">
                <span class="weekday">{{ day.name }}</span>
                <span class="date">{{ day.displayDate }}</span>
            </div>
            <button class="nav-arrow" @click="changeWeek(7)">→</button>
            <button class="nav-btn" @click="$emit('openSettings')">
            ⚙️ <span class="label">Настройки</span>
        </button>
        </div>
    <div class="week-view-container">
        <div class="grid-body">
            <div v-for="day in weekDays" :key="day.date" class="day-column">
                <div v-for="slot in 5" :key="slot" class="slot-cell">
                    <div class="slot-num">{{ slot }}</div>

                    <div class="lesson-content-wrapper">
                        <!-- Итерируемся по массиву найденных пар -->
                        <template v-if="getLessonsForSlot(day.date, slot).length > 0">
                            <div class="lessons-flex">
                                <!-- Измени @click на @lessonClick и передай payload -->
                                <LessonCard v-for="(lesson, idx) in getLessonsForSlot(day.date, slot)" :key="idx"
                                    :lesson="lesson" :date="day.date"
                                    @lessonClick="(payload) => $emit('lessonClick', payload)"
                                    class="desktop-lesson-card" />
                            </div>
                        </template>
                    </div>
                </div>
            </div>
        </div>
    </div>
</template>

<!-- ... template и script те же ... -->

<style scoped>
.week-view-container {
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

lesson-content-wrapper {
    width: 100%;
    height: 100%;
}

.lessons-flex {
    display: flex;
    gap: 4px;
    /* Маленький отступ между подгруппами */
    height: 100%;
    width: 100%;
    padding: 2px;
    box-sizing: border-box;
}

/* Если пары две, они делят место 50/50 */
.is-split {
    flex: 1;
    min-width: 0;
}

:deep(.lesson-card) {
    border-radius: 10px !important;
    height: 100%;
}

.week-nav-sticky {
    /* Прилипание */
    position: sticky;
    top: 0;
    z-index: 50;

    /* Стили стекла */
    background: var(--glass-bg);
    backdrop-filter: blur(15px);
    -webkit-backdrop-filter: blur(15px);

    /* Позиционирование и отступы */
    display: flex;
    justify-content: center;
    align-items: center;
    gap: 20px;
    padding: 15px 0;
    margin-bottom: 20px;
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
    gap: 8px;
    margin-bottom: 8px;
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
    gap: 8px;
    flex: 1;
}

.day-column {
    display: flex;
    flex-direction: column;
    gap: 0;
    border: 1px solid var(--card-border);
    border-radius: 12px;
    overflow: hidden;
    background: var(--card-bg);
    /* Общий фон дня */
}

.slot-cell {
    background: transparent;
    border: none;
    /* Добавляем линию-разделитель снизу */
    border-bottom: 1px solid var(--row-border);
    height: 130px;
    position: relative;
    padding: 0;
}

/* У последней ячейки убираем линию */
/* .slot-cell:last-child {
    border-bottom: none;
} */

.slot-num {
    position: absolute;
    user-select: none;
    bottom: 6px;
    right: 8px;
    font-size: 14px;
    opacity: 0.2;
    font-weight: bold;
    z-index: 10;
}

.lesson-content {
    width: 100%;
    height: 100%;
}

.row:last-child {
    border-bottom: none;
}

:deep(.desktop-lesson-card:not(:last-child)) {
    border-right: 1px solid var(--row-border) !important;
}

:deep(.lesson-card) {
    border-radius: 0 !important;
    /* Внутри колонки без скруглений */
    border: none !important;
    height: 100%;
    /* Если это замена/отмена, фон будет переопределен в LessonCard */
}

/* При наведении подсвечиваем ячейку */
.slot-cell:hover {
    background-color: rgba(255, 255, 255, 0.02);
}
.nav-btn {
    background: var(--row-border);
    border: 1px solid transparent;
    color: var(--text-primary);
    padding: 6px 16px;
    border-radius: 8px;
    font-size: 18px;
    cursor: pointer;
    font-weight: 500;
    transition: all 0.2s;
}

.nav-btn:hover {
    opacity: 1;
    transform: scale(0.95);
}

</style>