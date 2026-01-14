import os
import streamlit as st
from openai import OpenAI
import tempfile
import base64

from docx import Document

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

if "image_context" not in st.session_state:
    st.session_state.image_context = ""

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
# IMAGE UPLOAD (OPENAI VISION)
# -----------------------------
st.subheader("📷 Upload Image (Optional)")
uploaded_image = st.file_uploader(
    "Upload PNG or JPG (student answer / worksheet / notes)",
    type=["png", "jpg", "jpeg"]
)

if uploaded_image:
    image_bytes = uploaded_image.read()
    encoded_image = base64.b64encode(image_bytes).decode("utf-8")

    vision_prompt = (
        "Extract and summarize the educational content from this image. "
        "If it is a student's answer, extract the answer clearly. "
        "If it is a worksheet or notes, extract the text accurately."
    )

    vision_response = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": vision_prompt},
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{encoded_image}"
                        },
                    },
                ],
            }
        ],
    )

    extracted_text = vision_response.choices[0].message.content
    st.session_state.image_context = extracted_text
    st.success("🖼 Image processed successfully using AI.")

# -----------------------------
# SYSTEM PROMPT
# -----------------------------
SYSTEM_PROMPT = """
You are EduGenie Teacher Assistant.

You help teachers with:
- Worksheets, quizzes, question papers
- Lesson plans, unit plans
- Student answer evaluation with feedback
- Differentiated explanations
- Administrative tasks

Rules:
- Use simple, teacher-friendly language
- Use headings, bullet points, tables
- Always include answer keys where relevant
- Keep output printable
- Never mention AI
- Do not store student data
- No medical, legal, or psychological advice

If image-based reference content is provided, use it as context.
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

    if st.session_state.image_context:
        combined_input += "\n\nREFERENCE CONTENT FROM IMAGE:\n" + st.session_state.image_context

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
