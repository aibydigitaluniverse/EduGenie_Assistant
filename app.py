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

    if st.session_state.attempts >= MAX_ATTEMPTS:
        st.error(
           if remaining == 0:
    st.error("❌ The access code you entered is invalid. Please contact SparkMind Labs to request access.")
else:
    st.error(f"❌ The access code you entered is invalid. Attempts remaining: {remaining}")

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
            st.error(
                f"❌ The access code you entered is invalid. "
                f"{'Please contact Spark
