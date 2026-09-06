FROM python:3.13-slim

RUN mkdir /app

WORKDIR /app

ENV PYHTONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

RUN pip install --upgrade pip

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8001

CMD ["python","manage.py","runserver","0.0.0.0:8001"]