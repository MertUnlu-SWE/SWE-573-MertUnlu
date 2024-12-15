# Base image for Python Version
FROM python:3.12.7

# Working Directory Setting
WORKDIR /app/mysteriumProject

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends gcc libpq-dev

# Get Requirements
COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy Project Files
COPY . .

# Define Env Variables (Optional)
ENV DB_NAME=postgres
ENV DB_USER=mysteriumMert
ENV DB_PASSWORD=Mert539Unlu
ENV DB_HOST=mysterium-db.cj6g0u6gkb0e.eu-north-1.rds.amazonaws.com
ENV DB_PORT=5432

RUN pip install whitenoise

# Collect Static Files
RUN python manage.py collectstatic --noinput

EXPOSE 8000

# Application Start Command
CMD ["gunicorn", "mysteriumProject.wsgi:application", "--bind", "0.0.0.0:8000"]

