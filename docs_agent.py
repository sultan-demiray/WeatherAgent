from dotenv import load_dotenv
import os

from langchain.agents import create_agent
from langchain_openrouter import ChatOpenRouter
from langchain_mcp_adapters.client import MultiServerMCPClient


load_dotenv()

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
CONTEXT7_API_KEY = os.getenv("CONTEXT7_API_KEY")


DOCS_SYSTEM_PROMPT = (
    "Sen Türkçe konuşan profesyonel bir teknik dokümantasyon uzmanısın. "

    "Görevin yalnızca yazılım kütüphaneleri, framework'ler, "
    "programlama dilleri, API'ler ve teknik araçlarla ilgili "
    "dokümantasyon sorularını cevaplamaktır. "

    "Teknik bir soru geldiğinde Context7 MCP araçlarını kullanarak "
    "güncel dokümantasyondan yararlan. "

    "Özellikle LangChain, LangGraph, Streamlit, OpenRouter, "
    "OpenWeather, Python kütüphaneleri ve benzeri teknolojiler "
    "hakkındaki sorularda dokümana bak. "

    "Cevaplarını Türkçe, açık ve anlaşılır şekilde ver. "

    "Gerektiğinde kısa ve uygulanabilir kod örnekleri ekle. "

    "Dokümanda bulunmayan bir bilgiyi kesinmiş gibi üretme. "

    "Hava durumu sorularına cevap verme. "
    "Hava durumu sorusu gelirse bu sorunun Weather Agent tarafından "
    "ele alınması gerektiğini kısa şekilde belirt."
)


async def create_docs_agent():
    docs_llm = ChatOpenRouter(
        model="anthropic/claude-haiku-4.5",
        api_key=OPENROUTER_API_KEY,
        temperature=0,
        max_tokens=1000
    )

    context7_client = MultiServerMCPClient(
        {
            "context7": {
                "transport": "streamable_http",
                "url": "https://mcp.context7.com/mcp",
                "headers": {
                    "CONTEXT7_API_KEY": CONTEXT7_API_KEY
                }
            }
        }
    )

    context7_tools = await context7_client.get_tools()

    docs_agent = create_agent(
        model=docs_llm,
        tools=context7_tools,
        system_prompt=DOCS_SYSTEM_PROMPT,
        name="docs_agent"
    )

    return docs_agent