# Python image that runs in RPI ARM systems
FROM python:3.11-slim

WORKDIR /safedo

# Copy dependencies and install them
COPY requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt

COPY . .

# Expose port 5000
EXPOSE 5000

# Run the app
CMD ["python", "app.py"]