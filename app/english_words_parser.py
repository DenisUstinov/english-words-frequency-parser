from typing import List, Dict
import requests
from bs4 import BeautifulSoup
from collections import defaultdict
from urllib.parse import urljoin, urlparse

class EnglishWordsParser:
    """
    Класс для парсинга английских слов на веб-сайтах и подсчета их частотности.

    Атрибуты:
    - initial_links (List[str]): Список начальных ссылок для парсинга.
    - output_file (str): Имя файла, в который будут сохранены результаты парсинга.
    - base_url (str): Базовый URL, извлеченный из начальных ссылок.
    - to_parse_links (List[str]): Список ссылок для парсинга.
    - parsed_links (List[str]): Список уже спарсенных ссылок.
    - word_frequency (Dict[str, int]): Словарь для хранения частоты слов.
    - current_link (str): Текущая обрабатываемая ссылка.
    """
    def __init__(self, initial_links: List[str], output_file: str):
        """
        Инициализация экземпляра класса.

        Параметры:
        - initial_links (List[str]): Список начальных ссылок для парсинга.
        - output_file (str): Имя файла, в который будут сохранены результаты парсинга.
        """
        self.base_url = self.extract_base_url(initial_links[0])
        self.to_parse_links = initial_links
        self.parsed_links = []
        self.output_file = output_file
        self.word_frequency: Dict[str, int] = defaultdict(int)

    def extract_base_url(self, url: str) -> str:
        """
        Извлечение базового URL из переданной ссылки.

        Параметры:
        - url (str): Ссылка.

        Возвращает:
        - str: Базовый URL.
        """
        parsed_url = urlparse(url)
        return f"{parsed_url.scheme}://{parsed_url.netloc}"

    def fetch_page_content(self, url: str) -> str:
        """
        Получение текстового содержания страницы по заданной ссылке.

        Параметры:
        - url (str): Ссылка.

        Возвращает:
        - str: Текстовое содержание страницы.
        """
        try:
            response = requests.get(url)
            response.raise_for_status()
            return response.text
        except requests.exceptions.RequestException as e:
            print(f"Error fetching {url}: {e}")
            return ""

    def collect_words_from_text(self, text: str) -> None:
        """
        Сбор слов и подсчет их частоты из переданного текста.

        Параметры:
        - text (str): Текст.

        """
        words = text.split()
        for word in words:
            if word.isalpha() and word.isascii():
                self.word_frequency[word.lower()] += 1

    def find_links_and_add_to_parse(self, text: str) -> None:
        """
        Поиск ссылок в тексте и добавление их в список для парсинга.

        Параметры:
        - text (str): Текст.

        """
        soup = BeautifulSoup(text, 'html.parser')
        for link in soup.find_all('a', href=True):
            absolute_url = urljoin(self.current_link, link['href'])
            self.parse_url(absolute_url)

    def parse_url(self, url: str) -> None:
        """
        Парсинг заданной ссылки и добавление в список для парсинга.

        Параметры:
        - url (str): Ссылка.

        """
        parsed_url = urlparse(url)
        if (
            not parsed_url.path or not '.' in parsed_url.path
        ) and url not in self.to_parse_links and url not in self.parsed_links and parsed_url.netloc == urlparse(self.base_url).netloc:
            self.to_parse_links.append(url)

    def sort_word_frequency(self) -> None:
        """
        Сортировка словаря с частотой слов по убыванию.
        """
        self.word_frequency = dict(sorted(self.word_frequency.items(), key=lambda item: item[1], reverse=True))

    def parse_all_links(self) -> None:
        """
        Парсинг всех ссылок в списке для парсинга.
        """
        while self.to_parse_links:
            self.current_link = self.to_parse_links.pop(0)
            page_content = self.fetch_page_content(self.current_link)

            if page_content:
                self.collect_words_from_text(page_content)
                self.find_links_and_add_to_parse(page_content)
                self.parsed_links.append(self.current_link)
                print(self.current_link, len(self.word_frequency))

    def save_to_file(self) -> None:
        """
        Сортировка словаря по частоте слов и сохранение результатов в файл.
        """
        self.sort_word_frequency()
        with open(self.output_file, 'w') as file:
            for word, frequency in self.word_frequency.items():
                file.write(f"{word}:{frequency}\n")

# Пример использования:
initial_links = ["https://go.dev"]
output_file = "go_english_words.txt"

parser = EnglishWordsParser(initial_links, output_file)
parser.parse_all_links()
parser.save_to_file()
