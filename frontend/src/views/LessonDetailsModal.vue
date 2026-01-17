<template>
    <div class="modal-overlay" @click.self="$emit('close')">
        <div class="modal-card">
            <div class="modal-header">
                <span class="pair-num">{{ lesson.lesson_number }}-я пара</span>
                <button class="close-btn" @click="$emit('close')">✕</button>
            </div>

            <div class="info-content">
                <!-- Заголовок -->
                <h3 class="subject">{{ lesson.subject }}</h3>

                <div class="row">
                    <span class="icon">👨‍🏫</span>
                    <span class="value">{{ lesson.teacher || 'Преподаватель не указан' }}</span>
                </div>

                <div class="row" v-if="lesson.group">
                    <span class="icon">🎓</span>
                    <span class="value">Группа {{ lesson.group }}</span>
                </div>

                <!-- БЛОК ЗАМЕНЫ (Желтый) -->
                <div v-if="lesson.status === 'replacement'" class="status-block replacement">
                    <span class="status-icon">🔥</span>
                    <div class="status-text">
                        <strong>Замена</strong>
                        <p v-if="lesson.original_subject">
                            Вместо предмета: <span class="orig-subject">«{{ lesson.original_subject }}»</span>
                        </p>
                        <p v-else>В расписании произошли изменения.</p>
                    </div>
                </div>

                <!-- БЛОК ОТМЕНЫ (Красный) -->
                <div v-if="lesson.status === 'cancellation'" class="status-block cancelled">
                    <span class="status-icon">❌</span>
                    <div class="status-text">
                        <strong>Пара отменена</strong>
                        <!-- Если у нас есть инфа об оригинале, выводим её -->
                        <p v-if="lesson.original_subject">
                            Отменен предмет: <span class="orig-subject">«{{ lesson.original_subject }}»</span>
                        </p>
                        <p v-else>Занятия не будет.</p>
                    </div>
                </div>
            </div>
        </div>
    </div>
</template>
<script setup lang="ts">
import type { Lesson } from '@/types';

defineProps<{ lesson: Lesson }>();
defineEmits(['close']);
</script>

<style scoped>
.modal-overlay {
    position: fixed;
    inset: 0;
    background: var(--bg-color);
    backdrop-filter: blur(8px);
    z-index: 200;
    display: flex;
    justify-content: center;
    align-items: center;
    animation: fadeIn 0.2s;
}

.orig-subject {
    font-style: italic;
    opacity: 0.8;
    display: inline-block;
    margin-top: 2px;
}

.modal-card {
    background: var(--bg-color);
    width: 90%;
    max-width: 350px;
    border-radius: 20px;
    padding: 24px;
    border: 1px solid var(--border-color);
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
    color: #8e8e93;
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
    color: #aeaeb2;
}

.icon {
    font-size: 18px;
    width: 24px;
    text-align: center;
}

/* Статусные блоки */
.status-block {
    margin-top: 25px;
    padding: 15px;
    border-radius: 12px;
    display: flex;
    gap: 15px;
    align-items: flex-start;
}

.replacement {
    background: rgba(255, 159, 10, 0.15);
    /* Orange/Yellow alpha */
    border: 1px solid rgba(255, 159, 10, 0.3);
    color: #ff9f0a;
}

.cancelled {
    background: rgba(255, 69, 58, 0.15);
    /* Red alpha */
    border: 1px solid rgba(255, 69, 58, 0.3);
    color: #ff453a;
}

.status-text strong {
    display: block;
    margin-bottom: 4px;
    font-size: 15px;
}

.status-text p {
    margin: 0;
    font-size: 13px;
    opacity: 0.9;
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