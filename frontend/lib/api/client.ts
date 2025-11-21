import axios, { AxiosInstance, AxiosResponse, InternalAxiosRequestConfig } from 'axios'

// Базовая конфигурация API
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8001/api'

// Создаем экземпляр axios
const apiClient: AxiosInstance = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000, // 30 секунд для загрузки файлов
  headers: {
    'Content-Type': 'application/json',
  },
})

// Перехватчик запросов
apiClient.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    // Логирование запросов в development
    if (process.env.NODE_ENV === 'development') {
      console.log(`[API Request] ${config.method?.toUpperCase()} ${config.url}`, config.data)
    }
    
    // Добавляем авторизацию если есть токен (для будущего использования)
    const token = localStorage.getItem('auth_token')
    if (token && config.headers) {
      config.headers.Authorization = `Bearer ${token}`
    }
    
    return config
  },
  (error) => {
    console.error('[API Request Error]', error)
    return Promise.reject(error)
  }
)

// Перехватчик ответов
apiClient.interceptors.response.use(
  (response: AxiosResponse) => {
    // Логирование ответов в development
    if (process.env.NODE_ENV === 'development') {
      console.log(`[API Response] ${response.status}`, response.data)
    }
    return response
  },
  (error) => {
    // Централизованная обработка ошибок
    console.error('[API Response Error]', error.response?.data || error.message)
    
    // Обработка специфичных статус кодов
    if (error.response?.status === 401) {
      // Очищаем токен при неавторизованном доступе
      localStorage.removeItem('auth_token')
      // Перенаправляем на страницу авторизации (если нужно)
    }
    
    if (error.response?.status === 413) {
      // Файл слишком большой
      throw new Error('Файл слишком большой. Максимальный размер: 10MB')
    }
    
    if (error.response?.status === 429) {
      // Слишком много запросов
      throw new Error('Слишком много запросов. Попробуйте позже')
    }
    
    return Promise.reject(error)
  }
)

export default apiClient

// Типы для API ответов
export interface ApiResponse<T = any> {
  data: T
  message?: string
  success: boolean
}

export interface ApiError {
  message: string
  code?: string
  details?: any
}