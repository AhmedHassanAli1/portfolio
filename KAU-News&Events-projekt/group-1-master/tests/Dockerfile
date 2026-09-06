FROM python:3.10-alpine
WORKDIR /app
ENV PYTHONUNBUFFERED=0
ENV PYTHONDONTWRITEBYTECODE=1
ENV FLASK_APP=app.py
ENV FLASK_RUN_HOST=0.0.0.0
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt
CMD ["pytest", "-v"]
