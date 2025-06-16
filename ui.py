import streamlit as st
import fitz  # For reading PDFs
import tempfile
import os
from generator import generate_flashcards, parse_flashcards

st.set_page_config(page_title="Flashcard Generator", layout="centered")
st.title("🧠 Flashcard Generator (Ollama + Phi3)")

option = st.radio("Choose your input method:", ["✍️ Direct Paste", "📂 Upload File"])

content = ""
subject = st.text_input("Optional Subject (to help the model, e.g., Biology):")

# --- Handle Direct Paste ---
if option == "✍️ Direct Paste":
    content = st.text_area("Enter your content here:", height=300)

# --- Handle File Upload (.txt or .pdf) ---
elif option == "📂 Upload File":
    uploaded_file = st.file_uploader("Upload a .txt or .pdf file", type=["txt", "pdf"])
    if uploaded_file is not None:
        file_name = uploaded_file.name
        if file_name.endswith(".txt"):
            content = uploaded_file.read().decode("utf-8")
        elif file_name.endswith(".pdf"):
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
                tmp.write(uploaded_file.read())
                tmp_path = tmp.name
            doc = fitz.open(tmp_path)
            content = "\n".join([page.get_text() for page in doc])
            os.remove(tmp_path)
        st.text_area("📄 File Preview", content[:1000], height=200)

# --- Generate Flashcards ---
if st.button("Generate Flashcards") and content.strip():
    with st.spinner("Generating flashcards..."):
        raw_output = generate_flashcards(content, subject)
        st.text_area("LLM response",raw_output,height=300)
        flashcards = parse_flashcards(raw_output)

    if flashcards:
        st.success(f"✅ Generated {len(flashcards)} flashcards!")
        for i, card in enumerate(flashcards, 1):
            st.markdown(f"**Q{i}:** {card['question']}")
            st.markdown(f"**A{i}:** {card['answer']}")
            st.markdown(f"Difficulty: {card['difficulty']}")
            st.markdown("---")
    else:
        st.error("⚠️ No flashcards found in the model response.")

