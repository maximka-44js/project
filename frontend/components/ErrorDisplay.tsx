'use client';

interface ErrorDisplayProps {
  error: string;
  onRetry: () => void;
}

export default function ErrorDisplay({ error, onRetry }: ErrorDisplayProps) {
  return (
    <div className="w-full max-w-2xl mx-auto">
      <div className="bg-red-50 rounded-xl p-8 border border-red-200 text-center space-y-6">
        {/* Error Icon */}
        <div className="w-16 h-16 mx-auto bg-red-100 rounded-full flex items-center justify-center">
          <svg className="w-8 h-8 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.732 16.5c-.77.833.192 2.5 1.732 2.5z" />
          </svg>
        </div>

        {/* Error Message */}
        <div className="space-y-2">
          <h3 className="text-xl font-semibold text-red-800">Произошла ошибка</h3>
          <p className="text-red-700 leading-relaxed max-w-md mx-auto">
            {error}
          </p>
        </div>

        {/* Retry Button */}
        <button
          onClick={onRetry}
          className="bg-red-600 text-white font-semibold py-3 px-6 rounded-xl hover:bg-red-700 transform hover:scale-105 transition-all duration-300 shadow-lg hover:shadow-xl"
        >
          Попробовать снова
        </button>
      </div>
    </div>
  );
}