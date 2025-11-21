import { LucideIcon } from "lucide-react"

// Общие типы для Hero секции
export interface Feature {
  icon: LucideIcon
  title: string
  description: string
  iconBgColor: string
  iconColor: string
}

export interface StatItem {
  value: string
  label: string
}

export interface SalaryExample {
  level: string
  range: string
}

// Пропсы для компонентов
export interface FeatureCardProps {
  icon: LucideIcon
  title: string
  description: string
  iconBgColor: string
  iconColor: string
}

export interface StatsSectionProps {
  stats: StatItem[]
}

export interface EmailSignupFormProps {
  onSubmit?: (email: string) => void
  placeholder?: string
  buttonText?: string
  helperText?: string
}

export interface ResumeUploadCardProps {
  onFileUpload?: (file: File) => void
  salaryExamples?: SalaryExample[]
}

// Константы (иконы будут импортированы в компонентах)
export const DEFAULT_FEATURE_CONFIG = [
  {
    title: "Анализ резюме",
    description: "ИИ анализ навыков",
    iconBgColor: "bg-blue-100",
    iconColor: "text-blue-600"
  },
  {
    title: "Рыночные данные", 
    description: "Актуальная статистика",
    iconBgColor: "bg-green-100",
    iconColor: "text-green-600"
  },
  {
    title: "Персональный отчет",
    description: "Детальный анализ", 
    iconBgColor: "bg-purple-100",
    iconColor: "text-purple-600"
  }
]

export const DEFAULT_STATS: StatItem[] = [
  { value: "50K+", label: "Проанализированных резюме" },
  { value: "95%", label: "Точность прогнозов" },
  { value: "2000+", label: "Компаний в базе" }
]

export const DEFAULT_SALARY_EXAMPLES: SalaryExample[] = [
  { level: "Junior Developer", range: "80K - 120K ₽" },
  { level: "Middle Developer", range: "150K - 250K ₽" },
  { level: "Senior Developer", range: "300K - 500K ₽" }
]