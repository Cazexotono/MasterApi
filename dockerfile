FROM python:3.13.9-slim-trixie

WORKDIR /app
RUN pip install --no-cache-dir uv

COPY  pyproject.toml ./

RUN uv pip install --system .

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app/backend

CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
