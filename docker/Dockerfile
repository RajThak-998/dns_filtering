FROM python:3.12-slim

# Set working directory inside container
WORKDIR /app

# Copy dependencies first (layer caching)
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY dns ./dns
COPY main.py .
COPY db ./db
COPY logs ./logs

# DNS uses UDP
EXPOSE 5300/udp

# Run DNS server
CMD ["python", "main.py"]
