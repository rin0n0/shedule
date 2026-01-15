<!-- src/views/LessonDetailsModal.vue -->
<template>
    <div class="modal-overlay" @click.self="$emit('close')">
        <div class="modal-card">
            <div class="modal-header">
                <span class="pair-num">{{ lesson.lesson_number }}-я пара</span>
                <button class="close-btn" @click="$emit('close')">✕</button>
            </div>

            <div class="info-content">
                <h3 class="subject">{{ lesson.subject }}</h3>

                <div class="row">
                    <span class="icon">👨‍🏫</span>
                    <span class="value">{{ lesson.teacher || 'Преподаватель не указан' }}</span>
                </div>

                <div class="row" v-if="lesson.group">
                    <span class="icon">🎓</span>
                    <span class="value">Группа {{ lesson.group }}</span>
                </div>

                <!-- Статусы -->
                <div v-if="lesson.is_replacement" class="status-block replacement">
                    <span class="status-icon">🔥</span>
                    <div class="status-text">
                        <strong>Замена</strong>
                        <p>В расписании произошли изменения.</p>
                    </div>
                </div>

                <div v-if="isCancelled" class="status-block cancelled">
                    <span class="status-icon">❌</span>
                    <div class="status-text">
                        <strong>Пара отменена</strong>
                        <p>Занятия не будет.</p>
                    </div>
                </div>
            </div>
        </div>
    </div>
</template>

<script setup lang="ts">
import { computed } from 'vue';
import type { Lesson } from '@/types';

const props = defineProps<{ lesson: Lesson }>();
defineEmits(['close']);

const isCancelled = computed(() => props.lesson.subject.toLowerCase().includes('отмена'));
</script>

<style scoped>
.modal-overlay {
    position: fixed;
    inset: 0;
    background: rgba(0, 0, 0, 0.5);
    backdrop-filter: blur(5px);
    z-index: 200;
    display: flex;
    justify-content: center;
    align-items: center;
    animation: fadeIn 0.2s;
}

.modal-card {
    background: #1c1c1e;
    /* Темный фон iOS */
    width: 90%;
    max-width: 350px;
    border-radius: 20px;
    padding: 24px;
    border: 1px solid rgba(255, 255, 255, 0.1);
    box-shadow: 0 20px 50px rgba(0, 0, 0, 0.5);
    animation: scaleUp 0.2s;
}

.modal-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 20px;
}

.pair-num {
    font-size: 12px;
    text-transform: uppercase;
    color: var(--text-secondary);
    font-weight: 700;
    letter-spacing: 1px;
}

.close-btn {
    background: none;
    border: none;
    color: var(--text-secondary);
    font-size: 20px;
    cursor: pointer;
}

.subject {
    font-size: 18px;
    line-height: 1.3;
    margin-bottom: 20px;
    color: var(--text-primary);
}

.row {
    display: flex;
    align-items: center;
    gap: 12px;
    margin-bottom: 12px;
    font-size: 15px;
    color: var(--text-secondary);
}

.icon {
    font-size: 18px;
}

/* Статусные блоки */
.status-block {
    margin-top: 20px;
    padding: 12px;
    border-radius: 12px;
    display: flex;
    gap: 12px;
    align-items: flex-start;
}

.replacement {
    background: rgba(255, 149, 0, 0.15);
    color: #ff9f0a;
}

.cancelled {
    background: rgba(255, 59, 48, 0.15);
    color: #ff453a;
}

.status-text strong {
    display: block;
    margin-bottom: 2px;
    font-size: 14px;
}

.status-text p {
    margin: 0;
    font-size: 12px;
    opacity: 0.8;
}

@keyframes fadeIn {
    from {
        opacity: 0;
    }

    to {
        opacity: 1;
    }
}

@keyframes scaleUp {
    from {
        transform: scale(0.95);
        opacity: 0;
    }

    to {
        transform: scale(1);
        opacity: 1;
    }
}
</style>