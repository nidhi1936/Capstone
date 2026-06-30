from fastapi import FastAPI, File, UploadFile,Form, Depends,Cookie,HTTPException, Request
from fastapi.responses import FileResponse, RedirectResponse, JSONResponse
import shutil
import os
import jwt
from jwt import ExpiredSignatureError,InvalidTokenError
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from datetime import datetime,timedelta
from graph import graph
from crud import checkUsername
from urllib.parse import urlencode
from fastapi.staticfiles import StaticFiles

#CREATING FASTAPI
app=FastAPI()

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

#JWT SECRET KEY AND ALGORITHM
SECRET_KEY="secret_key"
ALGORITHM="HS256"

security = HTTPBearer()

#CALLING LOGIN PAGE
@app.get("/")
def main():
    return FileResponse("..\\frontend\\login.html") 

#CALLING RESUME PAGE
@app.get("/resume_file")
def resume_file():
    return FileResponse("..\\frontend\\resume_file.html")

#CALLING DISPLAY PAGE
@app.get("/display")
async def display():
    return FileResponse("..\\frontend\\display.html")

#CREATING JWT TOKEN
def create_token(id: int):
    payload = {
        "sub": str(id),
        "exp": datetime.utcnow() + timedelta(minutes=30)
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

#CHECKING FOR USER CREDENTIALS, CREATING TOKEN AND SENDING IT AS A COOKIE
@app.post("/login")
def login(username:str=Form(...),password:str=Form(...)):
    exist=checkUsername(username,password)
    if exist["message"]=="Login_Successful":
        #response = JSONResponse(content={})
        response = JSONResponse({"redirect": "/resume_file"})
        token = create_token(exist["id"])
        response.set_cookie(
            key="access_token",
            value=token,
            httponly=True,
            samesite="Lax",
            secure=False  # True when using HTTPS
        )
        return response
    return JSONResponse(
            status_code=401,
            content={"error": "Invalid username or password"}
        )

#CHECK FOR JWT AND ITS VALIDITY
async def check(access_token: str = Cookie(None)):
    if access_token is None:
        return JSONResponse({"error": "Please login first.","redirect":"/"})
    try:
        payload = jwt.decode(access_token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload["sub"]
    except ExpiredSignatureError:
        return "session_expired"
    except InvalidTokenError as e:
        return JSONResponse({"status_code":"401", "error": "Please login first. You have a invalid token.","redirect":"/"})

#SENDING PDF TO BE DISPLAYED
@app.get("/pdf/{filename}")
async def get_pdf(filename: str):
    return FileResponse(
        os.path.join(UPLOAD_DIR, filename),
        media_type="application/pdf",
        headers={"Content-Disposition": "inline"}
    )

#UPLOADING RESUME AND INVOKING GRAPH
@app.post("/upload-pdf")
async def upload_pdf(file:UploadFile=File(...),jd:str=Form(...),access_token: str = Cookie(None)):
    id=await check(access_token)
    # Check file type
    if id=="session_expired":
        return JSONResponse({"status_code":"401", "error": "Please login first. Your session has expired.","redirect":"/"})
    if file.content_type != "application/pdf":
        return JSONResponse({"error": "Only PDF files are allowed"})
    file_path = os.path.join(UPLOAD_DIR, file.filename)
    # Save file
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    #INVOKING GRAPH
    result=graph.invoke({"resume":file_path,"job_description":jd,"user_id":int(id)})
    if result["fit_analysis"]==False:
        return JSONResponse({"message":"Your resume does not meet the job description.","fit_analysis":str(result["fit_analysis"])})

    message="Your resume matches the job description the following are the points to be emphasised.\n"+result["emphasis"]
    params = urlencode({"resume_name": result["resume"]})
    return JSONResponse({"message":result["emphasis"],"fit_analysis":str(result["fit_analysis"]),"params":params})
    #jkjiljojl