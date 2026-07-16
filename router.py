from dotenv import load_dotenv
import os
import asyncio
import time

from database import save_token_usage

from typing import Literal
from pydantic import BaseModel, Field

from langchain_openrouter import ChatOpenRouter

from langchain_core.callbacks import UsageMetadataCallbackHandler

from weather_agent import weather_agent
from docs_agent import create_docs_agent

load_dotenv()

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")


class RouteDecision(BaseModel):
    """
    Kullanıcı sorusunun hangi agente gönderileceğini belirleyen
    yapılandırılmış router çıktısı.
    """

    route: Literal["weather", "docs", "general"] = Field(
        description=(
            "Kullanıcı sorusunun yönlendirileceği kategori. "
            "Hava durumu soruları için 'weather', "
            "teknik dokümantasyon soruları için 'docs', "
            "selamlaşma veya diğer sorular için 'general'."
        )
    )


router_llm = ChatOpenRouter(
    model="anthropic/claude-haiku-4.5",
    api_key=OPENROUTER_API_KEY,
    temperature=0,
    max_tokens=100
)

general_llm = ChatOpenRouter(
    model="anthropic/claude-haiku-4.5",
    api_key=OPENROUTER_API_KEY,
    temperature=0.4,
    max_tokens=250
)

structured_router = router_llm.with_structured_output(
    RouteDecision
)


ROUTER_SYSTEM_PROMPT = """
Sen bir yönlendirme uzmanısın.

Kullanıcının mesajını yalnızca aşağıdaki üç kategoriden birine ayır:

1. weather

Şehirlerin hava durumu, sıcaklık, hissedilen sıcaklık,
yağmur, kar, nem, rüzgar, bulutluluk veya görüş mesafesi
hakkındaki sorular bu kategoriye girer.

Kullanıcı yalnızca bir şehir adı yazarsa da bunu weather
olarak sınıflandır.

Örnekler:

"İstanbul'da hava nasıl?"
→ weather

"Ankara'da yağmur var mı?"
→ weather

"Kütahya"
→ weather

"İstanbul"
→ weather

"Paris"
→ weather


2. docs

Programlama, yazılım geliştirme, Python, LangChain,
LangGraph, Streamlit, OpenRouter, API, framework,
kütüphane, kod kullanımı veya teknik dokümantasyon
hakkındaki sorular bu kategoriye girer.

Örnekler:

"Streamlit'te session_state nasıl kullanılır?"
→ docs

"LangChain create_agent nedir?"
→ docs

"Python'da liste nasıl oluşturulur?"
→ docs


3. general

Selamlaşma, teşekkür, vedalaşma veya weather ve docs
kategorilerine girmeyen mesajlar bu kategoriye girer.

Örnekler:

"Merhaba"
→ general

"Teşekkür ederim"
→ general

"Görüşürüz"
→ general


Sadece kategoriyi belirle.
Kullanıcının sorusunu cevaplama.
"""


def classify_question(
    question: str,
    callback: UsageMetadataCallbackHandler | None = None
) -> str:
    """
    Kullanıcı sorusunu LLM ile sınıflandırır
    ve weather, docs veya general değerlerinden birini döndürür.
    """

    config = {}

    if callback is not None:
        config = {
            "callbacks": [callback]
        }

    result = structured_router.invoke(
        [
            {
                "role": "system",
                "content": ROUTER_SYSTEM_PROMPT
            },
            {
                "role": "user",
                "content": question
            }
        ],
        config=config
    )

    return result.route


def get_token_usage(callback: UsageMetadataCallbackHandler) -> dict:
    """
    Callback içinden token kullanım bilgisini okunabilir hale getirir.
    """

    usage = callback.usage_metadata

    total_input_tokens = 0
    total_output_tokens = 0
    total_tokens = 0

    for model_name, model_usage in usage.items():
        total_input_tokens += model_usage.get("input_tokens", 0)
        total_output_tokens += model_usage.get("output_tokens", 0)
        total_tokens += model_usage.get("total_tokens", 0)

    return {
        "input_tokens": total_input_tokens,
        "output_tokens": total_output_tokens,
        "total_tokens": total_tokens,
        "details": usage
    }


async def get_docs_answer(
    question: str,
    callback: UsageMetadataCallbackHandler
) -> str:
    """
    Teknik dokümantasyon sorusunu Docs Agent'a gönderir
    ve son cevabı döndürür.
    """

    docs_agent = await create_docs_agent()

    result = await docs_agent.ainvoke(
        {
            "messages": [
                {
                    "role": "user",
                    "content": question
                }
            ]
        },
        config={
            "callbacks": [callback]
        }
    )

    return result["messages"][-1].content


def get_answer(question: str) -> str:
    """
    Kullanıcı sorusunu sınıflandırır,
    ilgili uzman agent'a yönlendirir
    ve token kullanım bilgisini terminale yazdırır.
    """

    callback = UsageMetadataCallbackHandler()

    route = classify_question(question, callback)

    if route == "weather":
        result = weather_agent.invoke(
            {
                "messages": [
                    {
                        "role": "user",
                        "content": question
                    }
                ]
            },
            config={
                "callbacks": [callback]
            }
        )

        token_usage = get_token_usage(callback)

        print("ROUTE:", route)
        print("TOKEN USAGE:", token_usage)

        save_token_usage(question, route, token_usage)

        return result["messages"][-1].content

    if route == "docs":
        answer = asyncio.run(
            get_docs_answer(question, callback)
    )

        token_usage = get_token_usage(callback)

        print("ROUTE:", route)
        print("TOKEN USAGE:", token_usage)

        save_token_usage(question, route, token_usage)

        return answer

    general_response = general_llm.invoke(
        [
            {
                "role": "system",
                "content": (
                    "Sen Türkçe konuşan samimi ve kısa cevaplar veren "
                    "bir yardımcı asistansın. "
                    "Kullanıcının selamlaşma, teşekkür, vedalaşma veya "
                    "gündelik kısa mesajlarına doğal şekilde cevap ver. "
                    "Uzun açıklamalar yapma. "
                    "Kullanıcı hava durumu veya teknik dokümantasyon dışında "
                    "ayrıntılı bir konuda yardım isterse, bu uygulamanın "
                    "özellikle hava durumu ve teknik dokümantasyon alanlarına "
                    "odaklandığını kibarca belirt."
                )
            },
            {
                "role": "user",
                "content": question
            }
        ],
        config={
            "callbacks": [callback]
        }
    )

    token_usage = get_token_usage(callback)

    print("ROUTE:", route)
    print("TOKEN USAGE:", token_usage)

    save_token_usage(question, route, token_usage)

    return general_response.content


def ask_agent_stream(answer: str):
    """
    Hazırlanmış cevabı Streamlit ekranına
    karakter karakter gönderir.
    """

    for char in answer:
        yield char
        time.sleep(0.01)