"use client"

import { Badge } from "@/components/ui/badge"
import { TrendingUp, FileText, BarChart3, Target } from "lucide-react"
import BackgroundDecorations from "./BackgroundDecorations"
import FeatureCard from "./FeatureCard"
import EmailSignupForm from "./EmailSignupForm"
import StatsSection from "./StatsSection"
import ResumeUploadCard from "./ResumeUploadCard"

export default function HeroSection() {
  const features = [
    {
      icon: FileText,
      title: "Анализ резюме",
      description: "ИИ анализ навыков",
      iconBgColor: "bg-blue-100",
      iconColor: "text-blue-600"
    },
    {
      icon: BarChart3,
      title: "Рыночные данные",
      description: "Актуальная статистика",
      iconBgColor: "bg-green-100",
      iconColor: "text-green-600"
    },
    {
      icon: Target,
      title: "Персональный отчет",
      description: "Детальный анализ",
      iconBgColor: "bg-purple-100",
      iconColor: "text-purple-600"
    }
  ]

  const stats = [
    { value: "50K+", label: "Проанализированных резюме" },
    { value: "95%", label: "Точность прогнозов" },
    { value: "2000+", label: "Компаний в базе" }
  ]

  const handleEmailSubmit = (email: string) => {
    console.log("Email submitted:", email)
    // Здесь будет логика отправки email
  }

  const handleFileUpload = (file: File) => {
    console.log("File uploaded:", file.name)
    // Здесь будет логика загрузки файла
  }

  return (
    <section className="min-h-screen bg-linear-to-br from-slate-50 via-blue-50 to-indigo-50 relative overflow-hidden">
      <BackgroundDecorations />

      <div className="relative container mx-auto px-4 py-20 lg:py-32">
        <div className="grid lg:grid-cols-2 gap-12 items-center">
          {/* Left content */}
          <div className="space-y-8">
            <div className="space-y-4">
              <Badge variant="secondary" className="bg-blue-100 text-blue-700 hover:bg-blue-200">
                <TrendingUp className="w-4 h-4 mr-2" />
                Анализ рынка труда
              </Badge>
              
              <h1 className="text-4xl lg:text-6xl font-bold text-gray-900 leading-tight">
                Узнайте свою{" "}
                <span className="bg-linear-to-r from-blue-600 to-indigo-600 bg-clip-text text-transparent">
                  рыночную стоимость
                </span>
              </h1>
              
              <p className="text-xl text-gray-600 leading-relaxed">
                Загрузите резюме и получите персональный анализ зарплатной вилки 
                на основе ваших навыков, опыта и текущих тенденций рынка труда
              </p>
            </div>

            {/* Features */}
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
              {features.map((feature, index) => (
                <FeatureCard key={index} {...feature} />
              ))}
            </div>

            {/* Email Signup Form */}
            <EmailSignupForm onSubmit={handleEmailSubmit} />

            {/* Stats */}
            <StatsSection stats={stats} />
          </div>

          {/* Right content - Resume Upload Card */}
          <ResumeUploadCard onFileUpload={handleFileUpload} />
        </div>
      </div>
    </section>
  )
}
