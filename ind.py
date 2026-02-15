import os
import streamlit as st
from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage, HumanMessage
from fpdf import FPDF

# ------------------ API KEY CHECK ------------------
assert "GROQ_API_KEY" in os.environ, "Set GROQ_API_KEY in environment"

# ------------------ LLM INIT ------------------
llm = ChatGroq(
    model="llama-3.1-8b-instant",
    temperature=0
)

# ------------------ APP UI ------------------
st.set_page_config(page_title="StudyGenie", page_icon="📘")
st.title("StudyGenie")

# ------------------ SESSION STATE ------------------
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# ------------------ DISPLAY CHAT ------------------
for msg in st.session_state.chat_history:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# ------------------ USER INPUT ------------------
user_input = st.chat_input("Ask anything...")

if user_input:
    with st.chat_message("user"):
        st.markdown(user_input)

    st.session_state.chat_history.append(
        {"role": "user", "content": user_input}
    )

    messages = [
        SystemMessage(content="You are a helpful educational assistant."),
        HumanMessage(content=user_input)
    ]

    response = llm.invoke(messages)

    with st.chat_message("assistant"):
        st.markdown(response.content)

    st.session_state.chat_history.append(
        {"role": "assistant", "content": response.content}
    )

# ------------------ PDF FUNCTIONS ------------------
def safe_text(text):
    return text.encode("latin-1", "replace").decode("latin-1")

def create_pdf(chat_history):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    pdf.multi_cell(0, 10, "StudyGenie Chat History\n")
    pdf.ln(5)

    for msg in chat_history:
        role = msg["role"].upper()
        content = safe_text(msg["content"])
        pdf.multi_cell(0, 8, f"{role}: {content}")
        pdf.ln(2)

    file_path = "studygenie_chat.pdf"
    pdf.output(file_path)
    return file_path

# ------------------ DOWNLOAD BUTTON ------------------
if st.session_state.chat_history:
    pdf_file = create_pdf(st.session_state.chat_history)

    with open(pdf_file, "rb") as f:
        st.download_button(
            label="📄 Download Chat as PDF",
            data=f,
            file_name="studygenie_chat.pdf",
            mime="application/pdf"
        )
