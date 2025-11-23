'use client';

import { useState } from 'react';
import FileUpload from '@/components/FileUpload';
import AnalysisResults from '@/components/AnalysisResults';
import ErrorDisplay from '@/components/ErrorDisplay';
import { AnalysisResponse } from '@/utils/api/types';

type AppState = 'upload' | 'results' | 'error';

export default function Home() {
  const [appState, setAppState] = useState<AppState>('upload');
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
    setAppState('upload');
  };

  const handleNewAnalysis = () => {
    setAnalysisResult(null);
    setAppState('upload');
  };

  return (
    <div className="min-h-screen bg-linear-to-br from-blue-50 via-white to-purple-50">
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
          {appState === 'upload' && (
            <div className="animate-fade-in">
              <FileUpload
                onAnalysisComplete={handleAnalysisComplete}
                onError={handleError}
              />
            </div>
          )}

          {appState === 'results' && analysisResult && analysisResult.result && (
            <div className="animate-fade-in">
              <AnalysisResults
                result={analysisResult.result}
                onNewAnalysis={handleNewAnalysis}
              />
            </div>
          )}

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
