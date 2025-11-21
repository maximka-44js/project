'use client'

import { Upload, FileText, DollarSign, Users, Loader2, CheckCircle } from "lucide-react"
import { useRouter } from "next/navigation"
import { ResumeUploadCardProps, DEFAULT_SALARY_EXAMPLES } from "./types"
import { useResumeUpload, useSalaryAnalysis } from "@/lib/hooks/useApi"
import { useToast } from "@/lib/hooks/useToast"
import { useAuth } from "@/lib/hooks/useAuth"
import { validateResumeFile, formatFileSize, formatSalaryRange } from "@/lib/utils/validation"
import { useState, useEffect } from "react"

export default function ResumeUploadCard({ 
  onFileUpload, 
  salaryExamples = DEFAULT_SALARY_EXAMPLES 
}: ResumeUploadCardProps) {
  const [uploadedFile, setUploadedFile] = useState<File | null>(null)
  const [analysisResults, setAnalysisResults] = useState<any>(null)
  const router = useRouter()
  
  const resumeUpload = useResumeUpload()
  const salaryAnalysis = useSalaryAnalysis()
  const { toast } = useToast()
  const { isAuthenticated, isLoading: authLoading } = useAuth()

  const handleFileInputClick = (event: React.MouseEvent<HTMLInputElement>) => {
    if (!authLoading && !isAuthenticated) {
      event.preventDefault()
      toast.info("Требуется регистрация", "Для загрузки резюме необходимо создать аккаунт")
      router.push('/register')
      return
    }
  }

  const handleFileChange = async (event: React.ChangeEvent<HTMLInputElement>) => {
    if (!authLoading && !isAuthenticated) {
      toast.info("Требуется регистрация", "Для загрузки резюме необходимо создать аккаунт")
      router.push('/register')
      return
    }

    const file = event.target.files?.[0]
    if (!file) return

    // Валидация файла
    const validation = validateResumeFile(file)
    if (!validation.isValid) {
      toast.error("Ошибка файла", validation.error!)
      return
    }

    // Загружаем файл
    const uploadResult = await resumeUpload.upload(file)
    
    if (uploadResult) {
      setUploadedFile(file)
      toast.success(
        "Файл загружен!", 
        `${file.name} (${formatFileSize(file.size)})`
      )

      // Вызываем callback если передан
      if (onFileUpload) {
        onFileUpload(file)
      }

      // Если есть analysis_id, запускаем получение результатов
      if (uploadResult.analysis_id) {
        pollAnalysisResults(uploadResult.analysis_id)
      }
    } else {
      toast.error("Ошибка загрузки", resumeUpload.error || "Попробуйте позже")
    }

    // Сбрасываем значение input для возможности повторной загрузки того же файла
    event.target.value = ''
  }

  // Поллинг результатов анализа
  const pollAnalysisResults = async (analysisId: string) => {
    const maxAttempts = 30 // Максимум 5 минут (30 * 10 секунд)
    let attempts = 0

    const checkResults = async () => {
      const results = await salaryAnalysis.getResults(analysisId)
      
      if (results?.status === 'completed' && results.results) {
        setAnalysisResults(results.results)
        toast.success(
          "Анализ завершен!", 
          "Результаты готовы"
        )
        return
      }
      
      if (results?.status === 'error') {
        toast.error("Ошибка анализа", results.error_message || "Попробуйте загрузить файл заново")
        return
      }

      // Продолжаем поллинг если статус 'processing'
      attempts++
      if (attempts < maxAttempts && results?.status === 'processing') {
        setTimeout(checkResults, 10000) // Проверяем каждые 10 секунд
      } else if (attempts >= maxAttempts) {
        toast.warning("Анализ занимает больше времени", "Результаты будут отправлены на email")
      }
    }

    checkResults()
  }

  return (
    <div className="relative">
      <div className="bg-white rounded-2xl shadow-2xl p-8 border border-gray-200 relative overflow-hidden">
        {/* Card background decoration */}
        <div className="absolute top-0 right-0 w-32 h-32 bg-linear-to-br from-blue-400/20 to-indigo-400/20 rounded-full blur-2xl" />
        
        <div className="relative space-y-6">
          <div className="text-center">
            <div className="w-16 h-16 bg-linear-to-br from-blue-600 to-indigo-600 rounded-2xl flex items-center justify-center mx-auto mb-4">
              {resumeUpload.loading ? (
                <Loader2 className="w-8 h-8 text-white animate-spin" />
              ) : uploadedFile ? (
                <CheckCircle className="w-8 h-8 text-white" />
              ) : (
                <Upload className="w-8 h-8 text-white" />
              )}
            </div>
            <h3 className="text-xl font-semibold text-gray-900 mb-2">
              {uploadedFile ? 'Файл загружен' : 'Загрузите ваше резюме'}
            </h3>
            <p className="text-gray-600">
              {uploadedFile ? uploadedFile.name : 'Поддерживаются форматы PDF, DOC, DOCX'}
            </p>
          </div>

          {/* Upload area или статус */}
          {!uploadedFile ? (
            <label className="block" onClick={() => {
              if (!authLoading && !isAuthenticated) {
                toast.info("Требуется регистрация", "Для загрузки резюме необходимо создать аккаунт")
                router.push('/register')
              }
            }}>
              <input
                type="file"
                accept=".pdf,.doc,.docx,.txt"
                onChange={handleFileChange}
                onClick={handleFileInputClick}
                disabled={resumeUpload.loading}
                className="hidden"
              />
              <div className={`border-2 border-dashed rounded-lg p-8 text-center transition-colors cursor-pointer group ${
                resumeUpload.loading 
                  ? 'border-gray-200 cursor-not-allowed' 
                  : 'border-gray-300 hover:border-blue-400'
              }`}>
                <div className="space-y-3">
                  <div className={`w-12 h-12 rounded-lg flex items-center justify-center mx-auto transition-colors ${
                    resumeUpload.loading 
                      ? 'bg-gray-100' 
                      : 'bg-gray-100 group-hover:bg-blue-50'
                  }`}>
                    {resumeUpload.loading ? (
                      <Loader2 className="w-6 h-6 text-gray-400 animate-spin" />
                    ) : (
                      <FileText className="w-6 h-6 text-gray-400 group-hover:text-blue-500 transition-colors" />
                    )}
                  </div>
                  <div>
                    <p className="font-medium text-gray-900">
                      {resumeUpload.loading 
                        ? 'Загрузка...' 
                        : (!authLoading && !isAuthenticated 
                          ? 'Зарегистрируйтесь для загрузки' 
                          : 'Нажмите для загрузки')}
                    </p>
                    <p className="text-sm text-gray-500">
                      {resumeUpload.loading 
                        ? 'Пожалуйста, подождите' 
                        : (!authLoading && !isAuthenticated 
                          ? 'Создайте аккаунт, чтобы начать анализ' 
                          : 'или перетащите файл сюда')}
                    </p>
                  </div>
                  <p className="text-xs text-gray-400">
                    Максимальный размер файла: 10MB
                  </p>
                </div>
              </div>
            </label>
          ) : (
            <div className="bg-blue-50 border border-blue-200 rounded-lg p-6">
              <div className="flex items-center justify-between">
                <div className="flex items-center">
                  <CheckCircle className="w-5 h-5 text-blue-600 mr-2" />
                  <span className="text-blue-800 font-medium">Файл успешно загружен</span>
                </div>
                <button
                  onClick={() => {
                    setUploadedFile(null)
                    setAnalysisResults(null)
                    resumeUpload.reset()
                  }}
                  className="text-blue-600 hover:text-blue-800 text-sm underline"
                >
                  Загрузить другой
                </button>
              </div>
              <p className="text-blue-600 text-sm mt-2">
                {salaryAnalysis.loading 
                  ? 'Анализируем ваше резюме...' 
                  : analysisResults 
                  ? 'Анализ завершен!' 
                  : 'Анализ запущен, результаты будут готовы через несколько минут'
                }
              </p>
            </div>
          )}

          {/* Results or Example */}
          <div className="bg-gray-50 rounded-lg p-6 space-y-4">
            <h4 className="font-medium text-gray-900 flex items-center">
              <DollarSign className="w-4 h-4 mr-2 text-green-600" />
              {analysisResults ? 'Ваши результаты' : 'Пример результата'}
            </h4>
            
            <div className="space-y-3">
              {analysisResults ? (
                analysisResults.position_levels?.map((level: any, index: number) => (
                  <div key={index} className="flex justify-between items-center">
                    <span className="text-sm text-gray-600">{level.level}</span>
                    <div className="text-right">
                      <span className="font-medium">
                        {formatSalaryRange(level.salary_min, level.salary_max, level.currency)}
                      </span>
                      <span className="text-xs text-gray-500 block">
                        {Math.round(level.confidence * 100)}% точность
                      </span>
                    </div>
                  </div>
                ))
              ) : (
                salaryExamples.map((example, index) => (
                  <div key={index} className="flex justify-between items-center">
                    <span className="text-sm text-gray-600">{example.level}</span>
                    <span className="font-medium">{example.range}</span>
                  </div>
                ))
              )}
            </div>
            
            <div className="pt-3 border-t border-gray-200">
              <p className="text-xs text-gray-500">
                {analysisResults
                  ? `* Проанализировано ${analysisResults.market_data?.total_vacancies_analyzed || 0} вакансий`
                  : '* Данные основаны на анализе 10,000+ вакансий за последние 3 месяца'
                }
              </p>
            </div>
          </div>

          {/* Error display */}
          {(resumeUpload.error || salaryAnalysis.error) && (
            <div className="bg-red-50 border border-red-200 rounded-lg p-4">
              <p className="text-red-800 text-sm">
                {resumeUpload.error || salaryAnalysis.error}
              </p>
            </div>
          )}
        </div>
      </div>

      {/* Floating elements */}
      <div className="absolute -top-4 -right-4 w-24 h-24 bg-yellow-400 rounded-full flex items-center justify-center shadow-lg">
        <span className="text-2xl">💰</span>
      </div>
      
      <div className="absolute -bottom-4 -left-4 w-20 h-20 bg-green-400 rounded-full flex items-center justify-center shadow-lg">
        <Users className="w-8 h-8 text-white" />
      </div>
    </div>
  )
}