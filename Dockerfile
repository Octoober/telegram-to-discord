FROM python:3.13-alpine

# Установка зависимостей для медиаобработки
RUN apk add --no-cache ffmpeg

# Создает пользователя
RUN addgroup -S appuser && \ 
    adduser -S -G appuser -u 1000 -h /home/appuser -s /bin/sh appuser


# Создание рабочих директорий
RUN mkdir -p \
    /home/appuser/app/logs \
    /temp \
    chown -R appuser:appuser /home/appuser /temp /logs

USER appuser

# Рабочая директория
WORKDIR /home/appuser/app

# Копирование зависимостей и установка
COPY --chown=appuser:appuser requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# COPY --chown=appuser:appuser settings.json ./
# Копирование исходного кода
COPY --chown=appuser:appuser . ./

ENV PYTHONPATH="${PYTHONPATH}:/home/appuser/app"

CMD ["python", "-u", "app/main.py"]