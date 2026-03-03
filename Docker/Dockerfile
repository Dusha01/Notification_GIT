FROM python:3.10-slim

ENV TZ=Asia/Vladivostok
ENV PYTHONPATH=/app

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . /app/

CMD ["python", "run.py"]