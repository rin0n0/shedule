<template>
  <div class="modal-overlay" @click.self="$emit('close')">
    <div class="modal-card">
       <div class="modal-header">
           <span class="pair-num">{{ lesson.lesson_number }}-я пара</span>
           <button class="close-btn" @click="$emit('close')">✕</button>
       </div>
       
       <div class="info-content">
           <h3 class="subject">{{ lesson.subject }}</h3>
           
           <div class="meta-rows">
               <div class="row">
                   <span class="icon">👨‍🏫</span>
                   <span class="value">{{ lesson.teacher || 'Нет данных' }}</span>
               </div>
               <div class="row" v-if="lesson.group">
                   <span class="icon">🎓</span>
                   <span class="value">Группа {{ lesson.group }}</span>
               </div>
           </div>

           <!-- ЗАМЕТКИ -->
           <div class="notes-section">
               <label>Заметки / ДЗ</label>
               <textarea 
                   v-model="noteText" 
                   placeholder="Напиши что-нибудь важное..."
                   @input="handleInput"
               ></textarea>
           </div>

           <!-- БЛОК ЗАМЕНЫ -->
           <div v-if="lesson.status === 'replacement'" class="status-block replacement">
               <span class="status-icon">🔥</span>
               <div class="status-text">
                   <strong>Замена</strong>
                   
                   <!-- ЛОГИКА ОТОБРАЖЕНИЯ ИЗМЕНЕНИЙ -->
                   
                   <!-- 1. Если изменился ПРЕДМЕТ -->
                   <p v-if="lesson.original_subject && lesson.subject !== lesson.original_subject">
                       Вместо предмета <span class="orig-subject">{{ lesson.original_subject }}</span>
                   </p>
                   
                   <!-- 2. Если предмет тот же, но изменился ПРЕПОДАВАТЕЛЬ -->
                   <p v-else-if="lesson.original_teacher && lesson.teacher !== lesson.original_teacher">
                       Вместо преподавателя <span class="orig-subject">{{ lesson.original_teacher }}</span>
                   </p>
                   
                   <p v-else>В расписании произошли изменения.</p>
               </div>
           </div>

           <!-- БЛОК ОТМЕНЫ -->
           <div v-if="lesson.status === 'cancellation'" class="status-block cancelled">
               <span class="status-icon">❌</span>
               <div class="status-text">
                   <strong>Пара отменена</strong>
                   <!-- Если была инфа о предмете, пишем -->
                   <p v-if="lesson.original_subject">
                       Отменен предмет <span class="orig-subject">{{ lesson.original_subject }}</span>
                   </p>
                   <p v-else>Занятия не будет.</p>
               </div>
           </div>
       </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import type { Lesson } from '@/types';
import { useMainStore } from '@/stores/main_store';

const props = defineProps<{ lesson: Lesson, date: string }>();
const emit = defineEmits(['close']);
const mainStore = useMainStore();

const noteKey = `${props.date}_${props.lesson.lesson_number}_${props.lesson.subject}`;
const noteText = ref('');

onMounted(() => {
    noteText.value = mainStore.notes[noteKey] || '';
});

const handleInput = () => {
    mainStore.saveNote(noteKey, noteText.value);
};
</script>

<style scoped>
.modal-overlay {
    position: fixed;
    inset: 0;
    background: rgba(0,0,0,0.6);
    backdrop-filter: blur(8px);
    z-index: 200;
    display: flex;
    justify-content: center;
    align-items: center;
    animation: fadeIn 0.2s;
}

.modal-card {
    background: var(--card-bg);
    width: 90%;
    max-width: 350px;
    border-radius: 20px;
    padding: 24px;
    border: 1px solid var(--card-border);
    box-shadow: 0 20px 50px rgba(0,0,0,0.5);
    animation: scaleUp 0.2s;
}

.modal-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 20px;
}
.pair-num { font-size: 12px; text-transform: uppercase; color: var(--text-tertiary); font-weight: 700; letter-spacing: 1px; }
.close-btn { background: none; border: none; color: var(--text-secondary); font-size: 20px; cursor: pointer; }

.subject {
    font-size: 18px;
    line-height: 1.3;
    margin-bottom: 20px;
    color: var(--text-primary);
}

.meta-rows { margin-bottom: 20px; }
.row {
    display: flex;
    align-items: center;
    gap: 12px;
    margin-bottom: 10px;
    font-size: 15px;
    color: var(--text-secondary);
}
.icon { font-size: 18px; width: 24px; text-align: center; }

/* Заметки */
.notes-section {
    margin-bottom: 20px;
    display: flex;
    flex-direction: column;
    gap: 8px;
}
.notes-section label {
    font-size: 11px;
    text-transform: uppercase;
    font-weight: 700;
    color: var(--accent-color);
    letter-spacing: 0.5px;
    padding-left: 4px;
}
textarea {
    width: 100%;
    min-height: 80px;
    background: rgba(255, 255, 255, 0.03);
    border: 1px solid var(--card-border);
    border-radius: 12px;
    padding: 10px;
    color: var(--text-primary);
    font-family: inherit;
    font-size: 14px;
    line-height: 1.4;
    resize: none;
    outline: none;
    box-sizing: border-box; 
    transition: all 0.2s;
}
textarea:focus {
    background: rgba(255, 255, 255, 0.05);
    border-color: var(--accent-color);
}

/* Статусы */
.status-block {
    padding: 15px;
    border-radius: 12px;
    display: flex;
    gap: 15px;
    align-items: flex-start;
}
.replacement {
    background: rgba(255, 159, 10, 0.15);
    border: 1px solid rgba(255, 159, 10, 0.3);
    color: #ff9f0a;
}
.cancelled {
    background: rgba(255, 69, 58, 0.15);
    border: 1px solid rgba(255, 69, 58, 0.3);
    color: #ff453a;
}
.status-text strong { display: block; margin-bottom: 4px; font-size: 18px; }
.status-text p { margin: 0; font-size: 15px; opacity: 0.9; }
.orig-subject { font-style: bold; font-weight: 600; opacity: 1; }

@keyframes fadeIn { from { opacity: 0; } to { opacity: 1; } }
@keyframes scaleUp { from { transform: scale(0.95); opacity: 0; } to { transform: scale(1); opacity: 1; } }
</style>