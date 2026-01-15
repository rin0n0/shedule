<!-- src/views/LessonCard.vue -->
<template>
    <div class="lesson-card" :class="{ 'is-stream': isStream, 'is-cancelled': isCancelled }" @click="$emit('click')">
        <div class="card-content">
            <div class="header-row">
                <span class="subject-name">{{ lesson.subject }}</span>
                <!-- Иконка замены (огонек), если замена и не отмена -->
                <span v-if="lesson.is_replacement && !isCancelled" class="status-icon">🔥</span>
                <span v-if="isCancelled" class="status-icon">❌</span>
            </div>

            <div class="footer-row">
                <span v-if="!mainStore.userTeacher" class="teacher-name">{{ lesson.teacher }}</span>
                <span v-else class="teacher-name">{{ lesson.group }}</span>

                <div class="badges">
                    <span v-if="isStream" class="badge stream">Поток</span>
                    <span v-if="lesson.subgroup !== 0" class="badge sub">Подгр. {{ lesson.subgroup }}</span>
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

const isStream = computed(() => props.lesson.subgroup === 0);
const isCancelled = computed(() => props.lesson.subject.toLowerCase().includes('отмена'));

defineEmits(['click']);
</script>

<style scoped>
.lesson-card {
    background: rgba(255, 255, 255, 0.05);
    /* Очень легкий фон */
    border-radius: 12px;
    padding: 10px;
    height: 100%;
    transition: background 0.2s, transform 0.1s;
    cursor: pointer;
    border: 1px solid rgba(255, 255, 255, 0.05);
    display: flex;
    flex-direction: column;
}

.lesson-card:active {
    transform: scale(0.98);
    background: rgba(255, 255, 255, 0.1);
}

/* Стиль для отмены: серый и полупрозрачный */
.lesson-card.is-cancelled {
    opacity: 0.6;
    background: rgba(255, 59, 48, 0.1);
    /* Легкий красный оттенок */
}

/* Стиль для потока: легкий акцент слева */
.lesson-card.is-stream {
    border-left: 3px solid var(--accent-color);
    background: linear-gradient(90deg, rgba(10, 132, 255, 0.05) 0%, transparent 50%);
}

.card-content {
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    height: 100%;
    gap: 4px;
}

.header-row {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    gap: 5px;
}

.subject-name {
    font-size: 13px;
    font-weight: 600;
    line-height: 1.3;
    color: var(--text-primary);
    display: -webkit-box;
    -webkit-line-clamp: 3;
    -webkit-box-orient: vertical;
    overflow: hidden;
}

.status-icon {
    font-size: 14px;
}

.footer-row {
    display: flex;
    justify-content: space-between;
    align-items: flex-end;
    margin-top: auto;
}

.teacher-name {
    font-size: 11px;
    color: var(--text-secondary);
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
    max-width: 60%;
}

.badges {
    display: flex;
    gap: 4px;
}

.badge {
    font-size: 9px;
    padding: 2px 5px;
    border-radius: 4px;
    font-weight: 600;
}

.badge.stream {
    background: rgba(10, 132, 255, 0.2);
    color: var(--accent-color);
}

.badge.sub {
    background: rgba(255, 255, 255, 0.1);
    color: var(--text-secondary);
}
</style>