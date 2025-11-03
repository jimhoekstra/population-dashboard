FROM ghcr.io/astral-sh/uv:python3.12-trixie-slim

ENV PYTHONUNBUFFERED=1

RUN useradd -m -r appuser && mkdir /home/appuser/app

COPY . /home/appuser/app

WORKDIR /home/appuser/app

RUN chown -R appuser:appuser /home/appuser/app

RUN uv sync

EXPOSE 8000

USER appuser

CMD ["uv", "run", "newsflash", "dev", "main:app"]