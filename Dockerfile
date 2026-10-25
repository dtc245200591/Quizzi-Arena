FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

RUN groupadd --system app \
    && useradd --system --gid app --home-dir /app app \
    && mkdir -p /app/data /app/staticfiles \
    && chown -R app:app /app

COPY requirements.txt ./
RUN pip install --upgrade pip \
    && pip install -r requirements.txt

COPY --chown=app:app . .
RUN python manage.py collectstatic --noinput

USER app
EXPOSE 8000

HEALTHCHECK --interval=20s --timeout=5s --start-period=20s --retries=5 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/healthz/', timeout=3)"

CMD ["sh", "-c", "python manage.py migrate --noinput && exec gunicorn quizzi.wsgi:application --bind 0.0.0.0:8000 --workers 2 --access-logfile - --error-logfile -"]
