# 1. TEMEL İMAJ: Ödevin bizden tam olarak istediği Python sürümünü taban alıyoruz.
# "slim" versiyonu gereksiz sistem dosyalarından arındırılmış hafif bir versiyondur.
FROM python:3.13-slim

# 2. ÇALIŞMA DİZİNİ: Konteynerin içinde kendimize "/app" adında bir klasör açıyoruz.
# Bundan sonraki tüm işlemler bu klasörün içinde yapılacak.
WORKDIR /app

# 3. KÜTÜPHANE LİSTESİNİ KOPYALA: Senin bilgisayarındaki requirements.txt dosyasını, 
# konteynerin içindeki /app klasörüne kopyalıyoruz.
COPY requirements.txt .

# 4. KÜTÜPHANELERİ KUR: Python'un paket yöneticisi (pip) ile listemizdeki her şeyi indiriyoruz.
# --no-cache-dir parametresi, indirme dosyalarını silerek konteynerin boyutunu küçük tutar.
RUN pip install --no-cache-dir -r requirements.txt

# 5. KODLARI KOPYALA: Bilgisayarındaki api klasöründeki her şeyi (main.py vb.), 
# konteynerin içine kopyala.
COPY . .

# 6. ÇALIŞTIRMA KOMUTU: Konteyner ayağa kalktığında bu komut çalışacak.
# uvicorn: Sunucumuz. main:app -> main.py içindeki app objesini çalıştır.
# --host 0.0.0.0: Dışarıdan gelen bağlantılara açık ol.
# --reload: Kodda bir değişiklik yaparsak sunucuyu otomatik yeniden başlat (Geliştirme için harika!)
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]