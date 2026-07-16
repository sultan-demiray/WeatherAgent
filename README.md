# Weather & Docs Agent

Bu proje, LangChain tabanlı çoklu agent mantığına sahip bir Streamlit chat uygulamasıdır.

Uygulama, kullanıcıdan gelen soruyu LLM tabanlı bir router ile sınıflandırır ve uygun akışa yönlendirir:

- **Weather Agent**: Şehir bazlı güncel hava durumu bilgisini getirir.
- **Docs Agent**: Teknik dokümantasyon sorularını Context7 üzerinden yanıtlar.
- **General Assistant**: Selamlaşma ve kısa günlük mesajlara cevap verir.

Ayrıca her kullanıcı isteği sonrasında token kullanımı callback üzerinden alınır ve PostgreSQL veritabanına kaydedilir.

---

## Özellikler

- Streamlit tabanlı chat arayüzü
- OpenRouter üzerinden Claude Haiku 4.5 kullanımı
- OpenWeather API ile güncel hava durumu sorgulama
- Context7 destekli teknik dokümantasyon cevaplama
- LLM tabanlı router ile soru sınıflandırma
- Weather, docs ve general akışlarını ayrı yönetme
- Token kullanımını callback ile ölçme
- Token kayıtlarını PostgreSQL veritabanında saklama
- Son token kayıtlarını `test_database.py` ile görüntüleme
- API key ve gizli bilgileri `.env` dosyasında saklama

---

## Proje Yapısı

```text
WeatherAgent/
│
├── app.py                 # Streamlit chat arayüzü
├── router.py              # LLM router ve yönlendirme mantığı
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

LANGSMITH_TRACING=true
LANGSMITH_API_KEY=your_langsmith_api_key_here
LANGSMITH_PROJECT=weather-docs-agent

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

Bu bilgiler PostgreSQL veritabanındaki `token_usage_logs` tablosuna kaydedilir.

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
Input Tokens: 8880
Output Tokens: 961
Total Tokens: 9841
Tarih: 2026-07-16 17:58:22.121731+03:00
------------------------------------------------------------
ID: 2
Soru: Merhaba nasılsın?
Route: general
Input Tokens: 1539
Output Tokens: 65
Total Tokens: 1604
Tarih: 2026-07-16 17:57:43.083973+03:00
------------------------------------------------------------
ID: 1
Soru: İstanbul
Route: weather
Input Tokens: 3956
Output Tokens: 277
Total Tokens: 4233
Tarih: 2026-07-16 17:57:25.387216+03:00
------------------------------------------------------------
```

---

## Çalışma Mantığı

Uygulamanın genel akışı şu şekildedir:

```text
Kullanıcı soru sorar
↓
Router LLM soruyu sınıflandırır
↓
Soru weather, docs veya general route'larından birine yönlendirilir
↓
İlgili agent veya LLM cevap üretir
↓
Callback ile token bilgisi alınır
↓
Token bilgileri PostgreSQL'e kaydedilir
↓
Cevap Streamlit arayüzünde kullanıcıya gösterilir
```

---

## Route Yapısı

Router üç farklı kategori kullanır:

```text
weather
```

Hava durumu soruları için kullanılır.

Örnekler:

```text
İstanbul'da hava nasıl?
Ankara
İzmir hava durumu
```

```text
docs
```

Teknik dokümantasyon soruları için kullanılır.

Örnekler:

```text
Streamlit'te st.session_state nasıl kullanılır?
LangChain create_agent nasıl çalışır?
Python'da dotenv ne işe yarar?
```

```text
general
```

Selamlaşma, teşekkür, kısa günlük konuşmalar veya diğer genel mesajlar için kullanılır.

Örnekler:

```text
Merhaba
Nasılsın?
Teşekkür ederim
```

---

---

## Geliştirme Notları

Bu projede başlangıçta weather ve docs özellikleri tek bir agent yapısı içinde denenmiştir. Daha sonra yapı, daha kontrollü ve genişletilebilir olması için LLM tabanlı router yaklaşımına ayrılmıştır.

Bu sayede her soru tipi ilgili uzman akışa yönlendirilir:

- Weather soruları weather agent'a
- Teknik dokümantasyon soruları docs agent'a
- Genel konuşmalar general assistant'a

Token takibi için callback tabanlı kullanım verisi alınmış ve PostgreSQL'de saklanmıştır.
