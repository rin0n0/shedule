<template>
    <div class="lesson-card-content" :class="{ compact: isCompact }">
        <div class="info-col">
            <div v-if="lesson.subgroup && mainStore.userSubgroup === 0" class="subject">{{ lesson.subject }}
                ({{
                    lesson.subgroup }})</div>
            <div v-else class="subject">{{ lesson.subject }}</div>
            <div class="meta">
                <span class="teacher" v-if="lesson.teacher">{{ lesson.teacher }}</span>
            </div>
        </div>

        <div class="badges-col">
            <div v-if="lesson.is_replacement" class="badge replacement">🔥</div>
        </div>
    </div>
</template>

<script setup lang="ts">
import type { Lesson } from '@/types';
import { useMainStore } from '@/stores/main_store';

const mainStore = useMainStore();
defineProps<{
    lesson: Lesson,
    isCompact?: boolean
}>();
</script>

<style scoped>
.lesson-card-content {
    display: flex;
    flex-direction: column;
    /* Вертикальное расположение */
    justify-content: center;
    /* Центрирование по вертикали */
    gap: 6px;
    width: 100%;
    height: 100%;
    box-sizing: border-box;
    padding: 5px 0;
    /* Небольшие вертикальные отступы для баланса */
}

.info-col {
    overflow: hidden;
}

.subject {
    font-size: 15px;
    font-weight: 600;
    line-height: 1.3;
    color: var(--text-primary);
    /* Разрешаем перенос до 3 строк */
    display: -webkit-box;
    -webkit-line-clamp: 3;
    -webkit-box-orient: vertical;
    overflow: hidden;
}

.meta {
    font-size: 13px;
    color: var(--text-secondary);
}

.badges-col {
    display: flex;
    position: absolute;
    /* Позиционируем относительно ячейки */
    top: 15px;
    right: 15px;
}

.badge {
    width: 22px;
    height: 22px;
    border-radius: 6px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 11px;
    font-weight: bold;
}

.badge.replacement {
    background: #ff3b30;
    color: white;
}

/* Компактный вид для сплит-пар */
.compact {
    padding: 5px 10px;
    /* Отступы для сплит-ячеек */
}

.compact .subject {
    font-size: 14px;
    -webkit-line-clamp: 4;
    /* Позволяем больше строк в сплите */
}

.compact .meta {
    font-size: 12px;
}
</style>