FROM nginx:latest

# Varsayılan Nginx yapılandırmasını kaldır
RUN rm /etc/nginx/conf.d/default.conf

# Özel yapılandırmanızı ekleyin
COPY nginx.conf /etc/nginx/conf.d/

# Port 80'i açın
EXPOSE 80
