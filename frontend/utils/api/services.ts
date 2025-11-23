import axios from 'axios';
import { 
  UploadResponse, 
  FileInfo, 
  AnalysisRequest,
  FormAnalysisRequest, 
  AnalysisStartResponse, 
  AnalysisResponse 
} from './types';

// Базовые URL для микросервисов
const UPLOAD_SERVICE_URL = process.env.NEXT_PUBLIC_UPLOAD_SERVICE_URL || 'http://localhost:8003';
const ANALYSIS_SERVICE_URL = process.env.NEXT_PUBLIC_ANALYSIS_SERVICE_URL || 'http://localhost:8004';

// Настройка axios клиентов
const uploadClient = axios.create({
  baseURL: UPLOAD_SERVICE_URL,
  timeout: 30000, // 30 секунд для загрузки файлов
});

const analysisClient = axios.create({
  baseURL: ANALYSIS_SERVICE_URL,
  timeout: 10000, // 10 секунд для обычных запросов
  headers: {
    'Content-Type': 'application/json',
  },
});

/**
 * Загружает файл резюме на сервер
 * @param file - файл для загрузки
 * @returns Promise с информацией о загруженном файле
 */
export const uploadResumeFile = async (file: File): Promise<UploadResponse> => {
  const formData = new FormData();
  formData.append('file', file);
  
  const response = await uploadClient.post<UploadResponse>('/upload', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });
  return response.data;
};

/**
 * Получает информацию о загруженном файле и извлеченный текст
 * @param uploadId - ID загруженного файла
 * @returns Promise с информацией о файле
 */
export const getFileInfo = async (uploadId: string): Promise<FileInfo> => {
  const response = await uploadClient.get<FileInfo>(`/${uploadId}/content`);
  return response.data;
};

/**
 * Запускает анализ текста резюме
 * @param text - текст для анализа
 * @returns Promise с информацией о начале анализа
 */
export const startAnalysis = async (text: string): Promise<AnalysisStartResponse> => {
  const request: AnalysisRequest = { text };
  const response = await analysisClient.post<AnalysisStartResponse>('/analysis/from_raw_text', request);
  return response.data;
};

/**
 * Запускает анализ данных резюме через форму
 * @param formData - данные формы для анализа
 * @returns Promise с информацией о начале анализа
 */
export const startFormAnalysis = async (formData: FormAnalysisRequest): Promise<AnalysisStartResponse> => {
  // Преобразуем данные в FormData для отправки как form-data
  const form = new URLSearchParams();
  form.append('vacancy_nm', formData.vacancy_nm);
  form.append('location', formData.location);
  form.append('schedule', formData.schedule);
  form.append('experience', formData.experience);
  form.append('work_hours', formData.work_hours.toString());
  form.append('skills_text', formData.skills_text);

  const response = await analysisClient.post<AnalysisStartResponse>('/analysis/from_form_data', form, {
    headers: {
      'Content-Type': 'application/x-www-form-urlencoded',
    },
  });
  return response.data;
};

/**
 * Проверяет статус выполнения анализа
 * @param taskId - ID задачи анализа
 * @returns Promise с результатом анализа
 */
export const checkAnalysisStatus = async (taskId: string): Promise<AnalysisResponse> => {
  const response = await analysisClient.get<AnalysisResponse>(`/analysis/task/${taskId}`);
  return response.data;
};

/**
 * Полный цикл анализа резюме: загрузка файла, извлечение текста, анализ и получение результата
 * @param file - файл резюме
 * @param onProgress - callback для отслеживания прогресса
 * @returns Promise с результатом анализа
 */
export const analyzeResume = async (
  file: File,
  onProgress?: (progress: number, status: string) => void
): Promise<AnalysisResponse> => {
  try {
    // Шаг 1: Загрузка файла
    onProgress?.(10, 'Загрузка файла...');
    const uploadResult = await uploadResumeFile(file);
    console.log('Upload result:', uploadResult);
    
    if (!uploadResult.parsed) {
      throw new Error('Файл не удалось обработать');
    }

    // Шаг 2: Получение информации о файле и текста
    onProgress?.(30, 'Извлечение текста из файла...');
    const fileInfo = await getFileInfo(uploadResult.id);
    console.log('File info:', fileInfo);

    // Шаг 3: Запуск анализа
    onProgress?.(50, 'Запуск анализа резюме...');
    const analysisStart = await startAnalysis(fileInfo.text);
    console.log('Analysis start:', analysisStart);

    if (!analysisStart.success) {
      throw new Error(analysisStart.message || 'Ошибка запуска анализа');
    }

    // Шаг 4: Ожидание результата анализа (проверяем каждые 3 секунды)
    onProgress?.(70, 'Анализ резюме в процессе...');
    
    let attempts = 0;
    const maxAttempts = 20; // Максимум 1 минута ожидания
    
    while (attempts < maxAttempts) {
      await new Promise(resolve => setTimeout(resolve, 3000)); // Ждем 3 секунды
      
      try {
        const analysisResult = await checkAnalysisStatus(analysisStart.task_id);
        console.log(`Analysis status check ${attempts + 1}:`, analysisResult);
        
        // Если есть ошибка, выбрасываем исключение
        if (analysisResult.error) {
          throw new Error(analysisResult.error);
        }
        
        // Если анализ завершен успешно
        if (analysisResult.success && analysisResult.result) {
          onProgress?.(100, 'Анализ завершен!');
          return analysisResult;
        }
        
        // Если статус показывает, что задача еще выполняется
        if (analysisResult.status === 'pending' || analysisResult.status === 'processing') {
          onProgress?.(70 + (attempts * 2), 'Анализ резюме в процессе...');
          attempts++;
          continue;
        }
        
        // Если статус "completed" но нет результата, это может быть ошибка
        if (analysisResult.status === 'completed' && !analysisResult.result) {
          throw new Error('Анализ завершен, но результат отсутствует');
        }
        
        // Если статус неизвестен, но нет ошибки, продолжаем ждать
        attempts++;
      } catch (statusError) {
        // Если ошибка при проверке статуса, попробуем еще раз
        console.error(`Error checking status (attempt ${attempts + 1}):`, statusError);
        attempts++;
        if (attempts >= maxAttempts) {
          throw statusError;
        }
      }
    }
    
    throw new Error('Превышено время ожидания анализа');
    
  } catch (error) {
    console.error('Ошибка при анализе резюме:', error);
    
    // Улучшенная обработка ошибок
    if (axios.isAxiosError(error)) {
      if (error.response) {
        // Сервер ответил с кодом ошибки
        const status = error.response.status;
        const message = error.response.data?.message || error.response.data?.error || error.message;
        
        if (status === 404) {
          throw new Error('Сервис временно недоступен. Попробуйте позже.');
        } else if (status === 400) {
          throw new Error(`Ошибка в запросе: ${message}`);
        } else if (status >= 500) {
          throw new Error('Ошибка сервера. Попробуйте позже.');
        } else {
          throw new Error(`Ошибка ${status}: ${message}`);
        }
      } else if (error.request) {
        // Запрос был отправлен, но ответа не получено
        throw new Error('Не удается подключиться к серверу. Проверьте, что сервисы запущены.');
      } else {
        // Ошибка при настройке запроса
        throw new Error(`Ошибка настройки запроса: ${error.message}`);
      }
    }
    
    throw error;
  }
};

/**
 * Анализ резюме через форму: отправка данных и получение результата
 * @param formData - данные формы
 * @param onProgress - callback для отслеживания прогресса
 * @returns Promise с результатом анализа
 */
export const analyzeResumeFromForm = async (
  formData: FormAnalysisRequest,
  onProgress?: (progress: number, status: string) => void
): Promise<AnalysisResponse> => {
  try {
    // Шаг 1: Запуск анализа
    onProgress?.(20, 'Отправка данных для анализа...');
    const analysisStart = await startFormAnalysis(formData);

    if (!analysisStart.success) {
      throw new Error(analysisStart.message || 'Ошибка запуска анализа');
    }

    // Шаг 2: Ожидание результата анализа (проверяем каждые 3 секунды)
    onProgress?.(50, 'Анализ данных в процессе...');
    
    let attempts = 0;
    const maxAttempts = 20; // Максимум 1 минута ожидания
    
    while (attempts < maxAttempts) {
      await new Promise(resolve => setTimeout(resolve, 3000)); // Ждем 3 секунды
      
      const analysisResult = await checkAnalysisStatus(analysisStart.task_id);
      
      // Если есть ошибка, выбрасываем исключение
      if (analysisResult.error) {
        throw new Error(analysisResult.error);
      }
      
      // Если анализ завершен успешно
      if (analysisResult.success && analysisResult.result) {
        onProgress?.(100, 'Анализ завершен!');
        return analysisResult;
      }
      
      // Если статус показывает, что задача еще выполняется
      if (analysisResult.status === 'pending' || analysisResult.status === 'processing') {
        onProgress?.(50 + (attempts * 2), 'Анализ данных в процессе...');
        attempts++;
        continue;
      }
      
      // Если статус неизвестен, но нет ошибки, продолжаем ждать
      attempts++;
    }
    
    throw new Error('Превышено время ожидания анализа');
    
  } catch (error) {
    console.error('Ошибка при анализе данных формы:', error);
    throw error;
  }
};