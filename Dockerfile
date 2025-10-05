FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1

RUN useradd -m -r appuser && mkdir /app && chown -R appuser /app

USER appuser

COPY . /app/

WORKDIR /app

RUN pip install --upgrade pip && pip install uv && uv sync && uv run newsflash_setup

EXPOSE 8000

CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "2", "main:app"]