<template>
    <div class="modal-overlay" @click.self="$emit('close')">
        <div class="modal-card">
            <div class="modal-header">
                <h3>Настройки</h3>
                <button class="close-btn" @click="$emit('close')">✕</button>
            </div>

            <div class="content">
                <!-- СЕКЦИЯ 1: ГРУППА -->
                <div class="setting-block">
                    <label>Твоя группа</label>
                    <div class="input-wrapper">
                        <input type="text" v-model="groupInput" @input="handleSearch" @keydown.enter="saveSettings"
                            placeholder="Начни вводить..." :class="{ 'loading': mainStore.isLoading }" />
                        <span v-if="mainStore.isLoading" class="spinner"></span>
                    </div>

                    <!-- Подсказки (появляются при вводе) -->
                    <ul v-if="searchResults.length > 0" class="results">
                        <li v-for="g in searchResults" :key="g" @click="selectGroup(g)">
                            {{ g }}
                        </li>
                    </ul>
                </div>

                <!-- СЕКЦИЯ 2: ПОДГРУППА -->
                <div class="setting-block">
                    <label>Подгруппа</label>
                    <div class="subgroup-toggles">
                        <button v-for="opt in subgroupOptions" :key="opt.value" class="toggle-btn"
                            :class="{ active: selectedSubgroup === opt.value }" @click="selectedSubgroup = opt.value">
                            {{ opt.label }}
                        </button>
                    </div>
                    <p class="hint">Пары для всей группы показываются всегда.</p>
                </div>

                <button class="save-btn" @click="saveSettings">
                    Сохранить
                </button>

                <!-- <p class="credits">
                    Polytech Schedule v1.1<br>
                    Суверенная разработка 🇷🇺
                </p> -->
            </div>
        </div>
    </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { useMainStore } from '@/stores/main_store';

const emit = defineEmits(['close']);
const mainStore = useMainStore();

// Локальное состояние формы
const groupInput = ref('');
const selectedSubgroup = ref(0);
const searchResults = ref<string[]>([]);
let searchTimeout: number;

const subgroupOptions = [
    { label: 'Все', value: 0 },
    { label: '1', value: 1 },
    { label: '2', value: 2 }
];

// Инициализация данными из стора
onMounted(() => {
    groupInput.value = mainStore.userGroup || '';
    selectedSubgroup.value = mainStore.userSubgroup;
});

// Логика поиска (как в регистрации)
const handleSearch = () => {
    clearTimeout(searchTimeout);
    if (groupInput.value.length < 2) {
        searchResults.value = [];
        return;
    }
    searchTimeout = setTimeout(async () => {
        searchResults.value = await mainStore.searchGroups(groupInput.value);
    }, 300);
}

const selectGroup = (g: string) => {
    groupInput.value = g;
    searchResults.value = []; // Скрываем список после выбора
}

// Сохранение
const saveSettings = () => {
    // 1. Если группа изменилась — регистрируем новую
    if (groupInput.value !== mainStore.userGroup) {
        mainStore.registerGroup(groupInput.value);
        // При смене группы кэш расписания инвалидируется (надо будет перезагрузить страницу или очистить кэш)
        // Самый простой способ обновить все — перезагрузить страницу
        window.location.reload();
        return;
    }

    // 2. Сохраняем подгруппу
    if (selectedSubgroup.value !== mainStore.userSubgroup) {
        mainStore.setSubgroup(selectedSubgroup.value);
    }

    emit('close');
};
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
    background: var(--card-bg);
    border: 1px solid var(--card-border);
    border-radius: 24px;
    padding: 25px;
    width: 90%;
    max-width: 350px;
    animation: slideUp 0.3s ease-out;
    overflow: visible;
    position: relative;
}

.modal-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 20px;
}

.modal-header h3 {
    margin: 0;
    color: var(--text-primary);
}

.close-btn {
    background: none;
    border: none;
    color: var(--text-secondary);
    font-size: 24px;
    padding: 0;
    cursor: pointer;
}

.setting-block {
    margin-bottom: 20px;
    position: relative;
}

.setting-block label {
    display: block;
    margin-bottom: 8px;
    color: var(--text-secondary);
    font-size: 14px;
}

/* Инпут */
.input-wrapper {
    position: relative;
    z-index: 20;
}

input {
    width: 100%;
    padding: 12px;
    border-radius: 12px;
    border: 1px solid var(--card-border);
    background: var(--row-border);
    color: var(--text-primary);
    font-size: 16px;
    outline: none;
    box-sizing: border-box;
}

input:focus {
    border-color: var(--accent-color);
}

/* Спиннер в инпуте */
.spinner {
    position: absolute;
    right: 12px;
    top: 50%;
    transform: translateY(-50%);
    width: 16px;
    height: 16px;
    border: 2px solid var(--card-border);
    border-top-color: var(--text-primary);
    border-radius: 50%;
    animation: spin 1s linear infinite;
}

/* Результаты поиска */
.results {
    list-style: none;
    padding: 0;
    margin: 5px 0 0 0;
    max-height: 200px;
    overflow-y: auto;
    background: var(--card-bg);
    backdrop-filter: blur(20px);
    -webkit-backdrop-filter: blur(20px);
    border-radius: 12px;
    border: 1px solid var(--card-border);
    box-shadow: 0 10px 25px rgba(0, 0, 0, 0.25);
    position: absolute;
    width: 100%;
    top: 100%;
    left: 0;
    z-index: 100;
}

.results li {
    padding: 12px 16px;
    cursor: pointer;
    border-bottom: 1px solid var(--row-border);
    color: var(--text-primary);
}

.results li:hover {
    background: var(--accent-color);
    color: white;
}

.results li:last-child {
    border-bottom: none;
}

/* Переключатели подгрупп */
.subgroup-toggles {
    display: flex;
    gap: 10px;
    position: relative;
    z-index: 10;
}

.toggle-btn {
    flex: 1;
    padding: 10px;
    border: 1px solid transparent;
    /* Убрали рамку по умолчанию */
    background: var(--row-border);
    color: var(--text-secondary);
    border-radius: 10px;
    cursor: pointer;
    transition: 0.2s;
}

.toggle-btn.active {
    background: var(--accent-color);
    color: white;
}

.hint {
    font-size: 11px;
    color: var(--text-tertiary);
    margin-top: 5px;
    font-style: italic;
}

.save-btn {
    width: 100%;
    padding: 14px;
    border: none;
    background: var(--accent-color);
    color: white;
    border-radius: 12px;
    font-size: 16px;
    font-weight: bold;
    cursor: pointer;
    margin-top: 10px;
    position: relative;
    z-index: 10;
}

.save-btn:active {
    opacity: 0.9;
    transform: scale(0.98);
}

.credits {
    margin-top: 20px;
    text-align: center;
    color: var(--text-tertiary);
    font-size: 12px;
}

@keyframes spin {
    to {
        transform: rotate(360deg);
    }
}

@keyframes slideUp {
    from {
        transform: translateY(20px);
        opacity: 0;
    }

    to {
        opacity: 1;
    }
}
</style>