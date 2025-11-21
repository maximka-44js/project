import { z } from 'zod'

// Схема для регистрации
export const registerSchema = z.object({
  email: z
    .string()
    .min(1, 'Email обязателен')
    .email('Некорректный email'),
  password: z
    .string()
    .min(8, 'Пароль должен содержать минимум 8 символов')
    .regex(
      /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[!@#$%^&*()_+\-=\[\]{};':"\\|,.<>\/?]).{8,}$/,
      'Пароль должен содержать минимум одну строчную букву, одну заглавную букву, одну цифру и один специальный символ'
    ),
  full_name: z
    .string()
    .min(2, 'Полное имя должно содержать минимум 2 символа')
    .max(100, 'Полное имя не должно превышать 100 символов')
    .regex(/^[a-zA-Zа-яА-Я\s-']+$/, 'Полное имя может содержать только буквы, пробелы, дефисы и апострофы')
})

// Схема для входа
export const loginSchema = z.object({
  email: z
    .string()
    .min(1, 'Email обязателен')
    .email('Некорректный email'),
  password: z
    .string()
    .min(1, 'Пароль обязателен')
})

// Типы данных для форм
export type RegisterFormData = z.infer<typeof registerSchema>
export type LoginFormData = z.infer<typeof loginSchema>

// Типы ответов API
export interface AuthResponse {
  access_token: string
  refresh_token: string
  token_type: string
  expires_in: number
  user: {
    id: number
    email: string
    full_name: string
    is_active: boolean
    created_at: string
    updated_at: string
  }
}

export interface TokenResponse {
  access_token: string
  refresh_token: string
  token_type: string
  expires_in: number
}
