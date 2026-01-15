<template>
    <footer class="app-footer">
        <button class="nav-btn" @click="$emit('openCalendar')">
            📅 <span class="label">Дата</span>
        </button>

        <button class="nav-btn" @click="$emit('openSettings')">
            ⚙️ <span class="label">Настройки</span>
        </button>
    </footer>
</template>

<script setup lang="ts">
// Объявляем события, которые футер посылает наверх
defineEmits(['openCalendar', 'openSettings']);

const share = async () => {
    if (navigator.share) {
        try {
            await navigator.share({
                title: 'Расписание',
                text: 'Мое расписание в Polytech Schedule',
                url: window.location.href,
            });
        } catch (e) {
            // Игнорируем отмену шеринга
        }
    } else {
        // Фоллбэк: копирование в буфер
        navigator.clipboard.writeText(window.location.href);
        alert('Ссылка скопирована!');
    }
}
</script>

<style scoped>
.app-footer {
    position: absolute;
    bottom: 20px;
    left: 50%;
    transform: translateX(-50%);
    width: 90%;
    max-width: 400px;
    height: 70px;
    background: rgba(255, 255, 255, 0.1);
    backdrop-filter: blur(15px);
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: 20px;
    display: flex;
    justify-content: space-evenly;
    align-items: center;
    box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
    z-index: 50;
    /* Поверх всего */
}

.nav-btn {
    background: none;
    border: none;
    cursor: pointer;
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 4px;
    color: var(--text-primary);
    font-size: 30px;
    opacity: 0.7;
    transition: 0.2s;
}

.nav-btn:active {
    opacity: 1;
    transform: scale(0.95);
}

.nav-btn.main {
    background: var(--accent-color);
    width: 50px;
    height: 50px;
    border-radius: 15px;
    display: flex;
    justify-content: center;
    align-items: center;
    font-size: 24px;
    opacity: 1;
    margin-top: -30px;
    /* Выпирает вверх */
}

.label {
    font-size: 10px;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}
</style>