---

title: AI-Powered Job Recommendation System
emoji: 🤖
colorFrom: blue
colorTo: purple
sdk: streamlit
sdk_version: "1.31.0"
app_file: app.py
pinned: false
-------------

# 🤖 AI-Powered Job Recommendation System

An intelligent job recommendation system that analyzes a user's resume and suggests the most relevant job roles using Natural Language Processing (NLP) and Machine Learning techniques.

---

## 🚀 Features

* 📄 Upload resumes in **PDF** or **DOCX** format
* 🧠 Extract and process resume text automatically
* 🔍 Generate semantic embeddings using **Sentence Transformers**
* 📊 Recommend top matching job roles based on similarity
* 🎨 Clean and interactive **Streamlit UI**
* ⚡ Fast and efficient recommendations with caching

---

## 🧠 How It Works

1. **Resume Upload**
   User uploads a resume (PDF/DOCX)

2. **Text Extraction**

   * PDF → PyMuPDF
   * DOCX → python-docx

3. **Text Processing & Embedding**

   * Convert resume text into vector embeddings using `sentence-transformers`

4. **Job Matching**

   * Compare resume embeddings with job dataset embeddings
   * Use cosine similarity to find best matches

5. **Top Recommendations**

   * Display top job roles with highest similarity scores

---

## 🛠️ Tech Stack

* **Frontend/UI:** Streamlit
* **Backend:** Python
* **Machine Learning:**

  * Sentence Transformers
  * Scikit-learn
* **Data Processing:** Pandas, NumPy
* **File Handling:** PyMuPDF, python-docx, Pillow

---

## 📁 Project Structure

```
job-recommendation-system/
│
├── app.py                 # Streamlit frontend
├── model.py               # ML model & recommendation logic
├── JobsFE.csv             # Job dataset
├── requirements.txt       # Dependencies
└── README.md              # Project documentation
```

---

## ⚙️ Installation (Local Setup)

```bash
git clone https://github.com/your-username/job-recommendation-system.git
cd job-recommendation-system
pip install -r requirements.txt
streamlit run app.py
```

---

## 🌐 Deployment

This project is deployed using **Hugging Face Spaces** with Streamlit.

👉 Open the app in your browser and upload a resume to get recommendations instantly.

---

## ⚠️ Limitations

* Performance depends on resume text quality
* Large models may increase loading time
* OCR-based image resume parsing is not included in this version

---

## 🔮 Future Improvements

* Add OCR support for image-based resumes
* Improve recommendation accuracy with fine-tuned models
* Add skill extraction and visualization
* Deploy scalable backend with API support

---

## 👨‍💻 Author

**KAS**
Computer Science Engineering Student

---

## 📜 License

This project is licensed under the MIT License.

---

## ⭐ Acknowledgment

This project is built as part of an academic initiative to explore real-world applications of Machine Learning and NLP in job recommendation systems.
