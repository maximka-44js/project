"use client"

import { useState, useEffect } from 'react'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { useRouter } from 'next/navigation'
import Link from 'next/link'
import { Eye, EyeOff, Loader2 } from 'lucide-react'

import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { toast } from '@/lib/hooks/useToast'
import { registerSchema, RegisterFormData } from '@/lib/validation/auth'
import { authService } from '@/lib/api/services'
import { useAuth } from '@/lib/hooks/useAuth'

export default function RegisterForm() {
  const [isLoading, setIsLoading] = useState(false)
  const [showPassword, setShowPassword] = useState(false)
  const router = useRouter()
  const { login, redirectIfAuthenticated, isLoading: authLoading } = useAuth()

  const {
    register,
    handleSubmit,
    formState: { errors },
    reset
  } = useForm<RegisterFormData>({
    resolver: zodResolver(registerSchema)
  })

  // Перенаправляем авторизованных пользователей на главную страницу
  useEffect(() => {
    if (!authLoading) {
      redirectIfAuthenticated('/')
    }
  }, [authLoading, redirectIfAuthenticated])

  const onSubmit = async (data: RegisterFormData) => {
    setIsLoading(true)
    
    try {
      const response = await authService.register(data)
      
      // Используем хук аутентификации для сохранения данных
      login(response.user, {
        access_token: response.access_token,
        refresh_token: response.refresh_token
      })
      
      toast.success(
        "Регистрация успешна!",
        "Добро пожаловать в наш сервис анализа зарплат."
      )
      
      // Перенаправляем на главную страницу
      router.push('/')
      
    } catch (error: any) {
      console.error('Registration error:', error)
      
      // Обработка ошибок валидации от API
      if (error.response?.status === 422) {
        const validationErrors = error.response.data?.detail
        if (validationErrors && Array.isArray(validationErrors)) {
          validationErrors.forEach((err: any) => {
            if (err.msg) {
              toast.error("Ошибка валидации", err.msg)
            }
          })
          return
        }
      }
      
      toast.error(
        "Ошибка регистрации",
        error.response?.data?.message || "Произошла ошибка при регистрации. Попробуйте снова."
      )
    } finally {
      setIsLoading(false)
    }
  }

  // Показываем загрузку, пока проверяем статус аутентификации
  if (authLoading) {
    return (
      <div className="w-full max-w-md mx-auto flex justify-center items-center py-12">
        <Loader2 className="h-8 w-8 animate-spin text-primary" />
      </div>
    )
  }

  return (
    <div className="w-full max-w-md mx-auto">
      <div className="text-center mb-8">
        <h1 className="text-3xl font-bold text-foreground mb-2">Создать аккаунт</h1>
        <p className="text-muted-foreground">
          Заполните данные для регистрации
        </p>
      </div>

      <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
        <div className="space-y-2">
          <label htmlFor="full_name" className="text-sm font-medium text-foreground">
            Полное имя
          </label>
          <Input
            id="full_name"
            type="text"
            placeholder="Введите ваше полное имя"
            {...register('full_name')}
            aria-invalid={!!errors.full_name}
            className={errors.full_name ? 'border-destructive' : ''}
          />
          {errors.full_name && (
            <p className="text-sm text-destructive">{errors.full_name.message}</p>
          )}
        </div>

        <div className="space-y-2">
          <label htmlFor="email" className="text-sm font-medium text-foreground">
            Email
          </label>
          <Input
            id="email"
            type="email"
            placeholder="Введите ваш email"
            {...register('email')}
            aria-invalid={!!errors.email}
            className={errors.email ? 'border-destructive' : ''}
          />
          {errors.email && (
            <p className="text-sm text-destructive">{errors.email.message}</p>
          )}
        </div>

        <div className="space-y-2">
          <label htmlFor="password" className="text-sm font-medium text-foreground">
            Пароль
          </label>
          <div className="relative">
            <Input
              id="password"
              type={showPassword ? "text" : "password"}
              placeholder="Введите пароль"
              {...register('password')}
              aria-invalid={!!errors.password}
              className={errors.password ? 'border-destructive pr-10' : 'pr-10'}
            />
            <button
              type="button"
              onClick={() => setShowPassword(!showPassword)}
              className="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground transition-colors"
            >
              {showPassword ? (
                <EyeOff className="h-4 w-4" />
              ) : (
                <Eye className="h-4 w-4" />
              )}
            </button>
          </div>
          {errors.password && (
            <p className="text-sm text-destructive">{errors.password.message}</p>
          )}
        </div>

        <Button
          type="submit"
          className="w-full h-11"
          disabled={isLoading}
        >
          {isLoading ? (
            <>
              <Loader2 className="mr-2 h-4 w-4 animate-spin" />
              Создание аккаунта...
            </>
          ) : (
            "Создать аккаунт"
          )}
        </Button>
      </form>

      <div className="mt-6 text-center">
        <p className="text-sm text-muted-foreground">
          Уже есть аккаунт?{' '}
          <Link 
            href="/login" 
            className="text-primary hover:underline font-medium"
          >
            Войти
          </Link>
        </p>
      </div>
    </div>
  )
}