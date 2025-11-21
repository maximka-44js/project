import apiClient, { ApiResponse } from './client'

// Типы данных для API
export interface EmailSubscriptionData {
  email: string
  source?: string
  metadata?: Record<string, any>
}

export interface EmailSubscriptionResponse {
  id: string
  email: string
  subscribed: boolean
  created_at: string
}

export interface ResumeUploadResponse {
  upload_id: string
  file_name: string
  file_size: number
  status: 'uploaded' | 'processing' | 'completed' | 'error'
  analysis_id?: string
}

export interface SalaryAnalysisResponse {
  analysis_id: string
  status: 'processing' | 'completed' | 'error'
  results?: {
    position_levels: Array<{
      level: string
      salary_min: number
      salary_max: number
      currency: string
      confidence: number
    }>
    market_data: {
      total_vacancies_analyzed: number
      data_freshness_days: number
      location: string
    }
    recommendations?: string[]
  }
  error_message?: string
}

// Сервис для работы с email подписками
export const emailService = {
  /**
   * Подписать email на получение анализа зарплат
   * POST /api/v1/emails/subscribe
   */
  async subscribe(data: EmailSubscriptionData): Promise<EmailSubscriptionResponse> {
    const response = await apiClient.post<ApiResponse<EmailSubscriptionResponse>>(
      '/v1/emails/subscribe',
      {
        email: data.email,
        source: data.source || 'hero_section',
        metadata: data.metadata || {}
      }
    )
    return response.data.data
  },

  /**
   * Проверить статус подписки
   * GET /api/v1/emails/status/{email}
   */
  async checkStatus(email: string): Promise<EmailSubscriptionResponse> {
    const response = await apiClient.get<ApiResponse<EmailSubscriptionResponse>>(
      `/v1/emails/status/${encodeURIComponent(email)}`
    )
    return response.data.data
  }
}

// Сервис для работы с резюме и анализом зарплат
export const resumeService = {
  /**
   * Загрузить резюме для анализа
   * POST /api/v1/resumes/upload
   */
  async uploadResume(file: File, email?: string): Promise<ResumeUploadResponse> {
    const formData = new FormData()
    formData.append('resume', file)
    if (email) {
      formData.append('email', email)
    }

    const response = await apiClient.post<ApiResponse<ResumeUploadResponse>>(
      '/v1/resumes/upload',
      formData,
      {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
        // Прогресс загрузки можно отслеживать
        onUploadProgress: (progressEvent) => {
          if (progressEvent.total) {
            const percentCompleted = Math.round((progressEvent.loaded * 100) / progressEvent.total)
            console.log(`Upload progress: ${percentCompleted}%`)
          }
        }
      }
    )
    return response.data.data
  },

  /**
   * Получить результаты анализа зарплат
   * GET /api/v1/analysis/{analysis_id}
   */
  async getAnalysisResults(analysisId: string): Promise<SalaryAnalysisResponse> {
    const response = await apiClient.get<ApiResponse<SalaryAnalysisResponse>>(
      `/v1/analysis/${analysisId}`
    )
    return response.data.data
  },

  /**
   * Запустить анализ резюме (если загрузка и анализ разделены)
   * POST /api/v1/analysis/start
   */
  async startAnalysis(uploadId: string, email?: string): Promise<SalaryAnalysisResponse> {
    const response = await apiClient.post<ApiResponse<SalaryAnalysisResponse>>(
      '/v1/analysis/start',
      {
        upload_id: uploadId,
        email: email
      }
    )
    return response.data.data
  },

  /**
   * Получить список поддерживаемых форматов файлов
   * GET /api/v1/resumes/supported-formats
   */
  async getSupportedFormats(): Promise<string[]> {
    const response = await apiClient.get<ApiResponse<string[]>>(
      '/v1/resumes/supported-formats'
    )
    return response.data.data
  }
}

// Сервис для работы с аутентификацией
export const authService = {
  /**
   * Регистрация нового пользователя
   * POST /api/v1/auth/register
   */
  async register(data: {
    email: string
    password: string
    full_name: string
  }): Promise<{
    access_token: string
    refresh_token: string
    token_type: string
    expires_in: number
    user: {
      id: number
      email: string
      full_name: string
      is_active: boolean
      created_at: string
      updated_at: string
    }
  }> {
    const response = await apiClient.post<{
      access_token: string
      refresh_token: string
      token_type: string
      expires_in: number
      user: {
        id: number
        email: string
        full_name: string
        is_active: boolean
        created_at: string
        updated_at: string
      }
    }>('/v1/auth/register', data)
    return response.data
  },

  /**
   * Вход в систему
   * POST /api/v1/auth/login
   */
  async login(data: {
    email: string
    password: string
  }): Promise<{
    access_token: string
    refresh_token: string
    token_type: string
    expires_in: number
    user: {
      id: number
      email: string
      full_name: string
      is_active: boolean
      created_at: string
      updated_at: string
    }
  }> {
    const response = await apiClient.post<{
      access_token: string
      refresh_token: string
      token_type: string
      expires_in: number
      user: {
        id: number
        email: string
        full_name: string
        is_active: boolean
        created_at: string
        updated_at: string
      }
    }>('/v1/auth/login', data)
    return response.data
  }
}