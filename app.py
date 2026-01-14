import os
import streamlit as st
from openai import OpenAI
from fpdf import FPDF
import tempfile
from PIL import Image
import pytesseract
import PyPDF2

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
            st.error(
                "❌ Invalid access code."
                if remaining == 0
                else f"❌ Invalid code. Attempts remaining: {remaining}"
            )

    st.stop()

# -----------------------------
# FILE UPLOAD (PDF / IMAGE)
# -----------------------------
st.subheader("📂 Upload Reference File (Optional)")
uploaded_file = st.file_uploader(
    "Upload a PDF or image (worksheet, student answer, notes)",
    type=["pdf", "png", "jpg", "jpeg"]
)

if uploaded_file:
    extracted_text = ""

    if uploaded_file.type == "application/pdf":
        reader = PyPDF2.PdfReader(uploaded_file)
        for page in reader.pages:
            extracted_text += page.extract_text() or ""

    else:
        image = Image.open(uploaded_file)
        extracted_text = pytesseract.image_to_string(image)

    st.session_state.uploaded_text = extracted_text.strip()
    st.success("📄 File uploaded and text extracted successfully.")

# -----------------------------
# SYSTEM PROMPT
# -----------------------------
SYSTEM_PROMPT = """
You are EduGenie Teacher Assistant.

You help teachers with:
- Worksheets, quizzes, question papers
- Lesson plans, unit plans
- Student answer evaluation
- Differentiated explanations
- Administrative tasks

Rules:
- Always teacher-friendly language
- Use headings, bullet points, tables
- Always include answer keys where relevant
- Keep output printable
- Never mention AI
- No student data storage
- No medical or legal advice

If a reference document is provided, use it as the primary context.
"""

# -----------------------------
# CHAT HISTORY
# -----------------------------
for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

user_input = st.chat_input("Ask EduGenie (worksheet, evaluation, lesson plan, etc.)")

# -----------------------------
# PDF CREATION FUNCTION
# -----------------------------
def generate_pdf(text):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.set_auto_page_break(auto=True, margin=15)

    for line in text.split("\n"):
        pdf.multi_cell(0, 8, line)

    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
    pdf.output(tmp.name)
    return tmp.name

# -----------------------------
# CHAT HANDLING
# -----------------------------
if user_input:
    combined_input = user_input

    if st.session_state.uploaded_text:
        combined_input += "\n\nREFERENCE CONTENT:\n" + st.session_state.uploaded_text

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
    # PDF DOWNLOAD
    # -----------------------------
    pdf_path = generate_pdf(reply)
    with open(pdf_path, "rb") as f:
        st.download_button(
            "📥 Download Output as PDF",
            data=f,
            file_name="EduGenie_Output.pdf",
            mime="application/pdf"
        )
