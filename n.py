import os
import streamlit as st
import pdfplumber
import requests
from docx import Document
from PIL import Image
import pytesseract
import io
from dotenv import load_dotenv

load_dotenv()

# Groq API configuration
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"
GROQ_API_KEY = os.getenv("GROQ_API_KEY")


# pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

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
        "model": "mixtral-8x7b-32768",
        "messages": [
            {
                "role": "system",
                "content": """
                You are a professional job matcher. Analyze the match between job requirements and candidate qualifications.
                Focus only on concrete, verifiable information present in both documents.
                Do not make assumptions or infer information not explicitly stated.
                Provide a concise 50-word summary of the resume's compatibility with the job, including:
                1. Matching skills
                2. Missing requirements
                3. Experience match
                4. Overall compatibility score (0-100%)
                """
            },
            {
                "role": "user",
                "content": f"""
                Job Description:
                {job_desc}

                Resume:
                {resume_text}
                """
            }
        ],
        "temperature": 0.3,  # Lower temperature for more focused responses
        "max_tokens": 500
    }

    try:
        response = requests.post(GROQ_API_URL, json=payload, headers=headers)
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"]
    except Exception as e:
        return f"Error generating analysis. Please try again. Error: {str(e)}"

def main():
    st.title("Job Matching with AI")

    # Input fields
    resume_file = st.file_uploader("Upload Resume (PDF, DOCX, or Image)", type=["pdf", "docx", "doc", "png", "jpg", "jpeg"])
    job_desc = st.text_area("Job Description", height=200)

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

            # Display results
            st.subheader("Analysis Results")
            st.write(analysis)

if __name__ == "__main__":
    main()