'use client'

import { useState, useCallback, useEffect } from 'react'
import { generateId } from '@/lib/utils/validation'

export type ToastType = 'success' | 'error' | 'warning' | 'info'

export interface Toast {
  id: string
  type: ToastType
  title: string
  message?: string
  duration?: number
  action?: {
    label: string
    onClick: () => void
  }
}

// Глобальное состояние для тостов (простая реализация)
let toasts: Toast[] = []
let listeners: ((toasts: Toast[]) => void)[] = []

const notifyListeners = () => {
  listeners.forEach(listener => listener([...toasts]))
}

// API для управления тостами
export const toast = {
  success: (title: string, message?: string, options?: Partial<Toast>) => {
    const newToast: Toast = {
      id: generateId(),
      type: 'success',
      title,
      message,
      duration: 5000,
      ...options
    }
    toasts.push(newToast)
    notifyListeners()
    
    // Автоматическое удаление
    if (newToast.duration && newToast.duration > 0) {
      setTimeout(() => {
        toast.dismiss(newToast.id)
      }, newToast.duration)
    }
    
    return newToast.id
  },

  error: (title: string, message?: string, options?: Partial<Toast>) => {
    const newToast: Toast = {
      id: generateId(),
      type: 'error',
      title,
      message,
      duration: 7000, // Ошибки показываем дольше
      ...options
    }
    toasts.push(newToast)
    notifyListeners()
    
    if (newToast.duration && newToast.duration > 0) {
      setTimeout(() => {
        toast.dismiss(newToast.id)
      }, newToast.duration)
    }
    
    return newToast.id
  },

  warning: (title: string, message?: string, options?: Partial<Toast>) => {
    const newToast: Toast = {
      id: generateId(),
      type: 'warning',
      title,
      message,
      duration: 6000,
      ...options
    }
    toasts.push(newToast)
    notifyListeners()
    
    if (newToast.duration && newToast.duration > 0) {
      setTimeout(() => {
        toast.dismiss(newToast.id)
      }, newToast.duration)
    }
    
    return newToast.id
  },

  info: (title: string, message?: string, options?: Partial<Toast>) => {
    const newToast: Toast = {
      id: generateId(),
      type: 'info',
      title,
      message,
      duration: 4000,
      ...options
    }
    toasts.push(newToast)
    notifyListeners()
    
    if (newToast.duration && newToast.duration > 0) {
      setTimeout(() => {
        toast.dismiss(newToast.id)
      }, newToast.duration)
    }
    
    return newToast.id
  },

  dismiss: (id: string) => {
    toasts = toasts.filter(t => t.id !== id)
    notifyListeners()
  },

  dismissAll: () => {
    toasts = []
    notifyListeners()
  }
}

// Хук для использования тостов в компонентах
export const useToast = () => {
  const [currentToasts, setCurrentToasts] = useState<Toast[]>([])

  useEffect(() => {
    const listener = (newToasts: Toast[]) => {
      setCurrentToasts(newToasts)
    }

    listeners.push(listener)
    setCurrentToasts([...toasts]) // Инициализация текущим состоянием

    return () => {
      listeners = listeners.filter(l => l !== listener)
    }
  }, [])

  return {
    toasts: currentToasts,
    toast
  }
}

// Функции-помощники для быстрого показа уведомлений
export const showSuccess = (title: string, message?: string) => {
  return toast.success(title, message)
}

export const showError = (title: string, message?: string) => {
  return toast.error(title, message)
}

export const showWarning = (title: string, message?: string) => {
  return toast.warning(title, message)
}

export const showInfo = (title: string, message?: string) => {
  return toast.info(title, message)
}