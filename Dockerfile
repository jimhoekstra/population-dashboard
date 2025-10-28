FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1

RUN useradd -m -r appuser && mkdir /home/appuser/app

COPY . /home/appuser/app

WORKDIR /home/appuser/app

RUN chown -R appuser:appuser /home/appuser/app

RUN pip install --upgrade pip && pip install -r requirements.txt

EXPOSE 8000

USER appuser

CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "2", "main:wsgi_app"]