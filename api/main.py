from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from fastapi import FastAPI, Request
from pydantic import BaseModel
import psycopg2
import redis
import hashlib
import os

app = FastAPI(title="NAC Policy Engine")

# 1. ÇEVRESEL DEĞİŞKENLER (Docker'dan gelen şifreleri alıyoruz)
DB_USER = os.getenv("POSTGRES_USER", "project_admin")
DB_PASS = os.getenv("POSTGRES_PASSWORD", "cok_gizli_sifre_123")
DB_DB = os.getenv("POSTGRES_DB", "nac_database")
DB_HOST = "postgres" # docker-compose.yml içindeki servis adımız

# Global bağlantı nesnelerimiz (C++'daki pointerlar gibi düşünebilirsin)
conn = None
redis_client = None

# 2. BAŞLANGIÇ AYARLARI (Sunucu ilk açıldığında çalışır)
@app.on_event("startup")
def startup_db_client():
    global conn, redis_client
    # PostgreSQL'e Bağlan
    conn = psycopg2.connect(dbname=DB_DB, user=DB_USER, password=DB_PASS, host=DB_HOST)
    # Redis'e Bağlan
    redis_client = redis.Redis(host='redis', port=6379, db=0, decode_responses=True)

# 3. VERİ MODELİ (C++ / Java'daki Struct veya Class yapısı)
# FreeRADIUS'un bize göndereceği JSON verisinin şablonunu çıkarıyoruz.
class AuthRequest(BaseModel):
    username: str
    password: str = "" # MAB (MAC adresiyle giriş) yaparsak şifre boş gelebilir
    mac: str = ""

# 4. KİMLİK DOĞRULAMA ENDPOINT'İ (/auth)
@app.post("/auth")      # /autha post isteği atıyor  
def authenticate(req: AuthRequest):
    # ADIM 1: Rate-Limit
    attempts = redis_client.get(f"ratelimit:{req.username}")
    if attempts and int(attempts) >= 3:
        # 3 kez yanlış girdiyse HTTP 401 fırlatarak FreeRADIUS'u reddetmeye zorla
        raise HTTPException(status_code=401, detail="Cok fazla hatali deneme!")

    # ADIM 2: Veritabanında Kullanıcıyı Bul
    cursor = conn.cursor()
    cursor.execute("SELECT value FROM radcheck WHERE username = %s", (req.username,))
    result = cursor.fetchone()
    
    if not result:
        raise HTTPException(status_code=401, detail="Kullanici bulunamadi!")
        
    db_password_hash = result[0] 
    gelen_sifre_hash = hashlib.sha256(req.password.encode()).hexdigest()  
        # Python hashlib kütüphanesi ile SHA-256 doğrulaması yapıyoruz

    # ADIM 3: Şifre Kontrolü
    if gelen_sifre_hash == db_password_hash:
        redis_client.delete(f"ratelimit:{req.username}")
        # control:Auth-Type satırını sildik! Sadece mesaj dönüyoruz.
        return {"Reply-Message": "Hosgeldiniz! Su içmeyi unutmayin"}
    else:
        redis_client.incr(f"ratelimit:{req.username}")
        redis_client.expire(f"ratelimit:{req.username}", 60)
        raise HTTPException(status_code=401, detail="Hatali sifre!")
    

# 5. YETKİLENDİRME (AUTHORIZATION) ENDPOINT'İ
class AuthorizeRequest(BaseModel):
    username: str
    mac: str = ""

@app.post("/authorize")
def authorize(req: AuthorizeRequest):
    cursor = conn.cursor()
    
    # Kullanıcının hangi grupta (admin, employee, guest vb.) olduğunu ve 
    # o gruba ait VLAN ayarlarını veritabanından çekiyoruz.
    # SQL JOIN işlemi ile iki tabloyu (radusergroup ve radgroupreply) birleştiriyoruz.
    sorgu = """
        SELECT g.attribute, g.value 
        FROM radusergroup u 
        JOIN radgroupreply g ON u.groupname = g.groupname 
        WHERE u.username = %s
    """
    cursor.execute(sorgu, (req.username,))
    replies = cursor.fetchall()
    
    # FreeRADIUS'a döneceğimiz cevap sözlüğü
    response_dict = {}
    
    if replies:
        # Eğer kullanıcının bir grubu ve özel ayarları varsa, bunları cevaba ekle
        for attribute, value in replies:
            response_dict[attribute] = value
    else:
        # Kullanıcının özel bir grubu yoksa, onu varsayılan olarak Misafir Ağına (VLAN 30) atalım.
        response_dict["Tunnel-Type"] = "VLAN"
        response_dict["Tunnel-Medium-Type"] = "IEEE-802"
        response_dict["Tunnel-Private-Group-Id"] = "30"
        
    return response_dict


# 6. ACCOUNTING (LOGLAMA) ENDPOINT'İ
class AccountingRequest(BaseModel):
    username: str
    status_type: str        # Start, Stop veya Interim-Update
    session_id: str   
    nas_ip: str             # İŞTE BURASI! Artık API'miz bu veriyi zorunlu olarak isteyecek.
    input_octets: int = 0   # İndirilen veri (Varsayılan 0)
    output_octets: int = 0  # Yüklenen veri (Varsayılan 0)
    session_time: int = 0   # Saniye cinsinden ne kadar ağda kaldı?

@app.post("/accounting")
def accounting(req: AccountingRequest):
    try:
        cursor = conn.cursor()
        
        # DURUM 1: Kullanıcı ağa ilk bağlandığında (Start)
        if req.status_type == "Start":
            # 1. Kalıcı olarak PostgreSQL'e yaz (Tarihe not düşüyoruz)
            sorgu = "INSERT INTO radacct (username, acctsessionid, acctstarttime, nasipaddress) VALUES (%s, %s, CURRENT_TIMESTAMP, %s)"
            cursor.execute(sorgu, (req.username, req.session_id, req.nas_ip))
            
            # 2. Hızlı erişim için Redis'e yaz (Kimlik kartını masaya koyuyoruz)
            # "session:XYZ-987" isminde bir anahtar oluşturup içine "testuser" yazıyoruz.
            redis_client.set(f"session:{req.session_id}", req.username)
            
        # DURUM 2: Kullanıcı ağdan çıktığında (Stop)
        elif req.status_type == "Stop":
            # 1. PostgreSQL'deki kaydı bul, çıkış saatini ve harcadığı veriyi güncelle
            sorgu = "UPDATE radacct SET acctstoptime = CURRENT_TIMESTAMP, acctsessiontime = %s, acctinputoctets = %s, acctoutputoctets = %s WHERE acctsessionid = %s"
            cursor.execute(sorgu, (req.session_time, req.input_octets, req.output_octets, req.session_id))
            
            # 2. Adam ağdan çıktığı için Redis'teki aktif kimlik kartını yırtıp atıyoruz
            redis_client.delete(f"session:{req.session_id}")
            
        conn.commit()
        return {"status": "success"}
        
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=str(e))


# 7. SİSTEMDEKİ KULLANICILARI LİSTELEME
@app.get("/users")
def get_users():
    cursor = conn.cursor()
    # radcheck tablosundaki tüm kullanıcı adlarını getir
    cursor.execute("SELECT username FROM radcheck")
    users = cursor.fetchall()
    
    # Gelen veriyi ( ('testuser',), ('admin',) ) düzgün bir listeye çeviriyoruz
    kullanici_listesi = [u[0] for u in users]
    return {"kayitli_kullanicilar": kullanici_listesi}


# 8. ŞU AN AĞDA AKTİF OLAN KULLANICILAR (REDIS'TEN OKUNUR)
@app.get("/sessions/active")
def get_active_sessions():
    aktif_oturumlar = []
    
    # Redis'in içinde adı "session:" ile başlayan tüm anahtarları tara
    for key in redis_client.scan_iter("session:*"):
        username = redis_client.get(key)

        # Verileri listeye ekle (byte formatından string formatına çeviriyoruz .decode() ile)
        # .decode() kısımlarını sildik, çünkü veri zaten metin (string) olarak geliyor!
        aktif_oturumlar.append({
            "session_id": key.split(":")[1], 
            "username": username
        })
        
    return {"aktif_kullanicilar": aktif_oturumlar}