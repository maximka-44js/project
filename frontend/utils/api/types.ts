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

// Запрос на анализ через форму
export interface FormAnalysisRequest {
  vacancy_nm: string;
  location: string;
  schedule: string;
  experience: string;
  work_hours: number;
  skills_text: string;
}

// Типы для выбора графика работы
export type ScheduleType = 
  | 'OTHER' 
  | 'FLEXIBLE' 
  | 'SIX_ON_ONE_OFF' 
  | 'FIVE_ON_TWO_OFF'
  | 'TWO_ON_TWO_OFF' 
  | 'THREE_ON_THREE_OFF' 
  | 'FOUR_ON_TWO_OFF'
  | 'unknown' 
  | 'ONE_ON_THREE_OFF' 
  | 'WEEKEND' 
  | 'FOUR_ON_FOUR_OFF'
  | 'TWO_ON_ONE_OFF' 
  | 'FOUR_ON_THREE_OFF' 
  | 'ONE_ON_TWO_OFF'
  | 'THREE_ON_TWO_OFF';

// Типы для выбора опыта работы
export type ExperienceType = 'between1And3' | 'noExperience' | 'between3And6' | 'moreThan6';

// Опции для выбора графика работы
export const SCHEDULE_OPTIONS: { value: ScheduleType; label: string }[] = [
  { value: 'FIVE_ON_TWO_OFF', label: '5/2 (пятидневка)' },
  { value: 'SIX_ON_ONE_OFF', label: '6/1 (шестидневка)' },
  { value: 'FLEXIBLE', label: 'Гибкий график' },
  { value: 'TWO_ON_TWO_OFF', label: '2/2' },
  { value: 'THREE_ON_THREE_OFF', label: '3/3' },
  { value: 'FOUR_ON_TWO_OFF', label: '4/2' },
  { value: 'FOUR_ON_THREE_OFF', label: '4/3' },
  { value: 'FOUR_ON_FOUR_OFF', label: '4/4' },
  { value: 'ONE_ON_TWO_OFF', label: '1/2' },
  { value: 'ONE_ON_THREE_OFF', label: '1/3' },
  { value: 'TWO_ON_ONE_OFF', label: '2/1' },
  { value: 'THREE_ON_TWO_OFF', label: '3/2' },
  { value: 'WEEKEND', label: 'Только выходные' },
  { value: 'OTHER', label: 'Другой' },
  { value: 'unknown', label: 'Не указано' },
];

// Опции для выбора опыта работы
export const EXPERIENCE_OPTIONS: { value: ExperienceType; label: string }[] = [
  { value: 'noExperience', label: 'Без опыта' },
  { value: 'between1And3', label: 'От 1 до 3 лет' },
  { value: 'between3And6', label: 'От 3 до 6 лет' },
  { value: 'moreThan6', label: 'Более 6 лет' },
];

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