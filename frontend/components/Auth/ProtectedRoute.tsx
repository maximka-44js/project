'use client'

import { useEffect } from 'react'
import { useAuth } from '@/lib/hooks/useAuth'
import { Loader2 } from 'lucide-react'

interface ProtectedRouteProps {
  children: React.ReactNode
  redirectTo?: string
  requireAuth?: boolean
  fallback?: React.ReactNode
}

export const ProtectedRoute = ({ 
  children, 
  redirectTo = '/login', 
  requireAuth = true,
  fallback 
}: ProtectedRouteProps) => {
  const { isAuthenticated, isLoading, redirectIfNotAuthenticated, redirectIfAuthenticated } = useAuth()

  useEffect(() => {
    if (!isLoading) {
      if (requireAuth && !isAuthenticated) {
        redirectIfNotAuthenticated(redirectTo)
      } else if (!requireAuth && isAuthenticated) {
        redirectIfAuthenticated('/')
      }
    }
  }, [isLoading, isAuthenticated, requireAuth, redirectTo, redirectIfNotAuthenticated, redirectIfAuthenticated])

  // Показываем загрузку, пока проверяем аутентификацию
  if (isLoading) {
    return fallback || (
      <div className="min-h-screen flex items-center justify-center">
        <Loader2 className="h-8 w-8 animate-spin text-primary" />
      </div>
    )
  }

  // Для страниц, которые требуют аутентификации
  if (requireAuth && !isAuthenticated) {
    return null // Компонент будет перенаправлен
  }

  // Для страниц, которые не должны быть доступны авторизованным пользователям
  if (!requireAuth && isAuthenticated) {
    return null // Компонент будет перенаправлен
  }

  return <>{children}</>
}

// HOC для защиты страниц, требующих аутентификации
export const withAuth = <P extends object>(
  Component: React.ComponentType<P>,
  redirectTo: string = '/login'
) => {
  const AuthenticatedComponent = (props: P) => {
    return (
      <ProtectedRoute redirectTo={redirectTo} requireAuth={true}>
        <Component {...props} />
      </ProtectedRoute>
    )
  }

  AuthenticatedComponent.displayName = `withAuth(${Component.displayName || Component.name})`
  return AuthenticatedComponent
}

// HOC для защиты страниц от авторизованных пользователей (login, register)
export const withGuest = <P extends object>(
  Component: React.ComponentType<P>,
  redirectTo: string = '/'
) => {
  const GuestComponent = (props: P) => {
    return (
      <ProtectedRoute redirectTo={redirectTo} requireAuth={false}>
        <Component {...props} />
      </ProtectedRoute>
    )
  }

  GuestComponent.displayName = `withGuest(${Component.displayName || Component.name})`
  return GuestComponent
}