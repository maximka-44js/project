import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import re
import pickle
import os


def get_profession_id(data_path, model_path, profession_name, min_confidence=0.1):
    """
    Универсальная функция для определения profession_id по названию профессии
    
    Args:
        profession_name (str): Название профессии
        min_confidence (float): Минимальная уверенность (при меньшей возвращает 40)
        data_path (str): Путь к CSV файлу с данными
        model_path (str): Путь к файлу модели
    
    Returns:
        int: profession_id (40 при низкой уверенности)
    """
    
    # Глобальные переменные для кэширования модели
    if not hasattr(get_profession_id, '_cache'):
        get_profession_id._cache = {}
    
    cache_key = f"{data_path}_{model_path}"
    
    # Если модель уже загружена, используем кэш
    if cache_key in get_profession_id._cache:
        vectorizer, profession_vectors, profession_data = get_profession_id._cache[cache_key]
    else:
        # Функция предобработки текста
        def preprocess_text(text):
            if pd.isna(text):
                return ""
            text = str(text).lower()
            text = re.sub(r'[^\w\s\-]', ' ', text)
            text = re.sub(r'\s+', ' ', text)
            return text.strip()
        
        try:
            # Пытаемся загрузить готовую модель
            with open(model_path, 'rb') as f:
                model_data = pickle.load(f)
            vectorizer = model_data['vectorizer']
            profession_vectors = model_data['profession_vectors'] 
            profession_data = model_data['profession_data']
            
        except FileNotFoundError:
            # Создаем модель из CSV
            if not os.path.exists(data_path):
                raise FileNotFoundError(f"Файл данных не найден: {data_path}")
                
            df = pd.read_csv(data_path)
            df = df[df['profession_id'] != 40]  # Исключаем ID=40 из обучения
            df['vacancy_clean'] = df['vacancy_nm'].apply(preprocess_text)
            df = df[df['vacancy_clean'].str.len() > 0]
            
            vectorizer = TfidfVectorizer(
                max_features=5000,
                ngram_range=(1, 2),
                min_df=2,
                max_df=0.8
            )
            
            profession_vectors = vectorizer.fit_transform(df['vacancy_clean'])
            profession_data = df[['vacancy_nm', 'profession_id']].copy()
            
            # Сохраняем модель для следующих использований
            model_data = {
                'vectorizer': vectorizer,
                'profession_vectors': profession_vectors,
                'profession_data': profession_data
            }
            with open(model_path, 'wb') as f:
                pickle.dump(model_data, f)
        
        # Кэшируем модель
        get_profession_id._cache[cache_key] = (vectorizer, profession_vectors, profession_data)
    
    # Предобработка запроса
    def preprocess_text(text):
        if pd.isna(text):
            return ""
        text = str(text).lower()
        text = re.sub(r'[^\w\s\-]', ' ', text)
        text = re.sub(r'\s+', ' ', text)
        return text.strip()
    
    query_clean = preprocess_text(profession_name)
    query_vector = vectorizer.transform([query_clean])
    
    # Поиск наиболее похожего
    similarities = cosine_similarity(query_vector, profession_vectors).flatten()
    best_idx = similarities.argmax()
    best_similarity = similarities[best_idx]
    
    # Если уверенность слишком низкая, возвращаем 40
    if best_similarity < min_confidence:
        return 40
    
    return int(profession_data.iloc[best_idx]['profession_id'])




