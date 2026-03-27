import app as st
import fitz
from docx import Document
from model import JobRecommendationSystem

import pytesseract
from PIL import Image
import cv2
import numpy as np

pytesseract.pytesseract.tesseract_cmd = r"C:/Program Files/Tesseract-OCR/tesseract.exe"

# ---------- PAGE CONFIG ----------
st.set_page_config(
    page_title="AI Job Recommendation System",
    layout="wide"
)

# ---------- STYLING ----------
st.markdown("""
<style>

.stApp {
background: linear-gradient(135deg,#0f2027,#203a43,#2c5364);
color:white;
}

.score-high { color:#00ff9f; font-weight:bold; }
.score-mid { color:#ffc107; font-weight:bold; }
.score-low { color:#ff4d4d; font-weight:bold; }

.feature-card {
    background: linear-gradient(145deg, #1c2b3a, #243b55);
    padding: 20px;
    border-radius: 15px;
    text-align: center;
    height: 180px;
    box-shadow: 0px 4px 15px rgba(0,0,0,0.4);
    transition: transform 0.2s ease;
}

.feature-card:hover { transform: scale(1.05); }

.feature-title {
    font-size: 22px;
    font-weight: bold;
    margin-top: 10px;
}

.feature-desc {
    font-size: 16px;
    color: #cfd8dc;
    margin-top: 8px;
}

.apply-btn {
    background: linear-gradient(90deg, #00c6ff, #0072ff);
    color: white;
    border: none;
    padding: 8px 16px;
    border-radius: 8px;
    cursor: pointer;
    font-size: 14px;
    margin-top: 10px;
}

.apply-btn:hover {
    opacity: 0.9;
    transform: scale(1.05);
}

</style>
""", unsafe_allow_html=True)

# ---------- LOAD MODEL ----------
@st.cache_resource
def load_model():
    return JobRecommendationSystem("Naukri Jobs Data.csv")

recommender = load_model()

# ---------- TITLE ----------
st.title("AI Job Recommendation System")
st.write("Upload your resume to discover relevant job roles.")

# ---------- FEATURE SECTION ----------
st.markdown("### 🚀 What This System Can Do")

col1, col2, col3, col4 = st.columns(4)

features = [
    ("Smart Resume Analysis", "Extracts and understands your resume using NLP & AI models"),
    ("Accurate Job Matching", "Matches your profile with relevant jobs using semantic similarity"),
    ("Match Score", "Shows how well your resume fits each role with percentage scoring"),
    ("Instant Results", "Get top job recommendations instantly after uploading resume")
]

for col, (title, desc) in zip([col1, col2, col3, col4], features):
    with col:
        st.markdown(f"""
        <div class="feature-card">
            <div class="feature-title">{title}</div>
            <div class="feature-desc">{desc}</div>
        </div>
        """, unsafe_allow_html=True)

# ✅ Proper spacing BELOW cards
st.markdown("<div style='margin-bottom: 50px;'></div>", unsafe_allow_html=True)

# ---------- SESSION STATE ----------
if "role_selected" not in st.session_state:
    st.session_state.role_selected = None

if "grouped_jobs" not in st.session_state:
    st.session_state.grouped_jobs = None

def reset_recommendations():
    st.session_state.grouped_jobs = None
    st.session_state.role_selected = None

# ---------- FILE UPLOADER ----------
uploaded_file = st.file_uploader(
    "Upload Resume",
    type=["pdf", "docx", "jpg", "jpeg", "png"],
    on_change=reset_recommendations
)

# ---------- TEXT EXTRACTION ----------
def extract_pdf(file):
    doc = fitz.open(stream=file.read(), filetype="pdf")
    return "".join([page.get_text() for page in doc])

def extract_docx(file):
    doc = Document(file)
    return "\n".join([para.text for para in doc.paragraphs])

def extract_image(file):
    image = Image.open(file)
    img = np.array(image)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    thresh = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY)[1]
    return pytesseract.image_to_string(thresh)

resume_text = ""

if uploaded_file:
    file_name = uploaded_file.name.lower()

    if file_name.endswith("pdf"):
        resume_text = extract_pdf(uploaded_file)
    elif file_name.endswith("docx"):
        resume_text = extract_docx(uploaded_file)
    elif file_name.endswith(("jpg", "jpeg", "png")):
        resume_text = extract_image(uploaded_file)

# ---------- RECOMMEND ----------
if st.button("Get Job Recommendations"):

    if resume_text == "":
        st.warning("Please upload a valid resume")

    else:
        with st.spinner("Analyzing resume..."):

            jobs = recommender.recommend_jobs(resume_text)
            jobs = jobs.sort_values(by="match_score", ascending=False)

            grouped = recommender.group_jobs_by_role(jobs)

            st.session_state.grouped_jobs = grouped
            st.session_state.role_selected = None

# ---------- ROLE VIEW ----------
if st.session_state.grouped_jobs and st.session_state.role_selected is None:

    st.subheader("Recommended Job Roles")

    cols = st.columns(3)
    roles = list(st.session_state.grouped_jobs.keys())

    for i, role in enumerate(roles):
        count = len(st.session_state.grouped_jobs[role])

        with cols[i % 3]:
            if st.button(f"{role} ({count} jobs)"):
                st.session_state.role_selected = role
                st.rerun()

# ---------- COMPANY VIEW ----------
if st.session_state.role_selected:

    role = st.session_state.role_selected
    st.subheader(f"{role} Opportunities")

    if st.button("⬅ Back to Roles"):
        st.session_state.role_selected = None
        st.rerun()

    jobs = st.session_state.grouped_jobs[role]

    for job in jobs:

        score = round(float(job.get("match_score", 0)), 2)

        if score >= 60:
            score_class = "score-high"
        elif score >= 40:
            score_class = "score-mid"
        else:
            score_class = "score-low"

        with st.expander(f"{job['company']} — {job['location']}"):

            st.markdown(
                f"<p class='{score_class}'>Match Score: {score}%</p>",
                unsafe_allow_html=True
            )

            st.progress(int(score))

            st.write(f"**Job Title:** {role}")
            st.write(f"**Experience Required:** {job['experience']}")
            st.write(f"**Salary Offered:** {job['salary']}")

            # 🔗 APPLY BUTTON
            # ---------- LINKS ----------
            job_link = job.get("job_link", "")
            company_link = job.get("company_link", "")
            glassdoor_link = job.get("glassdoor_link", "")

            # Create 3 columns for buttons
            btn1, btn2, btn3 = st.columns(3)

            with btn1:
                if job_link:
                    st.markdown(
                        f"""
                        <a href="{job_link}" target="_blank">
                            <button class="apply-btn">🔗 Apply</button>
                        </a>
                        """,
                        unsafe_allow_html=True
                    )

            with btn2:
                if company_link:
                    st.markdown(
                        f"""
                        <a href="{company_link}" target="_blank">
                            <button class="apply-btn">🏢 Company Info</button>
                        </a>
                        """,
                        unsafe_allow_html=True
                    )

            with btn3:
                if glassdoor_link:
                    st.markdown(
                        f"""
                        <a href="{glassdoor_link}" target="_blank">
                            <button class="apply-btn">⭐ Reviews</button>
                        </a>
                        """,
                        unsafe_allow_html=True
                    )

            st.markdown("**Required Skills**")

            skills_raw = job["skills"]

            if not skills_raw or str(skills_raw).lower() == "nan":
                st.markdown("*No skills data available*")
            else:
                skills = [skill.strip() for skill in str(skills_raw).split(",") if skill.strip()]

                cols = st.columns(6)

                for i, skill in enumerate(skills):
                    with cols[i % 6]:
                        st.markdown(
                            f"""
                            <div style="
                                background:#1e1e1e;
                                padding:6px;
                                border-radius:20px;
                                text-align:center;
                                font-size:13px;
                            ">
                                {skill}
                            </div>
                            """,
                            unsafe_allow_html=True
                        )

            st.markdown("**Job Summary**")
            st.write(job['description'])