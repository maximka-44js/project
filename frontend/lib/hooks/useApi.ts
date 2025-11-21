'use client'
import { useState, useCallback } from 'react'
import { validateEmail, handleApiError } from '@/lib/utils/validation'
import { emailService, resumeService, EmailSubscriptionData } from '@/lib/api'

// Состояния для async операций
export type AsyncState<T = any> = {
  data: T | null
  loading: boolean
  error: string | null
}

// Хук для управления async состоянием
export const useAsyncState = <T = any>(initialData: T | null = null): [
  AsyncState<T>,
  {
    setLoading: (loading: boolean) => void
    setData: (data: T | null) => void
    setError: (error: string | null) => void
    reset: () => void
  }
] => {
  const [state, setState] = useState<AsyncState<T>>({
    data: initialData,
    loading: false,
    error: null
  })

  const setLoading = useCallback((loading: boolean) => {
    setState(prev => ({ ...prev, loading, error: loading ? null : prev.error }))
  }, [])

  const setData = useCallback((data: T | null) => {
    setState(prev => ({ ...prev, data, loading: false, error: null }))
  }, [])

  const setError = useCallback((error: string | null) => {
    setState(prev => ({ ...prev, error, loading: false }))
  }, [])

  const reset = useCallback(() => {
    setState({ data: initialData, loading: false, error: null })
  }, [initialData])

  return [state, { setLoading, setData, setError, reset }]
}

// Хук для подписки на email
export const useEmailSubscription = () => {
  const [state, actions] = useAsyncState()

  const subscribe = useCallback(async (email: string) => {
    // Валидация email
    const validation = validateEmail(email)
    if (!validation.isValid) {
      actions.setError(validation.error!)
      return false
    }

    actions.setLoading(true)

    try {
      const subscriptionData: EmailSubscriptionData = {
        email: email.trim().toLowerCase(),
        source: 'hero_section',
        metadata: {
          timestamp: new Date().toISOString(),
          user_agent: navigator.userAgent
        }
      }

      const result = await emailService.subscribe(subscriptionData)
      actions.setData(result)
      return true
    } catch (error) {
      const errorMessage = handleApiError(error)
      actions.setError(errorMessage)
      return false
    }
  }, [actions])

  const checkStatus = useCallback(async (email: string) => {
    actions.setLoading(true)

    try {
      const result = await emailService.checkStatus(email)
      actions.setData(result)
      return result
    } catch (error) {
      const errorMessage = handleApiError(error)
      actions.setError(errorMessage)
      return null
    }
  }, [actions])

  return {
    ...state,
    subscribe,
    checkStatus,
    reset: actions.reset
  }
}

// Хук для загрузки резюме
export const useResumeUpload = () => {
  const [state, actions] = useAsyncState()
  const [uploadProgress, setUploadProgress] = useState(0)

  const upload = useCallback(async (file: File, email?: string) => {
    actions.setLoading(true)
    setUploadProgress(0)

    try {
      // Здесь можно добавить прогресс-бар если нужно
      const result = await resumeService.uploadResume(file, email)
      actions.setData(result)
      setUploadProgress(100)
      return result
    } catch (error) {
      const errorMessage = handleApiError(error)
      actions.setError(errorMessage)
      setUploadProgress(0)
      return null
    }
  }, [actions])

  const reset = useCallback(() => {
    actions.reset()
    setUploadProgress(0)
  }, [actions])

  return {
    ...state,
    uploadProgress,
    upload,
    reset
  }
}

// Хук для получения результатов анализа
export const useSalaryAnalysis = () => {
  const [state, actions] = useAsyncState()

  const getResults = useCallback(async (analysisId: string) => {
    actions.setLoading(true)

    try {
      const result = await resumeService.getAnalysisResults(analysisId)
      actions.setData(result)
      return result
    } catch (error) {
      const errorMessage = handleApiError(error)
      actions.setError(errorMessage)
      return null
    }
  }, [actions])

  const startAnalysis = useCallback(async (uploadId: string, email?: string) => {
    actions.setLoading(true)

    try {
      const result = await resumeService.startAnalysis(uploadId, email)
      actions.setData(result)
      return result
    } catch (error) {
      const errorMessage = handleApiError(error)
      actions.setError(errorMessage)
      return null
    }
  }, [actions])

  return {
    ...state,
    getResults,
    startAnalysis,
    reset: actions.reset
  }
}