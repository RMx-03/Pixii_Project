FROM python:3.12-slim

WORKDIR /service

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

COPY pyproject.toml /service/pyproject.toml
RUN pip install --upgrade pip && pip install -e ".[dev]"

COPY . /service

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]

