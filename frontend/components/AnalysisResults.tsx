'use client';

import { AnalysisResult } from '@/utils/api/types';

interface AnalysisResultsProps {
  result: AnalysisResult;
  onNewAnalysis: () => void;
}

export default function AnalysisResults({ result, onNewAnalysis }: AnalysisResultsProps) {
  const { extracted_data, salary_prediction, recommendations } = result;

  const formatSalary = (amount: number, currency: string) => {
    return new Intl.NumberFormat('ru-RU').format(amount) + ' ' + currency.toUpperCase();
  };

  const getSalaryRange = () => {
    const min = salary_prediction.lowest_salary;
    const max = salary_prediction.highest_salary;
    const currency = salary_prediction.currency;
    
    if (min === max) {
      return formatSalary(min, currency);
    }
    
    return `${formatSalary(min, currency)} - ${formatSalary(max, currency)}`;
  };

  const parseSkills = (skillsText: string): string[] => {
    if (!skillsText) return [];
    
    // Попытка разделить навыки по различным разделителям
    const separators = [',', ';', '|', '\n', '•', '-'];
    let skills: string[] = [skillsText];
    
    for (const separator of separators) {
      if (skillsText.includes(separator)) {
        skills = skillsText.split(separator);
        break;
      }
    }
    
    return skills
      .map(skill => skill.trim())
      .filter(skill => skill.length > 0)
      .slice(0, 20); // Ограничиваем до 20 навыков
  };

  const skills = parseSkills(extracted_data.skills_text);

  return (
    <div className="w-full max-w-4xl mx-auto space-y-8">
      {/* Header */}
      <div className="text-center space-y-4">
        <div className="w-16 h-16 mx-auto bg-green-100 rounded-full flex items-center justify-center">
          <svg className="w-8 h-8 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
        </div>
        <h2 className="text-3xl font-bold bg-linear-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
          Анализ завершен!
        </h2>
        <p className="text-gray-600">Вот что мы смогли извлечь из вашего резюме</p>
      </div>

      {/* Salary Prediction - Main Card */}
      <div className="bg-linear-to-br from-blue-50 to-purple-50 rounded-2xl p-8 border border-blue-100 shadow-lg">
        <div className="text-center space-y-4">
          <h3 className="text-xl font-semibold text-gray-800">Примерная зарплатная вилка</h3>
          <div className="text-4xl font-bold bg-linear-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
            {getSalaryRange()}
          </div>
          <p className="text-sm text-gray-600">
            Основано на анализе рынка и ваших навыках
          </p>
        </div>
      </div>

      {/* Extracted Information Grid */}
      <div className="grid md:grid-cols-2 gap-6">
        {/* Personal Info */}
        <div className="bg-white rounded-xl p-6 shadow-lg border border-gray-100">
          <h3 className="text-lg font-semibold text-gray-800 mb-4 flex items-center">
            <svg className="w-5 h-5 text-blue-600 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
            </svg>
            Личная информация
          </h3>
          <div className="space-y-3">
            {extracted_data.vacancy_nm && (
              <div>
                <span className="text-sm text-gray-500">Желаемая позиция:</span>
                <p className="font-medium text-gray-800">{extracted_data.vacancy_nm}</p>
              </div>
            )}
            {extracted_data.location && (
              <div>
                <span className="text-sm text-gray-500">Локация:</span>
                <p className="font-medium text-gray-800">{extracted_data.location}</p>
              </div>
            )}
            {extracted_data.experience && (
              <div>
                <span className="text-sm text-gray-500">Опыт работы:</span>
                <p className="font-medium text-gray-800">{extracted_data.experience}</p>
              </div>
            )}
          </div>
        </div>

        {/* Work Preferences */}
        <div className="bg-white rounded-xl p-6 shadow-lg border border-gray-100">
          <h3 className="text-lg font-semibold text-gray-800 mb-4 flex items-center">
            <svg className="w-5 h-5 text-purple-600 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 13.255A23.931 23.931 0 0112 15c-3.183 0-6.22-.62-9-1.745M16 6V4a2 2 0 00-2-2h-4a2 2 0 00-2-2v2m8 0H8m8 0v2a2 2 0 002 2M8 6V4H6a2 2 0 00-2 2v2m0 0v8a2 2 0 002 2h2m0 0h8m0 0h2a2 2 0 002-2V8a2 2 0 00-2-2h-2" />
            </svg>
            Предпочтения по работе
          </h3>
          <div className="space-y-3">
            {extracted_data.schedule && (
              <div>
                <span className="text-sm text-gray-500">График работы:</span>
                <p className="font-medium text-gray-800">{extracted_data.schedule}</p>
              </div>
            )}
            {extracted_data.work_hours > 0 && (
              <div>
                <span className="text-sm text-gray-500">Рабочих часов:</span>
                <p className="font-medium text-gray-800">{extracted_data.work_hours} ч/неделя</p>
              </div>
            )}
            <div>
              <span className="text-sm text-gray-500">ID профессии:</span>
              <p className="font-medium text-gray-800">#{result.profession_id}</p>
            </div>
          </div>
        </div>
      </div>

      {/* Skills Section */}
      {skills.length > 0 && (
        <div className="bg-white rounded-xl p-6 shadow-lg border border-gray-100">
          <h3 className="text-lg font-semibold text-gray-800 mb-4 flex items-center">
            <svg className="w-5 h-5 text-green-600 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
            </svg>
            Навыки и компетенции
          </h3>
          <div className="flex flex-wrap gap-2">
            {skills.map((skill, index) => (
              <span
                key={index}
                className="px-3 py-1 bg-linear-to-r from-blue-100 to-purple-100 text-blue-800 rounded-full text-sm font-medium border border-blue-200"
              >
                {skill}
              </span>
            ))}
          </div>
        </div>
      )}

      {/* Raw Skills Text (if no parsed skills) */}
      {skills.length === 0 && extracted_data.skills_text && (
        <div className="bg-white rounded-xl p-6 shadow-lg border border-gray-100">
          <h3 className="text-lg font-semibold text-gray-800 mb-4 flex items-center">
            <svg className="w-5 h-5 text-green-600 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
            </svg>
            Навыки и компетенции
          </h3>
          <p className="text-gray-700 leading-relaxed">{extracted_data.skills_text}</p>
        </div>
      )}

      {/* Recommendations Section */}
      {recommendations && (
        <div className="bg-linear-to-br from-amber-50 to-orange-50 rounded-xl p-6 shadow-lg border border-amber-200">
          <h3 className="text-lg font-semibold text-gray-800 mb-4 flex items-center">
            <svg className="w-5 h-5 text-amber-600 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 3l1.917 5.983L20 9.75l-4.167.917L14.917 16.5L12 10.5 9.083 16.5 8.167 10.667 4 9.75l6.083-.767L12 3z" />
            </svg>
            Рекомендации по развитию
          </h3>
          <div className="bg-white/50 rounded-lg p-4 border border-amber-100">
            <p className="text-gray-700 leading-relaxed whitespace-pre-line text-sm">{recommendations}</p>
          </div>
        </div>
      )}

      {/* Action Button */}
      <div className="text-center pt-4">
        <button
          onClick={onNewAnalysis}
          className="bg-linear-to-r from-blue-600 to-purple-600 text-white font-semibold py-3 px-8 rounded-xl hover:from-blue-700 hover:to-purple-700 transform hover:scale-105 transition-all duration-300 shadow-lg hover:shadow-xl"
        >
          Анализировать новое резюме
        </button>
      </div>
    </div>
  );
}