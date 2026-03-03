FROM python:3.10-slim

ENV TZ=Asia/Vladivostok

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . /app/

ENV PYTHONPATH=/app/src

CMD ["gunicorn", "-c", "src/gunicorn.conf.py", "src.app:app"]