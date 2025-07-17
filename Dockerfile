###############################################################################
#                               ── BUILD STAGE ──                            #
# Purpose: compile *all* Python deps (and their own deps) into wheels offline #
###############################################################################
FROM python:3.11-slim AS builder

#–– basic hygiene ––
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /build

#–– system packages required by some Python wheels (e.g. uvloop) ––
RUN apt-get update && \
    apt-get install --no-install-recommends -y build-essential && \
    rm -rf /var/lib/apt/lists/*

#–– dependency list ––
COPY requirements.txt .

#–– build every requirement (incl. transitive deps) into /wheels ––
RUN pip wheel --no-cache-dir --wheel-dir /wheels -r requirements.txt



###############################################################################
#                              ── RUNTIME STAGE ──                            #
# Purpose: copy wheels, install offline, copy source, start Uvicorn           #
###############################################################################
FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# 1) copy the whole wheel‑house from builder
COPY --from=builder /wheels /wheels

# 2) copy requirements.txt for reproducibility (pip still needs it)
COPY requirements.txt .

# 3) install everything *strictly* from wheelhouse – no internet hits here
RUN pip install --no-cache-dir --no-index --find-links=/wheels -r requirements.txt && \
    rm -rf /wheels              # trim image size

# 4) copy application source
COPY app ./app

# 5) open the API port
EXPOSE 8000

# 6) default command
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
