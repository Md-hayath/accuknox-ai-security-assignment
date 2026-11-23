FROM python:3.12-slim-bookworm AS builder
WORKDIR /build
COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

FROM python:3.12-slim-bookworm
WORKDIR /app
RUN groupadd --gid 1000 app && useradd --uid 1000 --gid 1000 --create-home app
COPY --from=builder /install /usr/local
COPY assignment1 ./assignment1
RUN mkdir -p /app/assignment1/output && chown -R app:app /app
USER app
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    MPLCONFIGDIR=/tmp/matplotlib
CMD ["python", "assignment1/run_all.py"]
