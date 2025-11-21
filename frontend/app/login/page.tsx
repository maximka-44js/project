import LoginForm from '@/components/Auth/LoginForm'
import { ProtectedRoute } from '@/components/Auth/ProtectedRoute'

export default function LoginPage() {
  return (
    <ProtectedRoute requireAuth={false} redirectTo="/">
      <div className="min-h-screen flex items-center justify-center bg-background px-4 py-12">
        <LoginForm />
      </div>
    </ProtectedRoute>
  )
}

export const metadata = {
  title: 'Вход | Анализ зарплат',
  description: 'Войдите в ваш аккаунт для доступа к анализу зарплат',
}