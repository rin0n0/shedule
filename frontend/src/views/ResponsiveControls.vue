<template>
    <div class="controls-wrapper" :class="{ 'is-mobile': isMobile }">

        <!-- Левая часть: Название и неделя -->
        <div class="info-block" @click="$emit('openSettings')">
            <h2 class="main-title">{{ mainStore.currentModeTitle || 'Настроить расписание' }}</h2>
            <!--ПОТОМ НАДА ДОДЕЛАТЬ НО ЗНААМЕНАТЕЛЬ РЕАКТИВНО НЕ ИЗМЕНЯЕТСЯ <span class="week-info">{{ mainStore.currentWeekInfo }}</span> -->
        </div>

        <!-- Правая часть: Блок с кнопками -->
        <div class="action-group">
            <button class="action-btn" @click.stop="$emit('openCalendar')">
                <span class="icon">📅</span>
                <span class="label">Календарь</span>
            </button>
            <button class="action-btn" @click.stop="$emit('openSettings')">
                <span class="icon">⚙️</span>
                <span class="label">Параметры</span>
            </button>
        </div>
    </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { useMainStore } from '@/stores/main_store';

defineEmits(['openSettings', 'openCalendar']);

const mainStore = useMainStore();
const isMobile = ref(window.innerWidth < 768);

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
    z-index: 100;
    transition: all 0.3s;

    display: flex;
    justify-content: space-between;
    align-items: center;
    gap: 15px;
}

/* Mobile: Прибит к низу */
.controls-wrapper.is-mobile {
    position: fixed;
    bottom: 0;
    left: 0;
    right: 0;
    margin: 10px;
    /* Отступы от краев */
    border-radius: 20px;
    /* Сильное скругление */
    box-shadow: 0 10px 40px rgba(0, 0, 0, 0.3);
    padding: 10px;
}

/* Desktop: Сверху */
.controls-wrapper:not(.is-mobile) {
    top: 20px;
    margin: 0 auto 20px;
    width: 90%;
    max-width: 900px;
    border-radius: 16px;
    padding: 12px 20px;
}

/* === ФИКС ДЛЯ МОБИЛОК: Левый блок теперь гибкий === */
.info-block {
    flex: 1;
    /* Занимает все доступное место */
    min-width: 0;
    /* Позволяет блоку сжиматься */
    cursor: pointer;
}

.main-title {
    font-size: 16px;
    font-weight: 700;
    color: var(--text-primary);
    margin: 0;

    /* Обрезка длинных названий */
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}

.week-info {
    font-size: 12px;
    color: var(--accent-color);
    font-weight: 600;
}

/* === НОВЫЙ БЛОК КНОПОК === */
.action-group {
    display: flex;
    background: rgba(0, 0, 0, 0.1);
    border-radius: 16px;
    padding: 4px;
    flex-shrink: 0;
    /* Не сжиматься */
}

.action-btn {
    background: none;
    border: none;
    cursor: pointer;

    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    gap: 2px;

    color: var(--text-secondary);
    padding: 4px 12px;
    border-radius: 12px;
    transition: 0.2s;
    min-width: 70px;
}

.action-btn:hover,
.action-btn:active {
    background: var(--accent-color);
    color: white;
}

.icon {
    font-size: 20px;
}

.label {
    font-size: 10px;
    font-weight: 600;
    text-transform: uppercase;
}
</style>