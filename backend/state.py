from typing_extensions import TypedDict

class SupportState(TypedDict, total=False):
    user_id : int
    resume: str
    resume_text:str
    job_description : str
    company_name: str
    job_title: str

    fit_analysis : bool
    emphasis : str
    resume_rewrite: str
    cover_letter: str
    mock_interview : str

