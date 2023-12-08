from typing import Dict, List
import nltk
from nltk import pos_tag
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer
from nltk.corpus import wordnet

nltk.download('punkt')
nltk.download('stopwords')
nltk.download('averaged_perceptron_tagger')
nltk.download('wordnet')

class PartOfSpeechAnalyzer:
    def __init__(self, file_path: str, min_frequency: int, allowed_parts_of_speech: List[str]):
        """
        Инициализация анализатора частей речи.

        Параметры:
        - file_path (str): Путь к текстовому файлу с данными о частоте слов.
        - min_frequency (int): Минимальный порог частоты для включения слов.
        - allowed_parts_of_speech (List[str]): Список разрешенных частей речи для фильтрации.
        """
        self.file_path = file_path
        self.min_frequency = min_frequency
        self.allowed_parts_of_speech = allowed_parts_of_speech
        self.word_frequency_dict: Dict[str, int] = {}
        self.lemmatizer = WordNetLemmatizer()

    def process_file(self) -> None:
        """
        Обработка входного файла и заполнение словаря частоты слов.
        """
        with open(self.file_path, 'r') as file:
            for line in file:
                word, frequency = line.strip().split(':')
                frequency = int(frequency)
                if frequency > self.min_frequency:
                    words = word_tokenize(word)  # Токенизация слов в каждой строке
                    self.word_frequency_dict[' '.join(words)] = frequency  # Сохранение токенизированного слова и его частоты

    def lemmatize_words(self) -> None:
        """
        Лемматизация слов в self.word_frequency_dict.
        """
        self.word_frequency_dict = {self.lemmatizer.lemmatize(word): freq for word, freq in self.word_frequency_dict.items()}

    def is_valid_english_word(self, word: str) -> bool:
        """
        Проверка, является ли слово допустимым английским словом.

        Параметры:
        - word (str): Слово для проверки.

        Возвращает:
        - bool: True, если слово допустимо; False в противном случае.
        """
        synsets = wordnet.synsets(word)
        return len(synsets) > 0

    def filter_stop_words(self) -> None:
        """
        Фильтрация стоп-слов из self.word_frequency_dict.
        """
        stop_words = set(stopwords.words('english'))
        self.word_frequency_dict = {word: freq for word, freq in self.word_frequency_dict.items() if word.lower() not in stop_words}

    def filter_valid_english_words(self) -> None:
        """
        Фильтрация недопустимых английских слов из self.word_frequency_dict.
        """
        self.word_frequency_dict = {word: freq for word, freq in self.word_frequency_dict.items() if len(word) > 1 and self.is_valid_english_word(word)}

    def filter_by_part_of_speech(self) -> None:
        """
        Фильтрация слов на основе разрешенных частей речи в self.word_frequency_dict.
        """
        filtered_words: Dict[str, int] = {}

        for word, frequency in self.word_frequency_dict.items():
            words = word_tokenize(word)
            lemmatizer = WordNetLemmatizer()
            lemmatized_words = [lemmatizer.lemmatize(w) for w in words]
            pos_tags = pos_tag(lemmatized_words)

            if any(tag[1] in self.allowed_parts_of_speech for tag in pos_tags):
                filtered_words[word] = frequency

        self.word_frequency_dict = filtered_words

    def sort_and_remove_duplicates(self) -> None:
        """
        Сортировка и удаление дубликатов в self.word_frequency_dict.
        """
        sorted_dict = {k: v for k, v in sorted(self.word_frequency_dict.items(), key=lambda item: item[1], reverse=True)}
        self.word_frequency_dict = {k: sorted_dict[k] for k in sorted_dict if k}

    def save_to_file(self, output_file: str) -> None:
        """
        Сохранение отсортированного и без дубликатов словаря частот слов в текстовый файл.

        Параметры:
        - output_file (str): Путь к выходному текстовому файлу.
        """
        self.sort_and_remove_duplicates()
        with open(output_file, 'w') as file:
            for word, frequency in self.word_frequency_dict.items():
                file.write(f"{word}:{frequency}\n")

# Пример использования класса
file_path = 'go_english_words.txt'
min_frequency = 1000
allowed_parts_of_speech = ['NN', 'VB', 'IN', 'CC', 'PRP']
output_file = 'output.txt'

analyzer = PartOfSpeechAnalyzer(file_path, min_frequency, allowed_parts_of_speech)
analyzer.process_file()
# analyzer.filter_stop_words()
analyzer.filter_valid_english_words()
analyzer.lemmatize_words()
analyzer.filter_by_part_of_speech()
analyzer.save_to_file(output_file)
