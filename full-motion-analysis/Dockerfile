FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    MOTION_UPLOAD_ROOT=/tmp/motion-evidence-lab/uploads \
    MOTION_REPORT_DIR=/tmp/motion-evidence-lab/reports

RUN apt-get update \
    && apt-get install --yes --no-install-recommends ffmpeg ca-certificates libglib2.0-0 libgomp1 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY pyproject.toml README.md ./
COPY motionlab ./motionlab
COPY remote_mcp_server.py ./remote_mcp_server.py
RUN python -m pip install --disable-pip-version-check ".[vision,mcp,remote]"

RUN useradd --system --uid 10001 --create-home motion \
    && mkdir -p /tmp/motion-evidence-lab/uploads /tmp/motion-evidence-lab/reports \
    && chown -R motion:motion /app /tmp/motion-evidence-lab

USER motion
EXPOSE 10000
CMD ["sh", "-c", "exec uvicorn remote_mcp_server:app --host 0.0.0.0 --port \${PORT:-10000} --workers 1 --proxy-headers"]
