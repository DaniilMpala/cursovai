# Dockerfile

# Загружаем пайтен такой-то версии
FROM python:3.11

# Копируем файл с зависимости в рабочую директорию образа
COPY app/requirements.txt requirements.txt
# Загружаем все дополнительные пакеты
RUN pip install --no-cache-dir -r requirements.txt

# копируем из рабочей области в папку app оброза
COPY ./app app
ADD .env /env_file/.env
# Задаем рабочую папку
WORKDIR /app
# выполняем команда пайтена джанго мигрейт
RUN python ./manage.py migrate

# Задаем порт
EXPOSE 8000
# задаем начальную точку запуска
ENTRYPOINT ["python", "./manage.py"]
# Добавляем к ENTRYPOINT допольнительные команды запуска
CMD ["runserver", "0.0.0.0:8000"] 