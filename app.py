import streamlit as st

from router import get_answer, ask_agent_stream

st.set_page_config(
    page_title="Weather Agent",
    page_icon="🌤️",
    layout="centered"
)

st.title("🌤️ Weather & Docs Agent")

st.write(
    "Güncel hava durumunu sorabilir veya teknik dokümantasyon "
    "hakkında bilgi alabilirsiniz."
)


if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "assistant",
            "content": "Merhaba! 👋 Güncel hava durumu ve teknik dokümantasyon sorularınızda yardımcı olabilirim. Ne öğrenmek istersiniz?"
        }
    ]


for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])


user_question = st.chat_input("Bir şehir veya teknik dokümantasyon sorusu yazın...")

if user_question:
    st.session_state.messages.append(
        {
            "role": "user",
            "content": user_question
        }
    )

    with st.chat_message("user"):
        st.markdown(user_question)

    with st.chat_message("assistant"):

        with st.spinner("Cevabınız hazırlanıyor, lütfen bekleyin..."):
            answer_text = get_answer(user_question)

        stream = ask_agent_stream(answer_text)

        answer = st.write_stream(stream)


    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": answer
        }
    )