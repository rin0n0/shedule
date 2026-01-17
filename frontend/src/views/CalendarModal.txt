<template>
    <div class="modal-overlay" @click.self="$emit('close')">
        <div class="modal-card">
            <div class="modal-header">
                <h3>Календарь</h3>
                <button class="close-btn" @click="$emit('close')">✕</button>
            </div>

            <VCalendar transparent borderless expanded trim-weeks title-position="left" :attributes="attributes"
                @dayclick="onDayClick" @did-move="onPageChange" />
        </div>
    </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onBeforeUnmount } from 'vue';
import { useRouter } from 'vue-router';
import { useMainStore } from '@/stores/main_store';

const emit = defineEmits(['close']);
const router = useRouter();
const mainStore = useMainStore();

/* ======================================================
   АКЦЕНТНЫЙ ЦВЕТ — НАПРЯМУЮ ИЗ :root
====================================================== */

const calendarColor = ref<string>('#0a84ff');

const readAccentColor = () => {
    if (typeof window === 'undefined') return;
    const styles = getComputedStyle(document.documentElement);
    calendarColor.value = styles.getPropertyValue('--accent-color').trim();
};

let observer: MutationObserver | null = null;

onMounted(() => {
    readAccentColor();

    observer = new MutationObserver(readAccentColor);
    observer.observe(document.documentElement, {
        attributes: true,
        attributeFilter: ['style', 'class'],
    });

    const now = new Date();
    const monthStr = `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, '0')}`;
    mainStore.fetchActiveDays(monthStr);
});

onBeforeUnmount(() => {
    observer?.disconnect();
});

/* ======================================================
   ATTRIBUTES ДЛЯ V-CALENDAR
====================================================== */

const attributes = computed(() => {
    const attrs: any[] = [
        {
            key: 'today',
            highlight: {
                color: calendarColor.value,
                fillMode: 'outline',
            },
            dates: new Date(),
        },
    ];

    const dots = Array.from(mainStore.activeDays).map(
        dateStr => new Date(dateStr)
    );

    if (dots.length) {
        attrs.push({
            key: 'has-lessons',
            dot: { class: 'vc-dot-accent' },
            dates: dots,
        });
    }

    return attrs;
});

/* ======================================================
   ОБРАБОТЧИКИ
====================================================== */

const onDayClick = (day: any) => {
    router.push({ params: { date: day.id } });
    emit('close');
};

const onPageChange = async (pages: any[]) => {
    if (!pages.length) return;
    const { year, month } = pages[0];
    const monthStr = `${year}-${String(month).padStart(2, '0')}`;
    await mainStore.fetchActiveDays(monthStr);
};
</script>

<style scoped>
.modal-overlay {
    position: fixed;
    inset: 0;
    background: var(--accent-color-light);
    backdrop-filter: blur(10px);
    -webkit-backdrop-filter: blur(10px);
    z-index: 100;
    display: flex;
    align-items: center;
    justify-content: center;
    animation: fadeIn 0.2s ease-out;
}

.modal-card {
    background: var(--card-bg);
    border: 1px solid var(--card-border);
    border-radius: 24px;
    padding: 25px;
    width: 90%;
    max-width: 400px;
    box-shadow: 0 25px 50px -12px var(--card-border);
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
    cursor: pointer;
}

/* ======================================================
   V-CALENDAR
====================================================== */

:deep(.vc-container) {
    --vc-bg: transparent;
    --vc-border: none;
    --vc-color: var(--text-primary);
    --vc-accent-500: var(--accent-color);
    --vc-accent-600: var(--accent-color);
    font-family: inherit;
    padding: 0;
}

/* стрелки */
:deep(.vc-arrow) {
    background: var(--row-border);
    color: var(--text-primary);
    border-radius: 8px;
    width: 32px;
    height: 32px;
}

:deep(.vc-arrow:hover) {
    background: var(--card-border);
}

/* заголовок */
:deep(.vc-title) {
    background: var(--row-border);
    color: var(--text-primary);
    padding: 8px 12px;
    border-radius: 8px;
    font-weight: 600;
}

:deep(.vc-weekday) {
    color: var(--text-secondary);
}

/* дни */
:deep(.vc-day-content) {
    color: var(--text-primary);
    font-weight: 500;
}

:deep(.vc-highlight-bg) {
    background: none !important;
}

:deep(.vc-highlight.vc-attr) .vc-highlight-content {
    border: 2px solid var(--accent-color) !important;
    border-radius: 50% !important;
}

/* точки */
:deep(.vc-dot-accent) {
    background-color: var(--accent-color) !important;
}

/* навигационный поповер */
:deep(.vc-nav-popover) {
    background: var(--card-bg) !important;
    border: 1px solid var(--card-border) !important;
    backdrop-filter: blur(20px);
    border-radius: 12px;
}

:deep(.vc-nav-item) {
    background: var(--row-border);
    color: var(--text-primary);
    border-radius: 8px;
}

:deep(.vc-nav-item.is-active) {
    background: var(--accent-color);
    color: var(--text-primary);
}

/* ======================================================
   АНИМАЦИИ
====================================================== */

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
