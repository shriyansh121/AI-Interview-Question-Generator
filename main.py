import streamlit as st
import json
from pathlib import Path
import tempfile

from src.agent.interview_agent import InterviewAgent

# -------------------------------
# PAGE CONFIG
# -------------------------------
st.set_page_config(
    page_title="AI Interview Question Generator",
    layout="wide",
)

st.title("🎯 AI Interview Question Generator")
st.caption("Upload a resume → get role-specific interview questions")

st.divider()


# -------------------------------
# AGENT INIT (CACHE)
# -------------------------------
@st.cache_resource
def load_agent():
    return InterviewAgent()


agent = load_agent()


# -------------------------------
# FILE UPLOAD
# -------------------------------
uploaded_file = st.file_uploader(
    "Upload Resume (PDF, DOCX, or TXT)",
    type=["pdf", "docx", "txt"],
)


# -------------------------------
# RUN BUTTON
# -------------------------------
if uploaded_file:
    if st.button("🚀 Generate Interview Questions"):
        with st.spinner("Processing resume..."):
            # Save uploaded file to temp location
            suffix = Path(uploaded_file.name).suffix
            with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
                tmp.write(uploaded_file.read())
                resume_path = tmp.name

            # Run agent
            result = agent.run(resume_path)

        # -------------------------------
        # ERROR HANDLING
        # -------------------------------
        if result["status"] != "completed":
            st.error("❌ Failed to process resume")
            st.write(result.get("error"))
            st.stop()

        candidate = result["candidate_info"]
        questions = result["questions"]

        # -------------------------------
        # CANDIDATE SUMMARY
        # -------------------------------
        st.success("✅ Resume processed successfully")

        st.subheader("👤 Candidate Summary")
        col1, col2 = st.columns(2)

        with col1:
            st.write("**Name:**", candidate.get("name", "Unknown"))
            st.write("**Role:**", candidate.get("job_role", "Unknown"))
            st.write("**Experience:**", candidate.get("experience", "Unknown"))

        with col2:
            st.write("**Email:**", candidate.get("email", "N/A"))
            st.write("**Phone:**", candidate.get("phone", "N/A"))

        skills = candidate.get("skills", [])
        if skills:
            st.markdown("**Skills:**")
            st.write(", ".join(skills))

        st.divider()

        # -------------------------------
        # QUESTIONS
        # -------------------------------
        st.subheader("📝 Generated Interview Questions")

        for i, q in enumerate(questions, 1):
            with st.expander(f"{i}. {q['type'].capitalize()} Question", expanded=False):
                st.write("**Question:**")
                st.write(q["question"])
                st.write("**Evaluating:**")
                st.write(q["evaluating"])

        st.divider()

        # -------------------------------
        # DOWNLOAD JSON
        # -------------------------------
        output_json = {
            "candidate_info": candidate,
            "questions": questions,
        }

        st.download_button(
            label="⬇️ Download Questions as JSON",
            data=json.dumps(output_json, indent=2),
            file_name="interview_questions.json",
            mime="application/json",
        )

else:
    st.info("⬆️ Upload a resume to get started")
