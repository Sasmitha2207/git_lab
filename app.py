
import streamlit as st
from pypdf import PdfReader
from docx import Document
from google import genai

st.set_page_config(page_title="Mini LLM", page_icon="🤖")

st.title("🤖 My Mini LLM")
st.write("Upload a document and ask Gemini questions!")

api_key = st.sidebar.text_input(
    "Enter Gemini API Key", type="password"
)

uploaded_file = st.file_uploader(
    "Upload PDF, DOCX or TXT",
    type=["pdf", "docx", "txt"]
)

def extract_text(file):
    name = file.name.lower()

    if name.endswith(".pdf"):
        reader = PdfReader(file)
        return "\n".join(
            page.extract_text() or "" for page in reader.pages
        )

    elif name.endswith(".docx"):
        doc = Document(file)
        return "\n".join(p.text for p in doc.paragraphs)

    elif name.endswith(".txt"):
        return file.getvalue().decode("utf-8", errors="replace")

    return ""

if uploaded_file:
    text = extract_text(uploaded_file)

    if text.strip():
        st.success("Document uploaded successfully!")
        st.write("Characters extracted:", len(text))

        question = st.text_input("Ask your question")

        if st.button("Get Answer"):
            if not api_key:
                st.error("Enter your Gemini API key!")
            elif not question:
                st.warning("Enter a question!")
            else:
                try:
                    client = genai.Client(api_key=api_key)

                    prompt = f"""
                    Answer using only this document.
                    If the answer is not available,
                    say you cannot find it.

                    DOCUMENT:
                    {text[:30000]}

                    QUESTION:
                    {question}
                    """

                    with st.spinner("Gemini is thinking..."):
                        try:
                            response = client.models.generate_content(
                                model="gemini-3.8-flash",
                                contents=prompt
                            )

                        except Exception:
                            response = client.models.generate_content(
                                model="gemini-3.5-flash-lite",
                                contents=prompt
                            )

                    st.subheader("Answer")
                    st.write(response.text)

                except Exception as e:
                    st.error(f"Error: {e}")
    else:
        st.error("No readable text found in this document.")
