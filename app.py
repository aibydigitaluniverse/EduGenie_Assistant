import os
import streamlit as st
from openai import OpenAI

# -----------------------------
# CONFIG
# -----------------------------
ACCESS_CODE = "8124"
MAX_ATTEMPTS = 3

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

st.set_page_config(page_title="EduGenie Assistant", layout="centered")
st.title("🎓 EduGenie Assistant")

# -----------------------------
# SESSION STATE INIT
# -----------------------------
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if "attempts" not in st.session_state:
    st.session_state.attempts = 0

if "messages" not in st.session_state:
    st.session_state.messages = []

# -----------------------------
# ACCESS CONTROL UI
# -----------------------------
if not st.session_state.authenticated:

    # If max attempts exceeded
    if st.session_state.attempts >= MAX_ATTEMPTS:
        st.error(
            "🚫 Access denied. Please reach out to SparkMind Labs to obtain a valid access code."
        )
        st.stop()

    st.info(
        "Welcome to EduGenie Assistant! Please enter your 4-digit EduGenie Access Code."
    )

    code_input = st.text_input(
        "Access Code",
        type="password",
        max_chars=4
    )

    if st.button("Verify Access"):
        if code_input == ACCESS_CODE:
            st.session_state.authenticated = True
            st.success("✅ Access verified! How can I help you today?")
        else:
            st.session_state.attempts += 1
            remaining = MAX_ATTEMPTS - st.session_state.attempts

            if remaining == 0:
                st.error(
                    "❌ The access code you entered is invalid. Please contact SparkMind Labs to request access."
                )
            else:
                st.error(
                    f"❌ The access code you entered is invalid. Attempts remaining: {remaining}"
                )

    st.stop()

# -----------------------------
# SYSTEM PROMPT
# -----------------------------
SYSTEM_PROMPT = """
You are EduGenie Teacher Assistant, an AI designed to save teachers time and support them in planning,
assessment, and classroom management. You act as a reliable teaching co-pilot.

CORE PURPOSE:
Support teachers with content creation, grading guidance, lesson planning, classroom activities,
student support, administrative tasks, and academic content transformation.

STYLE & BEHAVIOR RULES:
- Use clear, simple, teacher-friendly language.
- Use headings, bullet points, and tables.
- Always include answer keys for worksheets, quizzes, and exams.
- Keep formatting printable and clean.
- Avoid copyrighted textbook content.
- Never mention that this is AI-generated.
- Maintain a professional, supportive tone.

WORKFLOW:
1. Understand the teacher's request.
2. Structure output clearly.
3. Add answer keys where appropriate.
4. Offer optional enhancements.
5. Ask only one follow-up question if absolutely required.

RESTRICTIONS:
- Do not generate medical, legal, or psychological advice.
- Do not infer or store student personal data.
- Redirect sensitive wellbeing cases to school counselors.
"""

# -----------------------------
# CHAT INTERFACE
# -----------------------------
for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

user_input = st.chat_input(
    "Ask EduGenie to create a worksheet, lesson plan, evaluation, etc."
)

if user_input:
    st.session_state.messages.append(
        {"role": "user", "content": user_input}
    )
    st.chat_message("user").write(user_input)

    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            *st.session_state.messages
        ]
    )

    reply = response.choices[0].message.content

    st.session_state.messages.append(
        {"role": "assistant", "content": reply}
    )
    st.chat_message("assistant").write(reply)
