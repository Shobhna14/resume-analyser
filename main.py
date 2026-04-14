import streamlit as st
from pdfminer.high_level import extract_text
import pytesseract
import cv2
import numpy as np

# Function to extract text from PDF using pdfminer
def extract_text_from_pdf(pdf_file):
    text = extract_text(pdf_file)
    return text

# Function to extract text from an image using Tesseract OCR
def extract_text_from_image(image_file):
    image = cv2.imdecode(np.frombuffer(image_file.read(), np.uint8), cv2.IMREAD_COLOR)
    text = pytesseract.image_to_string(image)
    return text

# Mocked tool functions for extracting information from resumes and matching with job description
def resume_extraction_tool(resume_text):
    return resume_text[:500]  # Just returning the first 500 characters

def job_matching_tool(job_description, resume_text):
    return 0.85  # Placeholder score, you can use NLP for better matching

# Streamlit UI for uploading and processing the resume
st.title("Resume Shortlisting Chatbot")

uploaded_file = st.file_uploader("Upload Resume", type=["pdf", "jpg", "png"])

if uploaded_file:
    if uploaded_file.name.endswith(".pdf"):
        resume_text = extract_text_from_pdf(uploaded_file)
    else:
        resume_text = extract_text_from_image(uploaded_file)

    # Display extracted resume text
    st.subheader("Extracted Resume Text")
    st.write(resume_text[:1000])  # Show a snippet of the resume text

    # Extract resume details (you can improve this logic)
    extracted_info = resume_extraction_tool(resume_text)

    st.subheader("Extracted Resume Info")
    st.write(extracted_info)

    # Job description input from the user
    job_description = st.text_area("Enter Job Description")

    if job_description:
        # Match the resume with the job description
        matching_score = job_matching_tool(job_description, resume_text)

        st.subheader("Job Match Score")
        st.write(f"The matching score is: {matching_score}")
