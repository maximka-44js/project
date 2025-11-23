import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // Включаем standalone output для Docker
  output: 'standalone',
  
  // Оптимизации для продакшена
  compress: true,
  
  // Настройки изображений
  images: {
    unoptimized: true, // Для статического экспорта, если нужно
  },
  
  // Переменные окружения для клиента
  env: {
    NEXT_PUBLIC_UPLOAD_SERVICE_URL: process.env.NEXT_PUBLIC_UPLOAD_SERVICE_URL || 'http://localhost:8003',
    NEXT_PUBLIC_ANALYSIS_SERVICE_URL: process.env.NEXT_PUBLIC_ANALYSIS_SERVICE_URL || 'http://localhost:8004',
  },
};

export default nextConfig;
