"""Модуль для конфигурации подключения к базе данных."""
import os
from dotenv import load_dotenv

# Загрузка переменных окружения из файла .env
load_dotenv()


class Config:
    """Класс конфигурации с параметрами подключения к БД."""

    DB_NAME: str = os.getenv('DB_NAME', 'hh_vacancies')
    DB_USER: str = os.getenv('DB_USER', 'postgres')
    DB_PASSWORD: str = os.getenv('DB_PASSWORD')
    DB_HOST: str = os.getenv('DB_HOST', 'localhost')
    DB_PORT: str = os.getenv('DB_PORT', '5432')

    @classmethod
    def get_db_params(cls) -> dict:
        """
        Получение параметров подключения к БД.

        Returns:
            dict: Словарь с параметрами подключения
        """
        return {
            'dbname': cls.DB_NAME,
            'user': cls.DB_USER,
            'password': cls.DB_PASSWORD,
            'host': cls.DB_HOST,
            'port': cls.DB_PORT
        }
