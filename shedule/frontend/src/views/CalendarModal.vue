<!-- components/CalendarModal.vue -->
<template>
    <div class="modal-overlay" @click.self="$emit('close')">
        <div class="modal-card">
            <div class="modal-header">
                <h3>Календарь</h3>
                <button class="close-btn" @click="$emit('close')">✕</button>
            </div>

            <VCalendar transparent borderless :attributes="attributes" @dayclick="onDayClick" @did-move="onPageChange"
                expanded title-position="left" trim-weeks />
        </div>
    </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watchEffect } from 'vue';
import { useRouter } from 'vue-router';
import { useMainStore } from '@/stores/main_store';

const emit = defineEmits(['close']);
const router = useRouter();
const mainStore = useMainStore();

// === ДИНАМИЧЕСКОЕ УПРАВЛЕНИЕ ТЕМОЙ ===
const calendarColor = ref('blue'); // По умолчанию (для светлой темы)
const isDark = ref(window.matchMedia('(prefers-color-scheme: dark)').matches);

// Следим за изменением системной темы
watchEffect(() => {
    const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)');
    isDark.value = mediaQuery.matches;

    // Функция-обработчик
    const handler = (e: MediaQueryListEvent) => {
        isDark.value = e.matches;
    };

    // Вешаем и убираем слушатель
    mediaQuery.addEventListener('change', handler);
    // onUnmounted(() => mediaQuery.removeEventListener('change', handler)); // Если нужно
});

const attributes = computed(() => {
    const attrs: any[] = [
        {
            key: 'today',
            highlight: {
                color: calendarColor.value,
                fillMode: 'outline',
            },
            dates: new Date(),
        }
    ];

    const dots = Array.from(mainStore.activeDays).map(dateStr => new Date(dateStr));

    if (dots.length > 0) {
        attrs.push({
            key: 'has-lessons',
            dot: {
                // Меняем цвет точки в зависимости от темы
                class: isDark.value ? 'vc-dot-dark' : 'vc-dot-light',
            },
            dates: dots,
        });
    }

    return attrs;
});

const onDayClick = (day: any) => {
    router.push({ params: { date: day.id } });
    emit('close');
};

const onPageChange = async (pages: any[]) => {
    if (pages.length > 0) {
        const { year, month } = pages[0];
        const monthStr = `${year}-${String(month).padStart(2, '0')}`;
        await mainStore.fetchActiveDays(monthStr);
    }
};

onMounted(() => {
    const now = new Date();
    const monthStr = `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, '0')}`;
    mainStore.fetchActiveDays(monthStr);
});
</script>

<style scoped>
.modal-overlay {
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background: rgba(0, 0, 0, 0.3);
    backdrop-filter: blur(10px);
    -webkit-backdrop-filter: blur(10px);
    z-index: 100;
    display: flex;
    align-items: center;
    justify-content: center;
    animation: fadeIn 0.2s ease-out;
}

.modal-card {
    /* Используем переменную для фона карточки */
    background: var(--card-bg);
    border: 1px solid var(--card-border);
    border-radius: 24px;
    padding: 25px;
    width: 90%;
    max-width: 400px;
    box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.25);
    animation: slideUp 0.3s ease-out;
}

.modal-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 10px;
}

.modal-header h3 {
    margin: 0;
    color: var(--text-primary);
    font-size: 22px;
}

.close-btn {
    background: none;
    border: none;
    color: var(--text-secondary);
    font-size: 24px;
    padding: 0;
    cursor: pointer;
}

/* === ГЛУБОКАЯ КАСТОМИЗАЦИЯ V-CALENDAR === */
:deep(.vc-container) {
    --vc-bg: transparent;
    --vc-border: none;
    --vc-color: var(--text-primary);
    --vc-accent-500: var(--accent-color);
    --vc-accent-600: var(--accent-color);
    font-family: inherit;
    box-shadow: none;
    padding: 0;
}

/* 1. Основные навигационные стрелки */
:deep(.vc-header .vc-arrow) {
    width: 32px;
    height: 32px;
    border-radius: 8px;
    background: var(--row-border);
    /* Используем переменную */
    color: var(--text-primary);
    transition: 0.2s;
    border: none !important;
    box-shadow: none !important;
}

:deep(.vc-header .vc-arrow:hover) {
    background: var(--card-border);
}

/* 2. Название месяца и года (Шапка) */
:deep(.vc-title) {
    padding: 8px 12px;
    border-radius: 8px;
    background: var(--row-border);
    /* Используем переменную */
    color: var(--text-primary);
    font-weight: 600;
    font-size: 16px;
    border: none;
    transition: 0.2s;
}

:deep(.vc-title:hover) {
    background: var(--card-border);
}

/* 3. Дни недели (ПН, ВТ, СР...) */
:deep(.vc-weekday) {
    color: var(--text-secondary);
}

/* 4. Ячейки дней */
:deep(.vc-day) {
    height: 40px;
}

:deep(.vc-day-content) {
    width: 36px;
    height: 36px;
    font-size: 15px;
    font-weight: 500;
    color: var(--text-primary);
    border: 2px solid transparent;
    transition: 0.2s;
}

:deep(.vc-highlight-bg) {
    background: none !important;
}

:deep(.vc-highlight.vc-attr) .vc-highlight-content {
    border: 2px solid var(--accent-color) !important;
    border-radius: 50% !important;
}

/* 5. МЕНЮ НАВИГАЦИИ (Всплывающее окно) */
:deep(.vc-nav-popover-container) {
    box-shadow: 0 10px 20px rgba(0, 0, 0, 0.2);
}

:deep(.vc-nav-popover) {
    background-color: var(--card-bg) !important;
    /* Используем переменную */
    backdrop-filter: blur(20px);
    -webkit-backdrop-filter: blur(20px);
    border: 1px solid var(--card-border) !important;
    border-radius: 12px !important;
    padding: 10px !important;
}

/* Заголовок внутри поповера (2026) */
:deep(.vc-nav-header) {
    border-bottom: 1px solid var(--card-border) !important;
}

:deep(.vc-nav-title) {
    background-color: transparent !important;
    color: var(--text-primary) !important;
    border: none !important;
    box-shadow: none !important;
}

:deep(.vc-nav-title span) {
    background-color: transparent !important;
    color: inherit !important;
    border: none !important;
    box-shadow: none !important;
}

/* Стрелки ВНУТРИ всплывающего меню */
:deep(.vc-nav-popover .vc-arrow) {
    background-color: var(--row-border) !important;
    /* Используем переменную */
    border: none !important;
    border-radius: 8px !important;
    box-shadow: none !important;
    width: 32px;
    height: 32px;
}

:deep(.vc-nav-popover .vc-arrow:hover) {
    background-color: var(--card-border) !important;
}

/* Кнопки месяцев/годов */
:deep(.vc-nav-item) {
    background: var(--row-border) !important;
    /* Используем переменную */
    border-radius: 8px !important;
    border: none !important;
    color: var(--text-primary) !important;
}

:deep(.vc-nav-item.is-active) {
    background-color: var(--accent-color) !important;
    color: white !important;
}

:deep(.vc-nav-item:hover) {
    background-color: var(--card-border) !important;
}

/* Анимации */
@keyframes slideUp {
    from {
        transform: translateY(20px);
        opacity: 0;
    }

    to {
        transform: translateY(0);
        opacity: 1;
    }
}

@keyframes fadeIn {
    from {
        opacity: 0;
    }

    to {
        opacity: 1;
    }
}
</style>