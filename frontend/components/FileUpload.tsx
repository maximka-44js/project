'use client';

import { useCallback, useState } from 'react';
import { analyzeResume } from '@/utils/api/services';
import { AnalysisResponse } from '@/utils/api/types';

interface FileUploadProps {
  onAnalysisComplete: (result: AnalysisResponse) => void;
  onError: (error: string) => void;
}

export default function FileUpload({ onAnalysisComplete, onError }: FileUploadProps) {
  const [isDragOver, setIsDragOver] = useState(false);
  const [isUploading, setIsUploading] = useState(false);
  const [progress, setProgress] = useState(0);
  const [statusText, setStatusText] = useState('');
  const [selectedFile, setSelectedFile] = useState<File | null>(null);

  const validateFile = (file: File): boolean => {
    const allowedTypes = ['application/pdf', 'application/msword', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document', 'text/plain'];
    const maxSize = 10 * 1024 * 1024; // 10MB

    if (!allowedTypes.includes(file.type)) {
      onError('Поддерживаются только файлы PDF, DOC, DOCX и TXT');
      return false;
    }

    if (file.size > maxSize) {
      onError('Размер файла не должен превышать 10MB');
      return false;
    }

    return true;
  };

  const handleFileSelect = useCallback((file: File) => {
    if (!validateFile(file)) return;
    
    setSelectedFile(file);
    setProgress(0);
    setStatusText('');
  }, []);

  const handleUpload = async () => {
    if (!selectedFile || isUploading) return;

    setIsUploading(true);
    setProgress(0);
    setStatusText('Подготовка к загрузке...');

    try {
      const result = await analyzeResume(selectedFile, (progress, status) => {
        setProgress(progress);
        setStatusText(status);
      });

      setStatusText('Анализ завершен!');
      onAnalysisComplete(result);
    } catch (error) {
      console.error('Ошибка при загрузке и анализе:', error);
      onError(error instanceof Error ? error.message : 'Произошла неизвестная ошибка');
    } finally {
      setIsUploading(false);
    }
  };

  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(true);
  }, []);

  const handleDragLeave = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(false);
  }, []);

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(false);
    
    const files = Array.from(e.dataTransfer.files);
    if (files.length > 0) {
      handleFileSelect(files[0]);
    }
  }, [handleFileSelect]);

  const handleFileInput = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files;
    if (files && files.length > 0) {
      handleFileSelect(files[0]);
    }
  }, [handleFileSelect]);

  return (
    <div className="w-full max-w-2xl mx-auto space-y-6">
      {/* Drag & Drop Area */}
      <div
        className={`
          relative border-2 border-dashed rounded-xl p-8 text-center transition-all duration-300 ease-in-out
          ${isDragOver 
            ? 'border-blue-500 bg-blue-50 scale-105' 
            : selectedFile 
            ? 'border-green-400 bg-green-50' 
            : 'border-gray-300 bg-gray-50 hover:border-blue-400 hover:bg-blue-50'
          }
          ${isUploading ? 'pointer-events-none opacity-70' : 'cursor-pointer'}
        `}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
        onClick={() => !isUploading && document.getElementById('fileInput')?.click()}
      >
        <input
          id="fileInput"
          type="file"
          accept=".pdf,.doc,.docx,.txt"
          onChange={handleFileInput}
          className="hidden"
          disabled={isUploading}
        />
        
        <div className="space-y-4">
          {/* Icon */}
          <div className="flex justify-center">
            {selectedFile ? (
              <div className="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center">
                <svg className="w-8 h-8 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              </div>
            ) : (
              <div className={`w-16 h-16 rounded-full flex items-center justify-center transition-colors duration-300 ${
                isDragOver ? 'bg-blue-100' : 'bg-gray-100'
              }`}>
                <svg className={`w-8 h-8 transition-colors duration-300 ${
                  isDragOver ? 'text-blue-600' : 'text-gray-600'
                }`} fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
                </svg>
              </div>
            )}
          </div>

          {/* Text */}
          <div className="space-y-2">
            {selectedFile ? (
              <>
                <h3 className="text-lg font-semibold text-green-700">Файл выбран</h3>
                <p className="text-sm text-gray-600">{selectedFile.name}</p>
                <p className="text-xs text-gray-500">
                  {(selectedFile.size / 1024 / 1024).toFixed(2)} MB
                </p>
              </>
            ) : (
              <>
                <h3 className="text-lg font-semibold text-gray-700">
                  {isDragOver ? 'Отпустите файл здесь' : 'Загрузите резюме'}
                </h3>
                <p className="text-sm text-gray-600">
                  Перетащите файл сюда или нажмите для выбора
                </p>
                <p className="text-xs text-gray-500">
                  Поддерживаются PDF, DOC, DOCX, TXT (до 10MB)
                </p>
              </>
            )}
          </div>
        </div>
      </div>

      {/* Progress Bar */}
      {isUploading && (
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

      {/* Action Button */}
      {selectedFile && !isUploading && (
        <button
          onClick={handleUpload}
          className="w-full bg-linear-to-r from-blue-600 to-purple-600 text-white font-semibold py-4 px-6 rounded-xl hover:from-blue-700 hover:to-purple-700 transform hover:scale-105 transition-all duration-300 shadow-lg hover:shadow-xl"
        >
          Анализировать резюме
        </button>
      )}

      {/* New File Button */}
      {selectedFile && !isUploading && (
        <button
          onClick={() => {
            setSelectedFile(null);
            setProgress(0);
            setStatusText('');
            const input = document.getElementById('fileInput') as HTMLInputElement;
            if (input) input.value = '';
          }}
          className="w-full bg-gray-100 text-gray-700 font-medium py-3 px-6 rounded-xl hover:bg-gray-200 transition-all duration-300"
        >
          Выбрать другой файл
        </button>
      )}
    </div>
  );
}