// Экспорт API клиента и типов
export { default as apiClient } from './client'
export type { ApiResponse, ApiError } from './client'

// Экспорт сервисов и типов
export { emailService, resumeService } from './services'
export type {
  EmailSubscriptionData,
  EmailSubscriptionResponse,
  ResumeUploadResponse,
  SalaryAnalysisResponse
} from './services'