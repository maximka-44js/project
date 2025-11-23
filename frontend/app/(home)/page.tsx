'use client';

import { useState } from 'react';
import FileUpload from '@/components/FileUpload';
import ResumeForm from '@/components/ResumeForm';
import AnalysisResults from '@/components/AnalysisResults';
import ErrorDisplay from '@/components/ErrorDisplay';
import { AnalysisResponse } from '@/utils/api/types';

type AppState = 'method-selection' | 'file-upload' | 'form-input' | 'results' | 'error';
type AnalysisMethod = 'file' | 'form';

export default function Home() {
  const [appState, setAppState] = useState<AppState>('method-selection');
  const [analysisMethod, setAnalysisMethod] = useState<AnalysisMethod>('file');
  const [analysisResult, setAnalysisResult] = useState<AnalysisResponse | null>(null);
  const [error, setError] = useState<string>('');

  const handleAnalysisComplete = (result: AnalysisResponse) => {
    setAnalysisResult(result);
    setAppState('results');
  };

  const handleError = (errorMessage: string) => {
    setError(errorMessage);
    setAppState('error');
  };

  const handleRetry = () => {
    setError('');
    setAnalysisResult(null);
    setAppState(analysisMethod === 'file' ? 'file-upload' : 'form-input');
  };

  const handleNewAnalysis = () => {
    setAnalysisResult(null);
    setAppState('method-selection');
  };

  const handleMethodSelect = (method: AnalysisMethod) => {
    setAnalysisMethod(method);
    setAppState(method === 'file' ? 'file-upload' : 'form-input');
  };

  return (
    <div className="min-h-screen bg-linear-to-br from-blue-50 via-white to-purple-50 mt-50">
      <div className="container mx-auto px-4 py-12">
        {/* Header */}
        <div className="text-center mb-12">
          <h1 className="text-4xl md:text-5xl font-bold bg-linear-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent mb-4">
            Анализатор резюме
          </h1>
          <p className="text-lg text-gray-600 max-w-2xl mx-auto">
            Загрузите ваше резюме и получите профессиональный анализ с оценкой зарплатной вилки
          </p>
        </div>

        {/* Main Content */}
        <div className="flex justify-center">
          {/* Method Selection */}
          {appState === 'method-selection' && (
            <div className="w-full max-w-2xl mx-auto space-y-8 animate-fade-in">
              <div className="text-center mb-8">
                <h2 className="text-2xl font-bold text-gray-800 mb-4">Выберите способ анализа</h2>
                <p className="text-gray-600">Загрузите готовое резюме или заполните форму с данными</p>
              </div>
              
              <div className="grid md:grid-cols-2 gap-6">
                {/* File Upload Option */}
                <button
                  onClick={() => handleMethodSelect('file')}
                  className="p-8 border-2 border-gray-200 rounded-xl hover:border-blue-400 hover:bg-blue-50 transition-all duration-300 group text-left"
                >
                  <div className="flex flex-col items-center space-y-4">
                    <div className="w-16 h-16 bg-blue-100 rounded-full flex items-center justify-center group-hover:bg-blue-200 transition-colors duration-300">
                      <svg className="w-8 h-8 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
                      </svg>
                    </div>
                    <div className="text-center">
                      <h3 className="text-lg font-semibold text-gray-800 mb-2">Загрузить файл</h3>
                      <p className="text-sm text-gray-600">
                        Загрузите готовое резюме в формате PDF, DOC, DOCX или TXT
                      </p>
                    </div>
                  </div>
                </button>

                {/* Form Input Option */}
                <button
                  onClick={() => handleMethodSelect('form')}
                  className="p-8 border-2 border-gray-200 rounded-xl hover:border-purple-400 hover:bg-purple-50 transition-all duration-300 group text-left"
                >
                  <div className="flex flex-col items-center space-y-4">
                    <div className="w-16 h-16 bg-purple-100 rounded-full flex items-center justify-center group-hover:bg-purple-200 transition-colors duration-300">
                      <svg className="w-8 h-8 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                      </svg>
                    </div>
                    <div className="text-center">
                      <h3 className="text-lg font-semibold text-gray-800 mb-2">Заполнить форму</h3>
                      <p className="text-sm text-gray-600">
                        Введите данные о себе и своих навыках в специальной форме
                      </p>
                    </div>
                  </div>
                </button>
              </div>
            </div>
          )}

          {/* File Upload */}
          {appState === 'file-upload' && (
            <div className="w-full space-y-6 animate-fade-in">
              <div className="text-center">
                <button
                  onClick={() => setAppState('method-selection')}
                  className="text-blue-600 hover:text-blue-700 font-medium flex items-center mx-auto mb-6"
                >
                  <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
                  </svg>
                  Назад к выбору способа
                </button>
              </div>
              <FileUpload
                onAnalysisComplete={handleAnalysisComplete}
                onError={handleError}
              />
            </div>
          )}

          {/* Form Input */}
          {appState === 'form-input' && (
            <div className="w-full space-y-6 animate-fade-in">
              <div className="text-center">
                <button
                  onClick={() => setAppState('method-selection')}
                  className="text-purple-600 hover:text-purple-700 font-medium flex items-center mx-auto mb-6"
                >
                  <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
                  </svg>
                  Назад к выбору способа
                </button>
              </div>
              <ResumeForm
                onAnalysisComplete={handleAnalysisComplete}
                onError={handleError}
              />
            </div>
          )}

          {/* Results */}
          {appState === 'results' && analysisResult && analysisResult.result && (
            <div className="animate-fade-in">
              <AnalysisResults
                result={analysisResult.result}
                onNewAnalysis={handleNewAnalysis}
              />
            </div>
          )}

          {/* Error */}
          {appState === 'error' && (
            <div className="animate-fade-in">
              <ErrorDisplay
                error={error}
                onRetry={handleRetry}
              />
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="text-center mt-16 pt-8 border-t border-gray-200">
          <p className="text-sm text-gray-500">
            Анализ резюме с использованием технологий машинного обучения
          </p>
        </div>
      </div>
    </div>
  );
}
