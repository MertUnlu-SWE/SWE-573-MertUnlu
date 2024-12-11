# Base image olarak Python kullanın
FROM python:3.12.7

# Çalışma dizinini ayarlayın
WORKDIR /app/mysteriumProject

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends gcc libpq-dev

# Bağımlılıkları yükleyin
COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Proje dosyalarını kopyalayın
COPY . .

#VOLUME /var/media

# Ortam değişkenleri tanımlayın (isteğe bağlı)
ENV DB_NAME=postgres
ENV DB_USER=mysteriumMert
ENV DB_PASSWORD=Mert539Unlu
ENV DB_HOST=mysterium-db.cj6g0u6gkb0e.eu-north-1.rds.amazonaws.com
ENV DB_PORT=5432

RUN pip install whitenoise

# Statik dosyaları toplayın
RUN python manage.py collectstatic --noinput

# Statik ve medya dosyalarını düzenle
#RUN mkdir -p /var/media
#RUN chmod -R 755 /var/media

EXPOSE 8000

# Uygulama başlatma komutu
CMD ["gunicorn", "mysteriumProject.wsgi:application", "--bind", "0.0.0.0:8000"]

