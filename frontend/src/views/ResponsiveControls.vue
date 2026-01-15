<!-- src/views/ResponsiveControls.vue -->
<template>
    <div class="controls-wrapper" :class="{ 'is-mobile': isMobile }">

        <!-- HEADER: Кнопка-триггер -->
        <div class="status-bar" @click="$emit('openSettings')">
            <div class="info">
                <!-- Показываем "Группу" или "Поиск...", если не выбрана -->
                <h2 class="main-title">{{ mainStore.currentModeTitle || 'Настроить расписание' }}</h2>
                <span class="week-info" v-if="weekInfo">{{ weekInfo }}</span>
            </div>
            <div class="actions">
                <button class="icon-btn" @click.stop="$emit('openCalendar')">📅</button>
                <!-- Кнопка настроек -->
                <button class="icon-btn setting-btn">⚙️</button>
            </div>
        </div>

        <!-- ТУТ БОЛЬШЕ НЕТ ПОИСКА INLINE, ОН В МОДАЛКЕ -->
    </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue';
import { useMainStore } from '@/stores/main_store';

defineEmits(['openSettings', 'openCalendar']);

const mainStore = useMainStore();
const isMobile = ref(window.innerWidth < 768);

const weekInfo = computed(() => {
    const todayStr = new Date().toISOString().substring(0, 10);
    const schedule = mainStore.getDaySchedule(todayStr);
    if (schedule?.week_type) {
        return `${schedule.week_number}-я нед. (${schedule.week_type})`;
    }
    return '';
});

onMounted(() => {
    window.addEventListener('resize', () => {
        isMobile.value = window.innerWidth < 768;
    });
});
</script>

<style scoped>
.controls-wrapper {
    background: var(--glass-bg);
    backdrop-filter: blur(20px);
    -webkit-backdrop-filter: blur(20px);
    border: 1px solid var(--glass-border);
    padding: 12px 20px;
    z-index: 100;
    transition: all 0.3s;
}

/* Mobile: Bottom Fixed */
.controls-wrapper.is-mobile {
    position: fixed;
    bottom: 0;
    left: 0;
    width: 100%;
    border-radius: 20px 20px 0 0;
    box-shadow: 0 -10px 40px rgba(0, 0, 0, 0.3);
    padding-bottom: max(12px, env(safe-area-inset-bottom));
    /* Для iPhone без кнопки */
}

/* Desktop: Top Sticky */
.controls-wrapper:not(.is-mobile) {
    position: sticky;
    top: 20px;
    margin: 0 auto;
    width: 90%;
    max-width: 900px;
    border-radius: 16px;
    margin-bottom: 20px;
}

.status-bar {
    display: flex;
    justify-content: space-between;
    align-items: center;
    cursor: pointer;
}

.main-title {
    font-size: 16px;
    font-weight: 700;
    margin: 0;
    color: var(--text-primary);
}

.week-info {
    font-size: 12px;
    color: var(--accent-color);
    font-weight: 600;
}

.actions {
    display: flex;
    align-items: center;
}

.icon-btn {
    background: rgba(255, 255, 255, 0.05);
    border: none;
    font-size: 20px;
    width: 40px;
    height: 40px;
    border-radius: 50%;
    cursor: pointer;
    margin-left: 10px;
    display: flex;
    align-items: center;
    justify-content: center;
}

.icon-btn:active {
    background: var(--accent-color);
}
</style>