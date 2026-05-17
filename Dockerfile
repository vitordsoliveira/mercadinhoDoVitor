FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY . /app

EXPOSE 10000

CMD ["gunicorn", "run:app", "--bind", "0.0.0.0:10000", "--workers", "2"]
