<!-- src/views/RegisterView.vue -->
<template>
  <div class="register-view">
    <div class="card">
      <h1>Введи номер группы</h1>

      <div class="input-wrapper">
        <input type="text" placeholder="23290907/3091" v-model="searchQuery" @input="handleSearch"
          @keydown.enter="handleEnter" :class="{ 'loading': mainStore.isLoading }" />
        <!-- Маленький спиннер прямо в инпуте -->
        <span v-if="mainStore.isLoading" class="spinner"></span>
      </div>

      <ul class="results">
        <li v-for="group in searchResults" :key="group" @click="selectGroup(group)">
          {{ group }}
        </li>
        <!-- Сообщение, если ничего не найдено -->
        <li v-if="!mainStore.isLoading && searchQuery.length > 2 && searchResults.length === 0" class="no-results">
          Группа не найдена
        </li>
      </ul>
    </div>
  </div>
</template>

<script setup lang="ts">
/* ... скрипт тот же, что и был ... */
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useMainStore } from '@/stores/main_store'

const mainStore = useMainStore()
const router = useRouter()
const searchQuery = ref('')
const searchResults = ref<string[]>([])
let searchTimeout: number;

const handleSearch = () => {
  clearTimeout(searchTimeout);
  if (searchQuery.value.length < 2) {
    searchResults.value = [];
    return;
  }
  searchTimeout = setTimeout(async () => {
    searchResults.value = await mainStore.searchGroups(searchQuery.value);
  }, 500); // Чуть увеличил задержку
}

const selectGroup = (group: string) => {
  mainStore.registerGroup(group);
  router.push({ name: 'Schedule' });
}
const handleEnter = async () => {
  // Если результаты уже есть на экране, берем первый и переходим
  if (searchResults.value.length > 0) {
    selectGroup(searchResults.value[0]!);
    return;
  }

  // Если результатов нет (например, быстро ввели и нажали Enter до поиска),
  // пробуем поискать прямо сейчас
  if (searchQuery.value.length >= 2) {
    // Очищаем таймер обычного поиска, чтобы не дублировать
    clearTimeout(searchTimeout);

    // Ищем принудительно
    const results = await mainStore.searchGroups(searchQuery.value);

    if (results.length > 0) {
      // Если нашли — выбираем первый и переходим
      selectGroup(results[0]!);
    } else {
      // Можно добавить уведомление "Группа не найдена"
      console.warn("Группа не найдена");
    }
  }
}
</script>

<style scoped>
/* ... основные стили те же ... */
.register-view {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100%;
  padding: 20px;
}

.card {
  background: var(--glass-bg);
  backdrop-filter: blur(12px);
  padding: 30px;
  border-radius: 24px;
  text-align: center;
  width: 100%;
  max-width: 400px;
  border: 1px solid var(--glass-border);
}

h1 {
  font-size: 20px;
  margin-bottom: 10px;
}

p {
  color: var(--text-primary);
  margin-bottom: 20px;
}

.input-wrapper {
  position: relative;
}

input {
  width: 100%;
  padding: 16px;
  border-radius: 12px;
  border: 1px solid rgba(0, 0, 0, 0.3);
  background: var(--card-bg);
  color: var(--text-primary);
  font-size: 18px;
  outline: none;
  transition: 0.3s;
  box-sizing: border-box;
  /* Важно! */
}

input:focus {
  border-color: var(--accent-color);
}

/* Спиннер */
.spinner {
  position: absolute;
  right: 15px;
  top: 50%;
  transform: translateY(-50%);
  width: 20px;
  height: 20px;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-top-color: white;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to {
    transform: translateY(-50%) rotate(360deg);
  }
}

.results {
  list-style: none;
  padding: 0;
  margin-top: 15px;
  max-height: 250px;
  overflow-y: auto;
  text-align: left;
}

.results li {
  padding: 12px 16px;
  border-radius: 10px;
  cursor: pointer;
  transition: 0.2s;
  font-size: 16px;
  color: var(--text-secondary);
}

.results li:hover {
  background: rgba(255, 255, 255, 0.1);
  color: white;
}

.no-results {
  padding: 12px;
  color: #666;
  font-style: italic;
  text-align: center;
}
</style>