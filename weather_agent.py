from dotenv import load_dotenv
import os

from langchain.agents import create_agent
from langchain_openrouter import ChatOpenRouter

from weather_tool import get_weather


load_dotenv()

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")


weather_llm = ChatOpenRouter(
    model="anthropic/claude-haiku-4.5",
    api_key=OPENROUTER_API_KEY,
    temperature=0,
    max_tokens=1000
)


WEATHER_SYSTEM_PROMPT = (
    "Sen Türkçe konuşan profesyonel bir hava durumu uzmanısın. "

    "Görevin yalnızca şehirlerin güncel hava durumu hakkında yardımcı olmaktır. "

    "Kullanıcı herhangi bir şehir için hava durumunu sorduğunda "
    "mutlaka get_weather tool'unu kullan. "

    "Cevabında yalnızca tool sonucunda bulunan gerçek verilere bağlı kal. "
    "Eksik bilgi üretme ve hava durumu verilerini tahmin etme. "

    "Cevabını aşağıdaki düzende ver:\n\n"

    "[Şehir] için güncel hava durumu:\n"
    "- Durum: ...\n"
    "- Sıcaklık: ...°C\n"
    "- Hissedilen sıcaklık: ...°C\n"
    "- Nem: %...\n"
    "- Rüzgar hızı: ... m/s\n"
    "- Bulutluluk: %...\n"
    "- Görüş mesafesi: ... km\n\n"

    "Cevabın sonunda hava koşullarıyla ilgili en fazla bir kısa ve doğal yorum yaz. "

    "Rüzgar hızını yüzde olarak yazma; m/s birimiyle yaz. "

    "Teknik dokümantasyon veya hava durumu dışındaki sorulara cevap verme. "
    "Böyle bir soru gelirse bu konunun başka bir uzman agent tarafından "
    "ele alınması gerektiğini kısa şekilde belirt."
)


weather_agent = create_agent(
    model=weather_llm,
    tools=[get_weather],
    system_prompt=WEATHER_SYSTEM_PROMPT,
    name="weather_agent"
)