# Small official Python 3.12 image
FROM python:3.12-slim

# Work inside /app in the container
WORKDIR /app

# Show Flask logs immediately in docker logs
ENV PYTHONUNBUFFERED=1

# Install dependencies first (Docker caches this layer)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the project
COPY . .

# Flask listens on port 5000
EXPOSE 5000

# Start the app
CMD ["python", "app.py"]
