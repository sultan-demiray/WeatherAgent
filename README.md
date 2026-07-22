# Weather & Docs Agent

Bu proje, LangChain tabanlı çoklu agent mantığına sahip bir Streamlit chat uygulamasıdır.

Uygulama, kullanıcıdan gelen soruyu LLM tabanlı bir router ile sınıflandırır ve uygun akışa yönlendirir:

- **Weather Agent**: Şehir bazlı güncel hava durumu bilgisini getirir.
- **Docs Agent**: Teknik dokümantasyon sorularını Context7 üzerinden yanıtlar.
- **General Assistant**: Selamlaşma ve kısa günlük mesajlara cevap verir.

Ayrıca her kullanıcı isteği sonrasında token kullanımı callback üzerinden alınır. Bu token bilgileri hem Streamlit arayüzünde gösterilir hem de PostgreSQL veritabanına kaydedilir.

---

## Özellikler

- Streamlit tabanlı chat arayüzü
- OpenRouter üzerinden Claude Haiku 4.5 kullanımı
- OpenWeather API ile güncel hava durumu sorgulama
- Context7 destekli teknik dokümantasyon cevaplama
- LLM tabanlı router ile soru sınıflandırma
- Weather, docs ve general akışlarını ayrı yönetme
- Token kullanımını callback ile ölçme
- Token kullanımını Streamlit arayüzünde gösterme
- Token kayıtlarını PostgreSQL veritabanında saklama
- Son token kayıtlarını `test_database.py` ile görüntüleme
- API key ve gizli bilgileri `.env` dosyasında saklama

---

## Proje Yapısı

```text
WeatherAgent/
│
├── app.py                 # Streamlit chat arayüzü ve token kullanım gösterimi
├── router.py              # LLM router, yönlendirme mantığı ve token ölçümü
├── weather_agent.py       # Weather agent tanımı
├── docs_agent.py          # Docs agent tanımı
├── weather_tool.py        # OpenWeather API tool fonksiyonu
├── database.py            # PostgreSQL bağlantısı ve token kayıt işlemleri
├── test_database.py       # Son token kayıtlarını listeleme dosyası
├── requirements.txt       # Python bağımlılıkları
├── .env.example           # Örnek environment değişkenleri
└── .gitignore             # GitHub'a gönderilmeyecek dosyalar
```

---

## Kullanılan Teknolojiler

- Python
- Streamlit
- LangChain
- LangGraph
- OpenRouter
- Claude Haiku 4.5
- OpenWeather API
- Context7
- PostgreSQL
- psycopg
- python-dotenv

---

## Kurulum

Projeyi klonladıktan sonra proje klasörüne girin.

```bash
cd WeatherAgent
```

Sanal ortam oluşturun:

```bash
python -m venv venv
```

Windows PowerShell için sanal ortamı aktif edin:

```bash
venv\Scripts\Activate.ps1
```

Gerekli paketleri kurun:

```bash
pip install -r requirements.txt
```

---

## Environment Değişkenleri

Proje kök dizininde `.env` dosyası oluşturun.

`.env.example` dosyasını referans alarak aşağıdaki değişkenleri doldurun:

```env
OPENROUTER_API_KEY=your_openrouter_api_key_here
OPENWEATHER_API_KEY=your_openweather_api_key_here
CONTEXT7_API_KEY=your_context7_api_key_here

DATABASE_URL=postgresql://postgres:your_password@localhost:5432/weather_agent_db
```

---

## PostgreSQL Kurulumu

Token kullanım kayıtları PostgreSQL veritabanında saklanmaktadır.

Kullanılan veritabanı adı:

```text
weather_agent_db
```

Token kayıtlarının tutulduğu tablo:

```text
token_usage_logs
```

Tabloyu oluşturmak için:

```bash
python -c "from database import create_token_usage_table; create_token_usage_table(); print('Tablo oluşturuldu')"
```

PostgreSQL server kapalıysa manuel olarak başlatmak için:

```powershell
& "C:\Program Files\PostgreSQL\18\bin\pg_ctl.exe" -D "C:\postgres-data\18" -l "C:\postgres-data\18\logfile.log" start
```

---

## Uygulamayı Çalıştırma

Streamlit uygulamasını başlatmak için:

```bash
streamlit run app.py
```

Uygulama varsayılan olarak şu adreste çalışır:

```text
http://localhost:8501
```

---

## Kullanım Örnekleri

Weather Agent için:

```text
İstanbul'da hava nasıl?
```

```text
Kütahya
```

Docs Agent için:

```text
Streamlit'te st.session_state nasıl kullanılır?
```

```text
LangChain'de create_agent nasıl çalışır?
```

General Assistant için:

```text
Merhaba nasılsın?
```

---

## Token Kullanımı

Bu projede token bilgileri callback yapısı üzerinden alınır.

Her istek sonrasında şu bilgiler elde edilir:

- Kullanıcının sorduğu soru
- Sorunun yönlendirildiği route
- Input token sayısı
- Output token sayısı
- Toplam token sayısı
- Detaylı kullanım bilgisi
- Kayıt tarihi

Token bilgileri iki farklı yerde kullanılır:

1. **Streamlit arayüzünde gösterilir.**
2. **PostgreSQL veritabanındaki `token_usage_logs` tablosuna kaydedilir.**

Arayüzde her cevabın altında **Token Kullanımı** alanı bulunur. Bu alanda ilgili cevabın route bilgisi, input token, output token ve total token değerleri gösterilir.

Örnek arayüz çıktısı:

```text
📊 Token Kullanımı

Route: weather

Input Tokens: 3956

Output Tokens: 275

Total Tokens: 4231
```

---

## Token Kayıtlarını Kontrol Etme

Son token kayıtlarını görüntülemek için:

```bash
python test_database.py
```

Örnek çıktı:

```text
Son Token Kullanım Kayıtları
------------------------------------------------------------
ID: 3
Soru: Streamlit'te st.session_state nasıl kullanılır?
Route: docs
Input Tokens: 8995
Output Tokens: 1077
Total Tokens: 10072
Tarih: 2026-07-22 ...
------------------------------------------------------------
ID: 2
Soru: İstanbul
Route: weather
Input Tokens: 3956
Output Tokens: 275
Total Tokens: 4231
Tarih: 2026-07-22 ...
------------------------------------------------------------
ID: 1
Soru: Merhaba
Route: general
Input Tokens: 1529
Output Tokens: 67
Total Tokens: 1596
Tarih: 2026-07-22 ...
------------------------------------------------------------
```

---

## Çalışma Mantığı

Uygulamanın genel akışı şu şekildedir:

```text
Kullanıcı soru sorar
↓
Router LLM soruyu weather / docs / general olarak sınıflandırır
↓
Soru ilgili agent veya LLM akışına yönlendirilir
↓
Cevap üretilir
↓
Callback ile token bilgisi alınır
↓
Token bilgileri PostgreSQL'e kaydedilir
↓
Token bilgileri Streamlit arayüzünde gösterilir
↓
Cevap kullanıcıya gösterilir
```

---

## Route Yapısı

Router üç farklı kategori kullanır:

### weather

Hava durumu soruları için kullanılır.

Örnekler:

```text
İstanbul'da hava nasıl?
Ankara
İzmir hava durumu
```

### docs

Teknik dokümantasyon soruları için kullanılır.

Örnekler:

```text
Streamlit'te st.session_state nasıl kullanılır?
LangChain create_agent nasıl çalışır?
Python'da dotenv ne işe yarar?
```

### general

Selamlaşma, teşekkür, kısa günlük konuşmalar veya diğer genel mesajlar için kullanılır.

Örnekler:

```text
Merhaba
Nasılsın?
Teşekkür ederim
```

---

## Güvenlik Notu

API key, database şifresi ve diğer gizli bilgiler `.env` dosyasında saklanır.

GitHub'a sadece örnek değişkenleri içeren `.env.example` dosyası yüklenir.

---
