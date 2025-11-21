"use client"

import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { ChevronRight, Loader2 } from "lucide-react"
import { useState } from "react"
import { useRouter } from "next/navigation"
import { EmailSignupFormProps } from "./types"
import { useEmailSubscription } from "@/lib/hooks/useApi"
import { useToast } from "@/lib/hooks/useToast"
import { useAuth } from "@/lib/hooks/useAuth"

export default function EmailSignupForm({
  onSubmit,
  placeholder = "Введите ваш email для получения отчета",
  buttonText = "Начать анализ",
  helperText = "Бесплатный анализ • Результат за 2 минуты • Без регистрации"
}: EmailSignupFormProps) {
  const [email, setEmail] = useState("")
  const [isSuccess, setIsSuccess] = useState(false)
  const router = useRouter()
  
  const emailSubscription = useEmailSubscription()
  const { toast } = useToast()
  const { isAuthenticated, isLoading: authLoading } = useAuth()

  const handleInputClick = () => {
    if (!authLoading && !isAuthenticated) {
      toast.info("Требуется регистрация", "Для использования этой функции необходимо создать аккаунт")
      router.push('/register')
      return
    }
  }

  const handleSubmit = async () => {
    if (!authLoading && !isAuthenticated) {
      toast.info("Требуется регистрация", "Для использования этой функции необходимо создать аккаунт")
      router.push('/register')
      return
    }

    if (!email.trim()) {
      toast.error("Ошибка", "Введите email адрес")
      return
    }

    const success = await emailSubscription.subscribe(email.trim())
    
    if (success) {
      setIsSuccess(true)
      toast.success(
        "Email добавлен!", 
        "Мы отправим результат анализа на указанный адрес"
      )
      
      // Вызываем callback если передан
      if (onSubmit) {
        onSubmit(email.trim())
      }
      
      // Сбрасываем состояние успеха через 5 секунд
      setTimeout(() => {
        setIsSuccess(false)
        setEmail("")
      }, 5000)
    } else {
      toast.error("Ошибка подписки", emailSubscription.error || "Попробуйте позже")
    }
  }

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !emailSubscription.loading) {
      handleSubmit()
    }
  }

  // Показываем сообщение об успехе
  if (isSuccess) {
    return (
      <div className="space-y-4">
        <div className="p-4 bg-green-50 border border-green-200 rounded-lg">
          <div className="flex items-center">
            <div className="w-8 h-8 bg-green-100 rounded-full flex items-center justify-center mr-3">
              <ChevronRight className="w-4 h-4 text-green-600 rotate-90" />
            </div>
            <div>
              <p className="text-green-800 font-medium">Email успешно добавлен!</p>
              <p className="text-green-600 text-sm">
                Результат анализа будет отправлен на {email}
              </p>
            </div>
          </div>
        </div>
        <p className="text-sm text-gray-500">
          Теперь загрузите резюме для анализа зарплатной вилки
        </p>
      </div>
    )
  }

  return (
    <div className="space-y-4">
      <div className="flex flex-col sm:flex-row gap-3">
        <Input
          type="email"
          placeholder={placeholder}
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          onKeyPress={handleKeyPress}
          onClick={handleInputClick}
          onFocus={handleInputClick}
          disabled={emailSubscription.loading}
          className="flex-1 h-12 text-base"
        />
        <Button 
          size="lg" 
          onClick={handleSubmit}
          disabled={emailSubscription.loading || !email.trim()}
          className="h-12 px-8 bg-linear-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700 hover:shadow-lg hover:scale-105 transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed disabled:hover:shadow-none disabled:hover:scale-100"
        >
          {emailSubscription.loading ? (
            <>
              <Loader2 className="w-4 h-4 mr-2 animate-spin" />
              Отправка...
            </>
          ) : (
            <>
              {buttonText}
              <ChevronRight className="w-4 h-4 ml-2" />
            </>
          )}
        </Button>
      </div>
      
      {emailSubscription.error && (
        <p className="text-sm text-red-600">
          {emailSubscription.error}
        </p>
      )}
      
      <p className="text-sm text-gray-500">
        {helperText}
      </p>
    </div>
  )
}