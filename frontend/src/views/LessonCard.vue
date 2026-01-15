<!-- src/views/LessonCard.vue -->
<template>
    <div class="lesson-card" :class="{ 'is-stream': lesson.is_stream, 'is-cancelled': isCancelled }">
        <div class="card-content">
            <div class="header-row">
                <!-- Ограничение строк для названия предмета -->
                <span class="subject-name" :title="lesson.subject">{{ lesson.subject }}</span>

                <!-- Новые индикаторы (кружки) -->
                <div class="indicators">
                    <span v-if="lesson.status === 'cancellation'" class="status-dot red"></span>
                    <span v-if="lesson.status === 'replacement'" class="status-dot yellow"></span>
                </div>
            </div>

            <div class="footer-row">
                <span v-if="!mainStore.userTeacher" class="teacher-name">{{ lesson.teacher }}</span>
                <span v-else class="teacher-name">{{ lesson.group }}</span>

                <div class="badges">
                    <span v-if="lesson.is_stream" class="badge stream">Поток</span>
                    <!-- Если 2 подгруппы одновременно, карточка сжата, значок подгруппы минималистичен -->
                    <span v-if="lesson.subgroup !== 0" class="badge sub">{{ lesson.subgroup }}</span>
                </div>
            </div>
        </div>
    </div>
</template>

<script setup lang="ts">
import { computed } from 'vue';
import type { Lesson } from '@/types';
import { useMainStore } from '@/stores/main_store';

const props = defineProps<{ lesson: Lesson }>();
const mainStore = useMainStore();

// Отмена теперь определяется по статусу с бэка
const isCancelled = computed(() => props.lesson.status === 'cancellation');
</script>

<style scoped>
.lesson-card {
    border-radius: 8px;
    padding: 8px;
    height: 100%;
    width: 100%;
    cursor: pointer;
    border: 1px solid transparent;
    display: flex;
    flex-direction: column;
    box-sizing: border-box;
    overflow: hidden;
    /* Обрезаем всё лишнее */
}

.lesson-card:active {
    background: rgba(255, 255, 255, 0.1);
}

.lesson-card.is-cancelled {
    background: rgba(255, 59, 48, 0.08);
}

/* Поток: тонкая полоска слева */
.lesson-card.is-stream {
    border-left: 3px solid var(--accent-color);
}

.card-content {
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    height: 100%;
    gap: 2px;
}

.header-row {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    gap: 4px;
}

.subject-name {
    font-size: 12px;
    font-weight: 600;
    line-height: 1.2;
    color: var(--text-primary);
    /* ГАРАНТИЯ ВМЕСТИМОСТИ: макс 4 строки, потом ... */
    display: -webkit-box;
    -webkit-line-clamp: 4;
    -webkit-box-orient: vertical;
    overflow: hidden;
    word-break: break-word;
}

.indicators {
    display: flex;
    flex-direction: column;
    gap: 4px;
    flex-shrink: 0;
    /* Чтобы кружки не сжимались */
}

.status-dot {
    width: 8px;
    height: 8px;
    border-radius: 50%;
    display: block;
}

.status-dot.red {
    background-color: #ff453a;
    box-shadow: 0 0 4px rgba(255, 69, 58, 0.5);
}

.status-dot.yellow {
    background-color: #ff9f0a;
    box-shadow: 0 0 4px rgba(255, 159, 10, 0.5);
}

.footer-row {
    display: flex;
    justify-content: space-between;
    align-items: flex-end;
    margin-top: auto;
    /* Прижимаем к низу */
}

.teacher-name {
    font-size: 10px;
    color: var(--text-secondary);
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
    max-width: 65%;
}

.badges {
    display: flex;
    gap: 3px;
    align-items: center;
}

.badge {
    font-size: 9px;
    padding: 1px 4px;
    border-radius: 3px;
    font-weight: 600;
}

.badge.stream {
    background: rgba(10, 132, 255, 0.15);
    color: var(--accent-color);
}

.badge.sub {
    background: rgba(255, 255, 255, 0.1);
    color: var(--text-secondary);
}
</style>