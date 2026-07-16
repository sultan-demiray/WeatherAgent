from dotenv import load_dotenv
import os
import requests

from langchain.tools import tool


load_dotenv()

OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")


@tool
def get_weather(city: str) -> str:
    """
    Verilen şehir adına göre güncel hava durumu bilgisini getirir.

    Args:
        city: Kullanıcının hava durumunu öğrenmek istediği şehir adı.
              Örnek: Istanbul, Ankara, Izmir, London.

    Returns:
        Sıcaklık, hissedilen sıcaklık, nem, basınç, rüzgar hızı,
        bulutluluk ve görüş mesafesi bilgilerini içeren okunabilir bir hava durumu özeti.
    """

    if not OPENWEATHER_API_KEY:
        return "OpenWeather API key bulunamadı. Lütfen .env dosyasını kontrol edin."

    url = "https://api.openweathermap.org/data/2.5/weather"

    params = {
        "q": city,
        "appid": OPENWEATHER_API_KEY,
        "units": "metric",
        "lang": "tr"
    }

    try:
        response = requests.get(url, params=params, timeout=10)
        data = response.json()

        if response.status_code != 200:
            error_message = data.get("message", "Bilinmeyen hata")
            return f"'{city}' için hava durumu bilgisi bulunamadı. Hata: {error_message}"

        city_name = data["name"]
        country = data["sys"]["country"]

        temperature = round(data["main"]["temp"])
        feels_like = round(data["main"]["feels_like"])
        temp_min = round(data["main"]["temp_min"])
        temp_max = round(data["main"]["temp_max"])

        humidity = data["main"]["humidity"]
        pressure = data["main"]["pressure"]

        wind_speed = data["wind"]["speed"]
        wind_degree = data["wind"].get("deg", "Bilinmiyor")

        cloudiness = data["clouds"]["all"]
        visibility_km = data.get("visibility", 0) / 1000

        description = data["weather"][0]["description"]

        return (
            f"{city_name}, {country} için güncel hava durumu:\n"
            f"- Durum: {description}\n"
            f"- Sıcaklık: {temperature}°C\n"
            f"- Hissedilen sıcaklık: {feels_like}°C\n"
            f"- Minimum sıcaklık: {temp_min}°C\n"
            f"- Maksimum sıcaklık: {temp_max}°C\n"
            f"- Nem: %{humidity}\n"
            f"- Basınç: {pressure} hPa\n"
            f"- Rüzgar hızı: {wind_speed} m/s\n"
            f"- Rüzgar yönü: {wind_degree}°\n"
            f"- Bulutluluk: %{cloudiness}\n"
            f"- Görüş mesafesi: {visibility_km:.1f} km"
        )

    except requests.exceptions.RequestException as error:
        return f"Hava durumu servisine bağlanırken bir hata oluştu: {error}"