# Backend CodeLingo API

**CodeLingo** — это RESTful API для мобильного приложения, предназначенного для изучения языков программирования. Проект объединяет в себе элементы геймификации (уровни, задачи, достижения) и классического онлайн-обучения.

### Основной стек
- Язык: Python 3.10+
- Фреймворк: FastAPI
- База данных: PostgreSQL
- ORM: SQLAlchemy 2.0 (Async) + Alembic (миграции)
- Валидация данных: Pydantic v2
- Паттерны: Unit of Work (UOW), Repository, Service Layer
- Тестирование: Pytest + HTTPX + Aiosqlite

### Ключевые интеграции

* Google Auth
* Cloudinary (облачное хранилище для медиафайлов)
* Resend (сервис для отправки писем) 

## Основные возможности
_Auth System_: Регистрация, логин (JWT) и социальный вход через Google.

_Learning Path_: Система курсов, разбитых на уровни и задачи различных типов (множственный выбор, заполнение пропусков, написание кода).

_User Progress_: Отслеживание пройденных этапов и сбор статистики.

_Gamification_: Система достижений и наград за активность.

## Структура проекта

```
backend-codelingo/
├── alembic.ini                    # Конфигурация Alembic для миграций базы данных
├── Dockerfile                     # Docker-конфигурация для контейнеризации приложения
├── entrypoint.sh                  # Скрипт запуска приложения в контейнере
├── pytest.ini                     # Конфигурация Pytest для тестирования
├── README.md                      # Документация проекта
├── requirements.txt               # Зависимости Python
├── alembic/                       # Директория миграций базы данных
├── app/                           # Основной код приложения
│   ├── main.py                    # Точка входа FastAPI приложения
│   ├── api/                       # API маршруты
│   │   └── v1/                    # Версия 1 API
│   ├── core/                      # Ядро приложения
│   │   ├── cloudinary.py          # Интеграция с Cloudinary
│   │   ├── config.py              # Конфигурация приложения
│   │   ├── exception.py           # Пользовательские исключения
│   │   ├── oath_google.py         # Google OAuth интеграция
│   │   ├── resend.py              # Интеграция с Resend для email
│   │   └── security.py            # Безопасность и аутентификация
│   ├── database/                  # Работа с базой данных
│   ├── executors/                 # Исполнители кода
│   │   ├── base.py                # Базовый класс исполнителя
│   │   ├── js_executor.py         # Исполнитель JavaScript кода
│   │   ├── python_executor.py     # Исполнитель Python кода
│   │   └── wandbox_executor.py    # Исполнитель через Wandbox API
│   ├── internal/                  # Внутренние компоненты
│   │   ├── admin_views.py         # Админ-панель
│   │   ├── mail.py                # Работа с email через FastAPI Mail
│   ├── models/                    # Модели базы данных
│   ├── repositories/              # Репозитории для работы с данными
│   ├── schemas/                   # Pydantic схемы для валидации
│   ├── services/                  # Бизнес-логика
│   └── utils/                     # Утилиты
└── tests/                         # Тесты
```