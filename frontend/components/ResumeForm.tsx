'use client';

import { useState } from 'react';
import { analyzeResumeFromForm } from '@/utils/api/services';
import { FormAnalysisRequest, SCHEDULE_OPTIONS, EXPERIENCE_OPTIONS, ScheduleType, ExperienceType } from '@/utils/api/types';
import { AnalysisResponse } from '@/utils/api/types';

interface ResumeFormProps {
  onAnalysisComplete: (result: AnalysisResponse) => void;
  onError: (error: string) => void;
}

export default function ResumeForm({ onAnalysisComplete, onError }: ResumeFormProps) {
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [progress, setProgress] = useState(0);
  const [statusText, setStatusText] = useState('');
  
  const [formData, setFormData] = useState<FormAnalysisRequest>({
    vacancy_nm: '',
    location: '',
    schedule: 'FIVE_ON_TWO_OFF' as ScheduleType,
    experience: 'noExperience' as ExperienceType,
    work_hours: 40,
    skills_text: '',
  });

  const [errors, setErrors] = useState<Partial<FormAnalysisRequest>>({});

  const validateForm = (): boolean => {
    const newErrors: Partial<FormAnalysisRequest> = {};

    if (!formData.vacancy_nm.trim()) {
      newErrors.vacancy_nm = 'Укажите желаемую должность';
    }

    if (!formData.location.trim()) {
      newErrors.location = 'Укажите местоположение';
    }

    if (!formData.skills_text.trim()) {
      newErrors.skills_text = 'Опишите ваши навыки и компетенции';
    }

    if (formData.work_hours < 1 || formData.work_hours > 168) {
      newErrors.work_hours = 'Рабочие часы должны быть от 1 до 168 в неделю';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!validateForm()) {
      return;
    }

    setIsAnalyzing(true);
    setProgress(0);
    setStatusText('Подготовка к анализу...');

    try {
      const result = await analyzeResumeFromForm(formData, (progress, status) => {
        setProgress(progress);
        setStatusText(status);
      });

      setStatusText('Анализ завершен!');
      onAnalysisComplete(result);
    } catch (error) {
      console.error('Ошибка при анализе формы:', error);
      onError(error instanceof Error ? error.message : 'Произошла неизвестная ошибка');
    } finally {
      setIsAnalyzing(false);
    }
  };

  const handleInputChange = (field: keyof FormAnalysisRequest, value: string | number) => {
    setFormData(prev => ({ ...prev, [field]: value }));
    
    // Убираем ошибку для поля при изменении
    if (errors[field]) {
      setErrors(prev => ({ ...prev, [field]: undefined }));
    }
  };

  return (
    <div className="w-full max-w-3xl mx-auto">
      <form onSubmit={handleSubmit} className="space-y-6">
        {/* Header */}
        <div className="text-center mb-8">
          <h2 className="text-2xl font-bold text-gray-800 mb-2">Анализ резюме через форму</h2>
          <p className="text-gray-600">Заполните данные о себе для получения анализа зарплатной вилки</p>
        </div>

        {/* Form Grid */}
        <div className="grid md:grid-cols-2 gap-6">
          {/* Vacancy Name */}
          <div className="md:col-span-2">
            <label htmlFor="vacancy_nm" className="block text-sm font-medium text-gray-700 mb-2">
              Желаемая должность *
            </label>
            <input
              type="text"
              id="vacancy_nm"
              value={formData.vacancy_nm}
              onChange={(e) => handleInputChange('vacancy_nm', e.target.value)}
              className={`w-full px-4 py-3 border rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-colors ${
                errors.vacancy_nm ? 'border-red-500' : 'border-gray-300'
              }`}
              placeholder="Например: Frontend разработчик"
              disabled={isAnalyzing}
            />
            {errors.vacancy_nm && (
              <p className="mt-1 text-sm text-red-600">{errors.vacancy_nm}</p>
            )}
          </div>

          {/* Location */}
          <div>
            <label htmlFor="location" className="block text-sm font-medium text-gray-700 mb-2">
              Местоположение *
            </label>
            <input
              type="text"
              id="location"
              value={formData.location}
              onChange={(e) => handleInputChange('location', e.target.value)}
              className={`w-full px-4 py-3 border rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-colors ${
                errors.location ? 'border-red-500' : 'border-gray-300'
              }`}
              placeholder="Например: Москва"
              disabled={isAnalyzing}
            />
            {errors.location && (
              <p className="mt-1 text-sm text-red-600">{errors.location}</p>
            )}
          </div>

          {/* Work Hours */}
          <div>
            <label htmlFor="work_hours" className="block text-sm font-medium text-gray-700 mb-2">
              Рабочих часов в неделю
            </label>
            <input
              type="number"
              id="work_hours"
              min="1"
              max="168"
              value={formData.work_hours}
              onChange={(e) => handleInputChange('work_hours', parseInt(e.target.value) || 0)}
              className={`w-full px-4 py-3 border rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-colors ${
                errors.work_hours ? 'border-red-500' : 'border-gray-300'
              }`}
              disabled={isAnalyzing}
            />
            {errors.work_hours && (
              <p className="mt-1 text-sm text-red-600">{errors.work_hours}</p>
            )}
          </div>

          {/* Schedule */}
          <div>
            <label htmlFor="schedule" className="block text-sm font-medium text-gray-700 mb-2">
              График работы
            </label>
            <select
              id="schedule"
              value={formData.schedule}
              onChange={(e) => handleInputChange('schedule', e.target.value as ScheduleType)}
              className="w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-colors"
              disabled={isAnalyzing}
            >
              {SCHEDULE_OPTIONS.map(option => (
                <option key={option.value} value={option.value}>
                  {option.label}
                </option>
              ))}
            </select>
          </div>

          {/* Experience */}
          <div>
            <label htmlFor="experience" className="block text-sm font-medium text-gray-700 mb-2">
              Опыт работы
            </label>
            <select
              id="experience"
              value={formData.experience}
              onChange={(e) => handleInputChange('experience', e.target.value as ExperienceType)}
              className="w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-colors"
              disabled={isAnalyzing}
            >
              {EXPERIENCE_OPTIONS.map(option => (
                <option key={option.value} value={option.value}>
                  {option.label}
                </option>
              ))}
            </select>
          </div>
        </div>

        {/* Skills Text */}
        <div>
          <label htmlFor="skills_text" className="block text-sm font-medium text-gray-700 mb-2">
            Навыки и компетенции *
          </label>
          <textarea
            id="skills_text"
            rows={6}
            value={formData.skills_text}
            onChange={(e) => handleInputChange('skills_text', e.target.value)}
            className={`w-full px-4 py-3 border rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-colors resize-vertical ${
              errors.skills_text ? 'border-red-500' : 'border-gray-300'
            }`}
            placeholder="Опишите ваши профессиональные навыки, технологии, которыми владеете, достижения и опыт работы..."
            disabled={isAnalyzing}
          />
          {errors.skills_text && (
            <p className="mt-1 text-sm text-red-600">{errors.skills_text}</p>
          )}
        </div>

        {/* Progress Bar */}
        {isAnalyzing && (
          <div className="space-y-3">
            <div className="w-full bg-gray-200 rounded-full h-3 overflow-hidden">
              <div 
                className="h-full bg-linear-to-r from-blue-500 to-purple-600 rounded-full transition-all duration-500 ease-out"
                style={{ width: `${progress}%` }}
              />
            </div>
            <div className="flex justify-between items-center text-sm">
              <span className="text-gray-600">{statusText}</span>
              <span className="font-semibold text-gray-700">{progress}%</span>
            </div>
          </div>
        )}

        {/* Submit Button */}
        <button
          type="submit"
          disabled={isAnalyzing}
          className={`w-full font-semibold py-4 px-6 rounded-xl transition-all duration-300 shadow-lg hover:shadow-xl ${
            isAnalyzing
              ? 'bg-gray-400 cursor-not-allowed'
              : 'bg-linear-to-r from-blue-600 to-purple-600 text-white hover:from-blue-700 hover:to-purple-700 transform hover:scale-105'
          }`}
        >
          {isAnalyzing ? 'Анализ в процессе...' : 'Анализировать резюме'}
        </button>
      </form>
    </div>
  );
}