# 1. Temel İmajımız
FROM freeradius/freeradius-server:latest-3.2

# 2. Dosyalarımızı kopyalıyoruz
COPY rest /etc/freeradius/mods-enabled/rest
COPY default /etc/freeradius/sites-enabled/default

# 3. İŞTE SİHİRLİ DOKUNUŞ: Dosya izinlerini "Sadece root yazabilir, diğerleri sadece okuyabilir" yapıyoruz (644)
RUN chmod 644 /etc/freeradius/mods-enabled/rest
RUN chmod 644 /etc/freeradius/sites-enabled/default