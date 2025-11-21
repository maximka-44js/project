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
import { loginSchema, LoginFormData } from '@/lib/validation/auth'
import { authService } from '@/lib/api/services'
import { useAuth } from '@/lib/hooks/useAuth'

export default function LoginForm() {
  const [isLoading, setIsLoading] = useState(false)
  const [showPassword, setShowPassword] = useState(false)
  const router = useRouter()
  const { login, redirectIfAuthenticated, isLoading: authLoading } = useAuth()

  const {
    register,
    handleSubmit,
    formState: { errors },
    reset
  } = useForm<LoginFormData>({
    resolver: zodResolver(loginSchema)
  })

  // Перенаправляем авторизованных пользователей на главную страницу
  useEffect(() => {
    if (!authLoading) {
      redirectIfAuthenticated('/')
    }
  }, [authLoading, redirectIfAuthenticated])

  const onSubmit = async (data: LoginFormData) => {
    setIsLoading(true)
    
    try {
      const response = await authService.login(data)
      
      // Используем хук аутентификации для сохранения данных
      login(response.user, {
        access_token: response.access_token,
        refresh_token: response.refresh_token
      })
      
      toast.success(
        "Вход выполнен успешно!",
        `Добро пожаловать, ${response.user.full_name}!`
      )
      
      // Перенаправляем на главную страницу
      router.push('/')
      
    } catch (error: any) {
      console.error('Login error:', error)
      
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
      
      // Обработка ошибки неверных учетных данных
      if (error.response?.status === 401) {
        toast.error(
          "Ошибка входа",
          "Неверный email или пароль. Проверьте правильность введенных данных."
        )
        return
      }
      
      toast.error(
        "Ошибка входа",
        error.response?.data?.message || "Произошла ошибка при входе в систему. Попробуйте снова."
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
        <h1 className="text-3xl font-bold text-foreground mb-2">Вход в аккаунт</h1>
        <p className="text-muted-foreground">
          Введите ваши учетные данные для входа
        </p>
      </div>

      <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
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
              Выполняется вход...
            </>
          ) : (
            "Войти"
          )}
        </Button>
      </form>

      <div className="mt-6 text-center">
        <p className="text-sm text-muted-foreground">
          Нет аккаунта?{' '}
          <Link 
            href="/register" 
            className="text-primary hover:underline font-medium"
          >
            Зарегистрироваться
          </Link>
        </p>
      </div>
    </div>
  )
}