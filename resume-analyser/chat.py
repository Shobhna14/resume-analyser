import os
import streamlit as st
import pdfplumber
from docx import Document
from PIL import Image
import pytesseract
import requests
from dotenv import load_dotenv

load_dotenv()

# Groq API configuration
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# Configure Tesseract path (if needed)
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
# pytesseract.pytesseract.tesseract_cmd = r'/usr/bin/tesseract'
def extract_text_from_pdf(pdf_file):
    """Extract text from a PDF file."""
    try:
        with pdfplumber.open(pdf_file) as pdf:
            return " ".join(page.extract_text() for page in pdf.pages)
    except Exception as e:
        st.error(f"Error extracting text from PDF: {str(e)}")
        return ""

def extract_text_from_docx(docx_file):
    """Extract text from a DOCX file."""
    try:
        doc = Document(docx_file)
        return " ".join([para.text for para in doc.paragraphs])
    except Exception as e:
        st.error(f"Error extracting text from DOCX: {str(e)}")
        return ""

def extract_text_from_image(image_file):
    """Extract text from an image using OCR."""
    try:
        image = Image.open(image_file)
        text = pytesseract.image_to_string(image)
        return text
    except Exception as e:
        st.error(f"Error extracting text from image: {str(e)}")
        return ""

def query_groq_llm(job_desc, resume_text):
    """Query Groq LLM to analyze the resume and job description."""
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "llama-3.3-70b-versatile",
        "messages": [
            {
                "role": "system",
                "content": """
                You are a professional job matcher. Analyze the match between job requirements and candidate qualifications.
                Focus only on concrete, verifiable information present in both documents.
                Provide the analysis in the following structured format:

                ### Resume Analysis:

                **List Format Analysis:**

                - "Education_Level": "[Education level mentioned in resume]",
                - "Relevant_Experience": "[Match Percentage]%",
                - "Skills_Match": "[Match Percentage]%",
                - "Relevant_Projects": "[Mentioned projects relevant to the job]",
                - "Location": "[Candidate location if available in structured form (e.g., Vallabhnagar, Udaipur, Rajasthan) (not where they worked)]",
                - "Confidence_Score": "[Overall match confidence score in percentage]",
                - "Stability_Score":  "[If only internships → '30%', otherwise evaluate job duration: Lower if <1 year in multiple jobs, higher if 2+ years]"
                - "Salary_Range": "[Expected or mentioned salary if available]"
                **Summary:**
                - [Provide a brief summary of the analysis in 100 words]
                """
            },

            {
                "role": "user",
                "content": f"""
                Job Requirements:
                {job_desc}

                Resume:
                {resume_text}
                """
            }
        ],
        "temperature": 0.3,
        "max_tokens": 1500
    }

    try:
        response = requests.post(GROQ_API_URL, json=payload, headers=headers)
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"]
    except Exception as e:
        return f"Error generating analysis. Please try again. Error: {str(e)}"

def main():
    st.title("Resume Scan Chatbot")

    # Input fields
    resume_file = st.file_uploader("Upload Resume (PDF, DOCX, or Image)", type=["pdf", "docx", "doc", "png", "jpg", "jpeg"])
    job_desc = st.text_area("Job Description/Requirements", height=100)

    if resume_file and job_desc:
        resume_text = ""
        file_extension = resume_file.name.split(".")[-1].lower()

        # Extract text based on file type
        if file_extension == "pdf":
            resume_text = extract_text_from_pdf(resume_file)
        elif file_extension in ["docx", "doc"]:
            resume_text = extract_text_from_docx(resume_file)
        elif file_extension in ["png", "jpg", "jpeg"]:
            resume_text = extract_text_from_image(resume_file)
        else:
            st.error("Unsupported file format. Please upload a PDF, DOCX, or image file.")
            return

        if resume_text:
            # Analyze resume and job description using Groq LLM
            analysis = query_groq_llm(job_desc, resume_text)



            st.write(analysis)

if __name__ == "__main__":
    main()