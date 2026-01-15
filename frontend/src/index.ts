const API_BASE_URL = "/api";

export const apiClient = {
  async get<T>(endpoint: string): Promise<T> {
    const response = await fetch(`${API_BASE_URL}${endpoint}`);
    if (!response.ok) {
      const errorData = await response
        .json()
        .catch(() => ({ detail: "Ошибка сервера" }));
      throw new Error(errorData.detail || `Ошибка ${response.status}`);
    }
    return response.json() as Promise<T>;
  },
};
