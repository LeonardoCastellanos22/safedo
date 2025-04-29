# Python image that runs in RPI ARM systems
FROM python:3.11-slim

WORKDIR /safedo

# Install system dependencies
RUN apt-get update && apt-get install -y nmap adb

# Copy dependencies and install them
COPY requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 5000

CMD ["python3", "app.py"]
