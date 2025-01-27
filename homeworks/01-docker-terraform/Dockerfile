FROM python:3.12-slim

RUN apt-get update \
    && apt-get install --no-install-recommends -y wget \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY ingest_data.py .

ENTRYPOINT [ "./ingest_data.py" ]
