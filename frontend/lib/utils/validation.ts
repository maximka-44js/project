// Валидация email
export const validateEmail = (email: string): { isValid: boolean; error?: string } => {
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
  
  if (!email.trim()) {
    return { isValid: false, error: 'Email обязателен' }
  }
  
  if (!emailRegex.test(email)) {
    return { isValid: false, error: 'Некорректный формат email' }
  }
  
  if (email.length > 254) {
    return { isValid: false, error: 'Email слишком длинный' }
  }
  
  return { isValid: true }
}

// Валидация файлов резюме
export const validateResumeFile = (file: File): { isValid: boolean; error?: string } => {
  // Поддерживаемые форматы
  const allowedTypes = [
    'application/pdf',
    'application/msword',
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
    'text/plain'
  ]
  
  const allowedExtensions = ['.pdf', '.doc', '.docx', '.txt']
  
  // Проверяем тип файла
  if (!allowedTypes.includes(file.type)) {
    const extension = file.name.toLowerCase().slice(file.name.lastIndexOf('.'))
    if (!allowedExtensions.includes(extension)) {
      return { 
        isValid: false, 
        error: 'Поддерживаются только файлы PDF, DOC, DOCX, TXT' 
      }
    }
  }
  
  // Проверяем размер файла (10MB максимум)
  const maxSize = 10 * 1024 * 1024 // 10MB в байтах
  if (file.size > maxSize) {
    return { 
      isValid: false, 
      error: 'Размер файла не должен превышать 10MB' 
    }
  }
  
  // Проверяем что файл не пустой
  if (file.size === 0) {
    return { 
      isValid: false, 
      error: 'Файл не может быть пустым' 
    }
  }
  
  return { isValid: true }
}

// Форматирование размера файла
export const formatFileSize = (bytes: number): string => {
  if (bytes === 0) return '0 Bytes'
  
  const k = 1024
  const sizes = ['Bytes', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
}

// Форматирование зарплаты
export const formatSalary = (amount: number, currency: string = '₽'): string => {
  if (amount >= 1000000) {
    return `${(amount / 1000000).toFixed(1)}M ${currency}`
  } else if (amount >= 1000) {
    return `${(amount / 1000).toFixed(0)}K ${currency}`
  } else {
    return `${amount} ${currency}`
  }
}

// Форматирование диапазона зарплат
export const formatSalaryRange = (
  min: number, 
  max: number, 
  currency: string = '₽'
): string => {
  return `${formatSalary(min, '')} - ${formatSalary(max, currency)}`
}

// Получение имени файла без расширения
export const getFileNameWithoutExtension = (fileName: string): string => {
  return fileName.replace(/\.[^/.]+$/, '')
}

// Получение расширения файла
export const getFileExtension = (fileName: string): string => {
  return fileName.slice(fileName.lastIndexOf('.'))
}

// Дебаунс функция для задержки выполнения
export const debounce = <T extends (...args: any[]) => any>(
  func: T,
  wait: number
): ((...args: Parameters<T>) => void) => {
  let timeout: NodeJS.Timeout | null = null
  
  return (...args: Parameters<T>) => {
    if (timeout) {
      clearTimeout(timeout)
    }
    
    timeout = setTimeout(() => {
      func(...args)
    }, wait)
  }
}

// Проверка поддержки drag & drop
export const isDragDropSupported = (): boolean => {
  const div = document.createElement('div')
  return (('draggable' in div) || ('ondragstart' in div && 'ondrop' in div)) && 
         'FormData' in window && 'FileReader' in window
}

// Обработка ошибок API
export const handleApiError = (error: any): string => {
  if (error.response?.data?.message) {
    return error.response.data.message
  }
  
  if (error.message) {
    return error.message
  }
  
  // Стандартные HTTP ошибки
  if (error.response?.status) {
    switch (error.response.status) {
      case 400:
        return 'Некорректные данные запроса'
      case 401:
        return 'Необходима авторизация'
      case 403:
        return 'Доступ запрещен'
      case 404:
        return 'Ресурс не найден'
      case 413:
        return 'Файл слишком большой'
      case 429:
        return 'Слишком много запросов, попробуйте позже'
      case 500:
        return 'Внутренняя ошибка сервера'
      case 503:
        return 'Сервис временно недоступен'
      default:
        return 'Произошла ошибка при выполнении запроса'
    }
  }
  
  return 'Произошла неожиданная ошибка'
}

// Генерация уникального ID
export const generateId = (): string => {
  return Math.random().toString(36).substr(2, 9)
}

// Задержка для тестирования
export const delay = (ms: number): Promise<void> => {
  return new Promise(resolve => setTimeout(resolve, ms))
}