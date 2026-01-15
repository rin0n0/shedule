<template>
    <div class="schedule-view">
        <ScheduleSwiper />

        <!-- Передаем события из футера в методы управления модалками -->
        <AppFooter @openCalendar="showCalendar = true" @openSettings="showSettings = true" />

        <!-- Модалки -->
        <Transition name="modal">
            <CalendarModal v-if="showCalendar" @close="showCalendar = false" />
        </Transition>

        <Transition name="modal">
            <SettingsModal v-if="showSettings" @close="showSettings = false" />
        </Transition>
    </div>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import ScheduleSwiper from '@/views/ScheduleSwiper.vue';
import AppFooter from '@/views/AppFooter.vue';
// Импортируем новые компоненты
import CalendarModal from '@/views/CalendarModal.vue';
import SettingsModal from '@/views/SettingsModal.vue';

const showCalendar = ref(false);
const showSettings = ref(false);
</script>

<style scoped>
.schedule-view {
    flex-grow: 1;
    display: flex;
    flex-direction: column;
    height: 100%;
    overflow: hidden;
}

/* Анимация для модалок (простое появление) */
.modal-enter-active,
.modal-leave-active {
    transition: opacity 0.2s ease;
}

.modal-enter-from,
.modal-leave-to {
    opacity: 0;
}
</style>