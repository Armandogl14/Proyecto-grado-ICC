FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DEBIAN_FRONTEND=noninteractive

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    postgresql-client \
    redis-tools \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Download spaCy model
RUN python -m spacy download es_core_news_sm

# Download NLTK data
RUN python -c "import nltk; nltk.download('stopwords'); nltk.download('punkt')"

# Copy project
COPY . /app/

# Create static and media directories
RUN mkdir -p /var/www/static /var/www/media

# Collect static files
RUN python manage.py collectstatic --noinput --settings=backend.settings_production

# Create non-root user
RUN useradd --create-home --shell /bin/bash appuser && \
    chown -R appuser:appuser /app /var/www
USER appuser

# Expose port
EXPOSE 8000

# Run gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "3", "--timeout", "120", "backend.wsgi:application"]
