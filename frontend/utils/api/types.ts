// Типы для API ответов микросервисов

// Ответ на загрузку файла
export interface UploadResponse {
  id: string;
  parsed: boolean;
}

// Информация о загруженном файле
export interface FileInfo {
  id: string;
  filename: string;
  file_type: string;
  uploaded_at: string;
  text: string;
}

// Запрос на анализ текста
export interface AnalysisRequest {
  text: string;
}

// Ответ на начало анализа
export interface AnalysisStartResponse {
  task_id: string;
  success: boolean;
  message: string;
}

// Извлеченные данные из резюме
export interface ExtractedData {
  vacancy_nm: string;
  location: string;
  schedule: string;
  experience: string;
  work_hours: number;
  skills_text: string;
}

// Предсказание зарплаты
export interface SalaryPrediction {
  lowest_salary: number;
  highest_salary: number;
  currency: string;
}

// Результат анализа
export interface AnalysisResult {
  extracted_data: ExtractedData;
  profession_id: number;
  salary_prediction: SalaryPrediction;
  recommendations: string;
}

// Полный ответ результата анализа
export interface AnalysisResponse {
  success: boolean;
  result?: AnalysisResult;
  error?: string;
  status: string;
}

// Состояния процесса загрузки и анализа
export enum ProcessState {
  IDLE = 'idle',
  UPLOADING = 'uploading',
  UPLOADED = 'uploaded',
  ANALYZING = 'analyzing',
  COMPLETED = 'completed',
  ERROR = 'error'
}

// Интерфейс для хранения состояния приложения
export interface AppState {
  state: ProcessState;
  uploadId?: string;
  taskId?: string;
  fileInfo?: FileInfo;
  analysisResult?: AnalysisResult;
  error?: string;
  progress?: number;
}