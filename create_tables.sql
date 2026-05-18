-- create_tables.sql
-- Таблица для работодателей
CREATE TABLE IF NOT EXISTS employers (
    employer_id INT PRIMARY KEY,
    employer_name VARCHAR(255) NOT NULL,
    employer_url TEXT,
    alternate_url TEXT,
    vacancies_url TEXT,
    open_vacancies INT
);

-- Таблица для вакансий
CREATE TABLE IF NOT EXISTS vacancies (
    vacancy_id VARCHAR(50) PRIMARY KEY,
    employer_id INT REFERENCES employers(employer_id) ON DELETE CASCADE,
    vacancy_name TEXT NOT NULL,
    salary_from INT,
    salary_to INT,
    salary_currency VARCHAR(10),
    url TEXT,
    requirement TEXT,
    responsibility TEXT,
    published_at TIMESTAMP
);

-- Индексы для ускорения запросов
CREATE INDEX IF NOT EXISTS idx_vacancies_employer ON vacancies(employer_id);
CREATE INDEX IF NOT EXISTS idx_vacancies_salary ON vacancies(salary_from, salary_to);