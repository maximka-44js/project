import pandas as pd
import os
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import re
from typing import Optional


class ProfessionMatcher:
    """Класс для поиска профессий с использованием векторизации."""
    
    def __init__(self, csv_path: Optional[str] = None):
        if csv_path is None:
            csv_path = os.path.join(os.path.dirname(__file__), 'data', 'professions.csv')
        
        self.csv_path = csv_path
        self.df = None
        self.vectorizer = None
        self.profession_vectors = None
        self._load_data()
    
    def _load_data(self):
        """Загружает данные и создает векторы для профессий."""
        # Загружаем данные
        self.df = pd.read_csv(self.csv_path)
        
        # Нормализуем названия профессий
        normalized_professions = [
            self.normalize_string(str(profession)) 
            for profession in self.df['vacancy_nm']
        ]
        
        # Создаем TF-IDF vectorizer
        self.vectorizer = TfidfVectorizer(
            lowercase=True,
            stop_words=None,  # Можно добавить русские стоп-слова
            ngram_range=(1, 2),  # Учитываем биграммы
            max_features=5000,
            analyzer='word',
            token_pattern=r'\b\w+\b'
        )
        
        # Векторизуем все профессии
        self.profession_vectors = self.vectorizer.fit_transform(normalized_professions)
    
    def find_profession_id(self, profession_name: str) -> int:
        """
        Находит наиболее вероятный profession_id по названию профессии 
        с использованием векторизации.
        
        Args:
            profession_name (str): Название профессии для поиска
            
        Returns:
            int: profession_id наиболее подходящей профессии
        """
        # Нормализуем входную строку
        normalized_query = self.normalize_string(profession_name)
        
        # Векторизуем запрос
        query_vector = self.vectorizer.transform([normalized_query])
        
        # Вычисляем косинусное сходство
        similarities = cosine_similarity(query_vector, self.profession_vectors).flatten()
        
        # Находим индекс с максимальным сходством
        best_match_index = np.argmax(similarities)
        
        # Возвращаем соответствующий profession_id
        return int(self.df.iloc[best_match_index]['profession_id'])
    
    def find_top_matches(self, profession_name: str, top_k: int = 5) -> list:
        """
        Находит топ-K наиболее похожих профессий.
        
        Args:
            profession_name (str): Название профессии для поиска
            top_k (int): Количество топ результатов
            
        Returns:
            list: Список кортежей (profession_id, similarity_score, profession_name)
        """
        # Нормализуем входную строку
        normalized_query = self.normalize_string(profession_name)
        
        # Векторизуем запрос
        query_vector = self.vectorizer.transform([normalized_query])
        
        # Вычисляем косинусное сходство
        similarities = cosine_similarity(query_vector, self.profession_vectors).flatten()
        
        # Получаем топ-K индексов
        top_indices = np.argsort(similarities)[::-1][:top_k]
        
        # Формируем результат
        results = []
        for idx in top_indices:
            results.append((
                int(self.df.iloc[idx]['profession_id']),
                float(similarities[idx]),
                str(self.df.iloc[idx]['vacancy_nm'])
            ))
        
        return results
    
    @staticmethod
    def normalize_string(text: str) -> str:
        """
        Нормализует строку для лучшего сравнения.
        
        Args:
            text (str): Исходная строка
            
        Returns:
            str: Нормализованная строка
        """
        # Приводим к нижнему регистру
        text = text.lower()
        
        # Убираем лишние пробелы и некоторые знаки препинания
        text = re.sub(r'[^\w\s-/]', ' ', text)  # Оставляем дефисы и слеши
        text = re.sub(r'\s+', ' ', text)
        text = text.strip()
        
        return text


# Глобальный экземпляр для быстрого доступа
_matcher = None


def get_matcher() -> ProfessionMatcher:
    """Получает глобальный экземпляр ProfessionMatcher (Singleton pattern)."""
    global _matcher
    if _matcher is None:
        _matcher = ProfessionMatcher()
    return _matcher


def find_profession_id(profession_name: str) -> int:
    """
    Находит наиболее вероятный profession_id по названию профессии 
    с использованием векторизации.
    
    Args:
        profession_name (str): Название профессии для поиска
        
    Returns:
        int: profession_id наиболее подходящей профессии
    """
    matcher = get_matcher()
    return matcher.find_profession_id(profession_name)


# Пример использования:
if __name__ == "__main__":
    # Тестируем функцию
    test_professions = [
        "программист",
        "автомойщик", 
        "агент недвижимости",
        "менеджер",
        "разработчик",
        "python разработчик",
        "data scientist"
    ]
    
    matcher = get_matcher()
    
    for profession in test_professions:
        profession_id = find_profession_id(profession)
        print(f"Профессия: '{profession}' -> profession_id: {profession_id}")
        
        # Показываем топ-3 наиболее похожих профессий
        top_matches = matcher.find_top_matches(profession, top_k=3)
        print("  Топ-3 похожих:")
        for pid, score, name in top_matches:
            print(f"    {pid}: {name} (сходство: {score:.3f})")
        print()
