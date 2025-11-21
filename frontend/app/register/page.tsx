import RegisterForm from '@/components/Auth/RegisterForm'
import { ProtectedRoute } from '@/components/Auth/ProtectedRoute'

export default function RegisterPage() {
  return (
    <ProtectedRoute requireAuth={false} redirectTo="/">
      <div className="min-h-screen flex items-center justify-center bg-background px-4 py-12">
        <RegisterForm />
      </div>
    </ProtectedRoute>
  )
}

export const metadata = {
  title: 'Регистрация | Анализ зарплат',
  description: 'Создайте аккаунт для получения персонализированного анализа зарплат',
}