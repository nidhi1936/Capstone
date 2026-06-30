from typing import Literal
from state import SupportState
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from pypdf import PdfReader
import requests
from urllib.parse import urlparse
from bs4 import BeautifulSoup
from reportlab.platypus import SimpleDocTemplate, Paragraph
from reportlab.lib.styles import getSampleStyleSheet
from crud import insertDetails

#USING OPENAI
load_dotenv()
llm=ChatOpenAI(model="gpt-4o-mini",temperature=0.7)

#CONVERTING JOB DESCRIPTION URL TO TEXT
def jd_url(job_description:str):
    try:
        response = requests.get(job_description)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        #description = soup.find("div", class_="job-description")
        #tags=description.get_text("\n", strip=True)
        tags = soup.find_all("a")
        return tags
    except requests.RequestException as e:
        return {}

#CHECKING IF RESUME MATCHES THE JOB DESCRIPTION
def fit_analyse(state: SupportState):
    job_description = state["job_description"]
    result = urlparse(job_description)
    if result.scheme and result.netloc:
        job_description=jd_url(job_description)
    resume=state["resume"]
    resume_text=read_file(resume)
    prompt=f"""You are an ATS (Applicant Tracking System) and resume evaluation expert.
        Compare the following resume with the given job description.
        **Evaluation Criteria:**
        * Compare the candidate's skills, experience, technologies, education, and responsibilities with the job description.
        * Consider the resume a match only if the candidate satisfies most of the essential requirements (approximately 60% or more).
        * Ignore minor differences in wording if the underlying skills or experience are equivalent.
        **Output Rules:**
        1. If the resume is **not a suitable match**, output exactly:
        NOT_MATCHING
        Do not provide any explanation or additional text.
        2. If the resume is a suitable match:
        * Do **not** rewrite the resume.
        * Return only 5-10 concise bullet points highlighting the candidate's strongest qualifications that should be emphasized to better align with the job description.
        * Focus on relevant skills, measurable achievements, certifications, projects, and domain experience.
        * Do not invent information that is not present in the resume.

        Resume:
        {resume_text}
        Job Description:
        {job_description}
    """
    #CALLING LLM
    message=llm.invoke([{"role": "system","content":prompt}]).content

    if any(word in message.lower() for word in ["not_matching"]):
        fit_analysis=False
        message=""
    else:
        fit_analysis=True
    return {"fit_analysis": fit_analysis,"emphasis":message}

#READING PDF FILE
def read_file(file:str):
    reader = PdfReader(file)
    text = ""
    for page in reader.pages:
        page_text = page.extract_text()
        if page_text:
            text += page_text + "\n"
    return text

#WRITING INTO A PDF FILE
def write_file(file:str,type:str,text:str):
    file_name=file[0:-4]
    file=file_name+"_"+type+".pdf"
    doc = SimpleDocTemplate(file)
    styles = getSampleStyleSheet()
    story = []
    for line in text.split("\n"):
        story.append(Paragraph(line, styles["Normal"]))
    doc.build(story)
    return file

#REWRITE A RESUME
def resume_rewrite(state: SupportState) -> SupportState:
    if state["fit_analysis"]==False:
        return {}
    resume_text=read_file(state["resume"])
    message=llm.invoke([{"role": "system","content":f"Kindly rewrite the resume {resume_text}to fit according to the job description {state["job_description"]} provided"}]).content
    result=write_file(state["resume"],"updated",message)
    return {"resume_rewrite":result}

#DRAFTING A COVER LETTER
def cover_letter_draft(state: SupportState) -> SupportState:
    if state["fit_analysis"]==False:
        return {}
    resume_text=read_file(state["resume"])
    message=llm.invoke([{"role": "system","content":f"Kindly write a cover letter draft for the resume {resume_text}to fit according to the job description {state["job_description"]} provided"}]).content
    result=write_file(state["resume"],"cover_letter",message)
    return {"cover_letter":result}

#MOCK INTERVIEW QUESTIONS AND ANSWERS
def mock_interview(state: SupportState) -> SupportState:
    if state["fit_analysis"]==False:
        return {}
    resume_text=read_file(state["resume"])
    message=llm.invoke([{"role": "system","content":f"Kindly give 10 mock interview questions and answers based on the resume {resume_text}to fit according to the job description {state["job_description"]} provided"}]).content
    result=write_file(state["resume"],"interview",message)
    return {"mock_interview":result}


#COLLECTONG ALL OUTPUT AND SAVING IN DB
def collect_output(state:SupportState):
    if state["fit_analysis"]==False:
        return {}
    msg=insertDetails({
        "user_id":state["user_id"],
        "job_title":"",
        "company":"","job_description":state["job_description"],
        "resume":state["resume"],
        "resume_rewrite":state["resume_rewrite"],
        "cover_letter":state["cover_letter"],
        "mock_interview":state["mock_interview"]
        })
    return {}