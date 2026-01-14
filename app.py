import os
import streamlit as st
from openai import OpenAI
import tempfile

from docx import Document
from PIL import Image
import pytesseract

# -----------------------------
# CONFIG
# -----------------------------
ACCESS_CODE = "8124"
MAX_ATTEMPTS = 3

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

st.set_page_config(page_title="EduGenie Assistant", layout="centered")
st.title("🎓 EduGenie Assistant")

# -----------------------------
# SESSION STATE
# -----------------------------
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if "attempts" not in st.session_state:
    st.session_state.attempts = 0

if "messages" not in st.session_state:
    st.session_state.messages = []

if "uploaded_text" not in st.session_state:
    st.session_state.uploaded_text = ""

# -----------------------------
# ACCESS CONTROL
# -----------------------------
if not st.session_state.authenticated:

    if st.session_state.attempts >= MAX_ATTEMPTS:
        st.error("🚫 Access denied. Please contact SparkMind Labs for access.")
        st.stop()

    st.info("Welcome to EduGenie Assistant! Please enter your 4-digit EduGenie Access Code.")

    code_input = st.text_input("Access Code", type="password", max_chars=4)

    if st.button("Verify Access"):
        if code_input == ACCESS_CODE:
            st.session_state.authenticated = True
            st.success("✅ Access verified! How can I help you today?")
            st.rerun()
        else:
            st.session_state.attempts += 1
            remaining = MAX_ATTEMPTS - st.session_state.attempts
            if remaining == 0:
                st.error("❌ Invalid code. Please contact SparkMind Labs.")
            else:
                st.error(f"❌ Invalid code. Attempts remaining: {remaining}")

    st.stop()

# -----------------------------
# IMAGE UPLOAD (PNG / JPG)
# -----------------------------
st.subheader("📷 Upload Image (Optional)")
uploaded_file = st.file_uploader(
    "Upload PNG or JPG image (student answer / notes / worksheet photo)",
    type=["png", "jpg", "jpeg"]
)

if uploaded_file:
    image = Image.open(uploaded_file)
    extracted_text = pytesseract.image_to_string(image)
    st.session_state.uploaded_text = extracted_text.strip()
    st.success("🖼 Image uploaded and text extracted successfully.")

# -----------------------------
# SYSTEM PROMPT
# -----------------------------
SYSTEM_PROMPT = """
You are EduGenie Teacher Assistant.

You support teachers with:
- Worksheets, quizzes, question papers
- Lesson plans, unit plans
- Student answer evaluation with feedback
- Differentiated explanations
- Administrative tasks

Rules:
- Use clear, teacher-friendly language
- Use headings, bullet points, and tables
- Always include answer keys where relevant
- Keep output printable
- Never mention AI
- Do not store student data
- No medical, legal, or psychological advice

If reference content is provided from an uploaded image, use it as context.
"""

# -----------------------------
# DISPLAY CHAT HISTORY
# -----------------------------
for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

user_input = st.chat_input("Ask EduGenie (worksheet, evaluation, lesson plan, etc.)")

# -----------------------------
# WORD FILE GENERATION
# -----------------------------
def generate_word(text):
    doc = Document()
    for line in text.split("\n"):
        doc.add_paragraph(line)

    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".docx")
    doc.save(tmp.name)
    return tmp.name

# -----------------------------
# CHAT HANDLING
# -----------------------------
if user_input:
    combined_input = user_input

    if st.session_state.uploaded_text:
        combined_input += "\n\nREFERENCE CONTENT FROM IMAGE:\n" + st.session_state.uploaded_text

    st.session_state.messages.append({"role": "user", "content": combined_input})
    st.chat_message("user").write(user_input)

    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            *st.session_state.messages
        ]
    )

    reply = response.choices[0].message.content
    st.session_state.messages.append({"role": "assistant", "content": reply})
    st.chat_message("assistant").write(reply)

    # -----------------------------
    # WORD DOWNLOAD
    # -----------------------------
    docx_path = generate_word(reply)
    with open(docx_path, "rb") as f:
        st.download_button(
            "📝 Download Output as Word File",
            f,
            file_name="EduGenie_Output.docx"
        )
