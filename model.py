import string
import numpy as np
import faiss
import pandas as pd
import torch
import os
import urllib.parse   # ✅ NEW

from sentence_transformers import SentenceTransformer
from sklearn.feature_extraction.text import TfidfVectorizer


MODEL = SentenceTransformer("paraphrase-MiniLM-L6-v2", device="cpu")

MODEL = torch.quantization.quantize_dynamic(
    MODEL,
    {torch.nn.Linear},
    dtype=torch.qint8
)


class JobRecommendationSystem:

    def __init__(self, jobs_csv):

        self.jobs_df = pd.read_csv(jobs_csv)

        # ---------- CLEAN DATA ----------
        self.jobs_df = self.jobs_df.drop_duplicates()

        self.jobs_df = self.jobs_df[
            self.jobs_df["job_description"].notna()
        ]

        self.jobs_df = self.jobs_df[
            self.jobs_df["job_description"].str.len() > 50
        ]

        # ---------- CREATE JOB TEXT ----------
        self.jobs_df["job_text"] = (
            self.jobs_df["job_post"].astype(str) + " " +
            self.jobs_df["required_skills"].astype(str) + " " +
            self.jobs_df["job_description"].astype(str) + " " +
            self.jobs_df["job_location"].astype(str) + " " +
            self.jobs_df["company"].astype(str)
        )

        self.jobs_texts = self.jobs_df["job_text"].tolist()
        self.job_info = self.jobs_df.copy()

        # ---------- EMBEDDINGS ----------
        if os.path.exists("job_embeddings.npy") and os.path.exists("jobs.index"):

            self.job_embeddings = np.load("job_embeddings.npy")
            faiss.normalize_L2(self.job_embeddings)
            self.index = faiss.read_index("jobs.index")

        else:

            print("Generating embeddings...")

            self.job_embeddings = MODEL.encode(
                self.jobs_texts,
                convert_to_numpy=True
            ).astype(np.float32)

            faiss.normalize_L2(self.job_embeddings)

            self.dim = self.job_embeddings.shape[1]

            self.index = faiss.IndexFlatIP(self.dim)
            self.index.add(self.job_embeddings)

            np.save("job_embeddings.npy", self.job_embeddings)
            faiss.write_index(self.index, "jobs.index")

        # ---------- TFIDF ----------
        self.vectorizer = TfidfVectorizer()
        self.job_vectors = self.vectorizer.fit_transform(self.jobs_texts)


    def clean_text(self, text):
        return text.lower().translate(
            str.maketrans("", "", string.punctuation)
        ).strip()


    def filter_top_jobs(self, resume_text, top_n=200):

        resume_vector = self.vectorizer.transform([resume_text])

        similarity_scores = (
            self.job_vectors @ resume_vector.T
        ).toarray().flatten()

        top_indices = np.argsort(similarity_scores)[-top_n:]

        return (
            self.job_embeddings[top_indices],
            self.job_info.iloc[top_indices].reset_index(drop=True)
        )


    def recommend_jobs(self, resume_text, top_n=20):

        resume_text = self.clean_text(resume_text)

        filtered_embeddings, filtered_info = self.filter_top_jobs(resume_text)

        faiss.normalize_L2(filtered_embeddings)

        dim = filtered_embeddings.shape[1]

        temp_index = faiss.IndexFlatIP(dim)
        temp_index.add(filtered_embeddings)

        resume_embedding = MODEL.encode(
            [resume_text],
            convert_to_numpy=True
        ).astype(np.float32)

        faiss.normalize_L2(resume_embedding)

        D, I = temp_index.search(resume_embedding, top_n)

        recommended_jobs = filtered_info.iloc[I[0]].copy()

        scores = D[0]
        match_scores = np.round(scores * 100, 2)

        recommended_jobs["match_score"] = match_scores

        return recommended_jobs


    # ---------- 🔥 UPDATED GROUP FUNCTION ----------
    def group_jobs_by_role(self, jobs_df):

        grouped = {}

        for _, row in jobs_df.iterrows():

            role = row["job_post"]

            if role not in grouped:
                grouped[role] = []

            # ---------- JOB LINK ----------
            if "job_link" in row and pd.notna(row["job_link"]):
                job_link = str(row["job_link"])
            else:
                query = f"{row['job_post']} {row['company']} job"
                job_link = "https://www.google.com/search?q=" + urllib.parse.quote(query)

            # ---------- COMPANY INFO ----------
            company_query = f"{row['company']} company profile"
            company_link = "https://www.google.com/search?q=" + urllib.parse.quote(company_query)

            # ---------- GLASSDOOR ----------
            glassdoor_query = f"{row['company']} glassdoor reviews"
            glassdoor_link = "https://www.google.com/search?q=" + urllib.parse.quote(glassdoor_query)

            grouped[role].append({
                "company": str(row["company"]),
                "location": str(row["job_location"]),
                "skills": str(row["required_skills1"]),
                "description": str(row["job_description"]),
                "experience": str(row["exp_required"]),
                "salary": str(row["salary_offered"]),
                "match_score": round(float(row.get("match_score", 0)), 2),

                # ✅ NEW LINKS
                "job_link": job_link,
                "company_link": company_link,
                "glassdoor_link": glassdoor_link
            })

        return grouped