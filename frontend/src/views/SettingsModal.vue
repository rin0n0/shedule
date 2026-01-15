<!-- src/views/SettingsModal.vue -->
<template>
    <div class="modal-overlay" @click.self="$emit('close')">
        <div class="modal-card">
            <div class="modal-header">
                <h3>Настройки</h3>
                <button class="close-btn" @click="$emit('close')">✕</button>
            </div>

            <div class="tabs">
                <button :class="{ active: mode === 'group' }" @click="mode = 'group'">Студент</button>
                <button :class="{ active: mode === 'teacher' }" @click="mode = 'teacher'">Преподаватель</button>
            </div>

            <div class="input-wrapper">
                <input type="text" v-model="query" @input="handleSearch"
                    :placeholder="mode === 'group' ? 'Номер группы (222...)' : 'Фамилия преподавателя'" autofocus />
                <ul v-if="results.length" class="results-list">
                    <li v-for="item in results" :key="item" @click="selectItem(item)">
                        {{ item }}
                    </li>
                </ul>
            </div>

            <!-- Подгруппы (только для студента) -->
            <div class="subgroups" v-if="mode === 'group' && mainStore.userGroup">
                <label>Подгруппа:</label>
                <div class="toggles">
                    <button v-for="sub in [0, 1, 2]" :key="sub" :class="{ active: mainStore.userSubgroup === sub }"
                        @click="mainStore.setSubgroup(sub)">{{ sub === 0 ? 'Все' : sub }}</button>
                </div>
            </div>

            <div class="footer-note">
                <p>Polytech Schedule v1.2</p>
            </div>
        </div>
    </div>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import { useMainStore } from '@/stores/main_store';

const emit = defineEmits(['close']);
const mainStore = useMainStore();
const mode = ref<'group' | 'teacher'>(mainStore.userTeacher ? 'teacher' : 'group');
const query = ref('');
const results = ref<string[]>([]);
let timer: number;

const handleSearch = () => {
    clearTimeout(timer);
    if (query.value.length < 2) { results.value = []; return; }

    timer = setTimeout(async () => {
        results.value = await mainStore.search(query.value, mode.value);
    }, 300);
};

const selectItem = (item: string) => {
    if (mode.value === 'group') mainStore.setGroup(item);
    else mainStore.setTeacher(item);

    emit('close');
    // Небольшой хак для обновления данных
    setTimeout(() => window.location.reload(), 50);
};
</script>

<style scoped>
.modal-overlay {
    position: fixed;
    inset: 0;
    background: rgba(0, 0, 0, 0.6);
    backdrop-filter: blur(10px);
    z-index: 200;
    display: flex;
    justify-content: center;
    align-items: flex-start;
    /* Чтобы на мобилке клавиатура не перекрывала */
    padding-top: 100px;
}

.modal-card {
    background: #1c1c1e;
    width: 90%;
    max-width: 400px;
    border-radius: 20px;
    padding: 20px;
    border: 1px solid rgba(255, 255, 255, 0.1);
}

.modal-header {
    display: flex;
    justify-content: space-between;
    margin-bottom: 20px;
    color: white;
}

.close-btn {
    background: none;
    border: none;
    font-size: 24px;
    color: gray;
    cursor: pointer;
}

.tabs {
    display: flex;
    background: rgba(255, 255, 255, 0.05);
    padding: 4px;
    border-radius: 10px;
    margin-bottom: 20px;
}

.tabs button {
    flex: 1;
    background: none;
    border: none;
    padding: 8px;
    color: gray;
    border-radius: 8px;
    cursor: pointer;
}

.tabs button.active {
    background: #3a3a3c;
    color: white;
}

.input-wrapper {
    position: relative;
    margin-bottom: 20px;
}

input {
    width: 100%;
    padding: 12px;
    border-radius: 10px;
    border: 1px solid #3a3a3c;
    background: #2c2c2e;
    color: white;
    font-size: 16px;
    box-sizing: border-box;
}

.results-list {
    position: absolute;
    top: 100%;
    left: 0;
    width: 100%;
    background: #2c2c2e;
    border-radius: 10px;
    list-style: none;
    padding: 0;
    margin-top: 5px;
    max-height: 200px;
    overflow-y: auto;
    z-index: 10;
    border: 1px solid #3a3a3c;
}

.results-list li {
    padding: 12px;
    border-bottom: 1px solid #3a3a3c;
    color: white;
}

.subgroups {
    color: gray;
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.toggles button {
    background: #2c2c2e;
    border: 1px solid #3a3a3c;
    color: gray;
    padding: 6px 12px;
    border-radius: 6px;
    margin-left: 5px;
    cursor: pointer;
}

.toggles button.active {
    background: var(--accent-color);
    color: white;
    border-color: var(--accent-color);
}

.footer-note {
    text-align: center;
    color: #555;
    font-size: 10px;
    margin-top: 20px;
}
</style>