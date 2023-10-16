FROM python:3.7.16-slim AS base

RUN apt-get update \
    && apt-get install -y python3-dev python3-opencv poppler-utils \
    && rm -rf /var/lib/apt/lists/*

RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

WORKDIR /app

COPY requirements.txt requirements.txt

RUN pip3 install -r requirements.txt

FROM python:3.7.16-slim

RUN apt-get update &&\
    apt-get install -y python3-opencv poppler-utils && \
    rm -rf /var/lib/apt/lists/*

COPY --from=base /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

WORKDIR /app

COPY . .

EXPOSE 8501 8000

ENTRYPOINT ["streamlit", "run", "streamlit_2.py", "--server.port=8501", "--server.address=0.0.0.0"]