# telegram_bot_mindset

**Telegram bot Picpack**

Телеграм бот генерирует описание и теги для картинки

## Запуск бота:
- Получить Токен через BotFather
- Создать файл .env из env.example, поменять переменные окружения

## Бот подключается к API локального бека и локальной базе данных, а также при запуске его на сервере:
- pip install -r requirements.txt при запуске локально
- Добавить модели из db.py в модели бека и сделать миграции

## Бот запускается локально, подключается к удаленному API на сервере:

- pip install -r requirements.txt
- Создать отдельную базу на сервере Postgres и создать ссылку подключения
- Запустить файл utils.py **Это удалит все данные в созданной базе и создаст новые таблицы**
- Запустить бот через bot_start.py

### В папке docs содержится инструкция по переводам бота



