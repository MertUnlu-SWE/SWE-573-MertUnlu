# Base image olarak Python kullanın
FROM python:3.12.7

# Çalışma dizinini ayarlayın
WORKDIR /app/mysteriumProject

# Bağımlılıkları yükleyin
COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt


# Proje dosyalarını kopyalayın
COPY . .

# Ortam değişkenleri tanımlayın (isteğe bağlı)
ENV DB_NAME=postgres
ENV DB_USER=mysteriumMert
ENV DB_PASSWORD=Mert539Unlu
ENV DB_HOST=mysterium-db.cj6g0u6gkb0e.eu-north-1.rds.amazonaws.com
ENV DB_PORT=5432

RUN pip install whitenoise

# Statik dosyaları toplayın
RUN python manage.py collectstatic --noinput

EXPOSE 8000

# Uygulama başlatma komutu
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "mysteriumProject.wsgi:application"]

# Django komutlarını çalıştırmak için entrypoint ayarlayın
#CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
