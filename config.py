"""Конфигурация подключения к базе данных."""
from dataclasses import dataclass
from typing import Optional


@dataclass
class DatabaseConfig:
    """Конфигурация подключения к PostgreSQL."""

    dbname: str = "hh_parser"
    user: str = "postgres"
    password: str = "password"
    host: str = "localhost"
    port: int = 5432

    def get_connection_string(self) -> str:
        """Получить строку подключения к БД."""
        return f"dbname={self.dbname} user={self.user} password={self.password} host={self.host} port={self.port}"


# Список компаний для парсинга (ID компаний на hh.ru)
EMPLOYERS = [
    {"id": "1002", "name": "Yandex"},
    {"id": "1001", "name": "Ozon Tech"},
    {"id": "1005", "name": "Sber"},
    {"id": "1004", "name": "Tinkoff"},
    {"id": "1003", "name": "VK"},
]
