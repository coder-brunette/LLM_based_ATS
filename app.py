import streamlit as st
import google.generativeai as genai
import os
import PyPDF2 as pdf
import json
from dotenv import load_dotenv

load_dotenv()  # Load environment variables

genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

## Gemini Pro Response
def get_gemini_response(input):
    model = genai.GenerativeModel('gemini-pro')
    response = model.generate_content(input)
    return response.text

## Extract text from the PDF
def input_pdf_text(uploaded_file):
    reader = pdf.PdfReader(uploaded_file)
    text = ""
    for page in range(len(reader.pages)):
        page = reader.pages[page]
        text += str(page.extract_text)
    return text

## Prompt template
input_prompt = """
Hi, act like a very experienced ATS(Application tracking system) with a deep understanding of tech field,
software engineering, data science, data analysis, data engineering and machine learning engineering.
Your task is to evaluate each resume based on the given job description. You must consider the job market, which
is extremely competitive and you should be able to provide the best assistance for improving the resumes.
Assign the percentage match based on the job description and missing keywords with high accuracy.
resume: {text}
description: {jd}

I want a one liner response having this structure 
{{'Job description match: ': '%', 'Missing keywords: []', 'Profile summary':""}}
"""

## Creating the Streamlit app
st.title('Smart ATS')
st.text('Improve your resume with this ATS')
jd = st.text_area('Paste the job description here')
uploaded_file = st.file_uploader('Upload your resume', type='pdf', help='Please upload only pdf')
submit = st.button('Submit')

if submit:
    if uploaded_file is not None:
        text = input_pdf_text(uploaded_file)
        formatted_prompt = input_prompt.format(text=text, jd=jd)
        response = get_gemini_response(formatted_prompt)
        st.subheader(response)
        
        # Process response to format it
        try:
            result = json.loads(response)
            job_match = result.get('Job description match: ', 'N/A')
            missing_keywords = result.get('Missing keywords: ', 'N/A')
            profile_summary = result.get('Profile summary', 'N/A')
            
            # Display formatted output
            st.markdown(f"""
            <div style="border: 2px solid #ddd; border-radius: 10px; padding: 10px; background-color: #f9f9f9;">
                <p><strong>Job description match:</strong> {job_match}%</p>
                <p><strong>Missing keywords:</strong> {missing_keywords}</p>
                <p><strong>Profile summary:</strong> {profile_summary}</p>
            </div>
            """, unsafe_allow_html=True)
        except json.JSONDecodeError:
            st.error("Error parsing response from the model.")
