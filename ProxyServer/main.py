from fastapi import FastAPI
from functions import validateAndRequest
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()
app.add_middleware(
    CORSMiddleware, 
    allow_origins=['*'],

)


@app.get("/")
async def root():
    return {"message": "Hello Stranger!"}

@app.get("/get-course")
async def get_course(P_SEMESTER: str, P_SUBJ: str, P_NUM: str):
    return validateAndRequest(P_SEMESTER, P_SUBJ.upper(), P_NUM)

@app.get("/get-course-list")
async def get_course_list():
    with open("validFormData/validCourseList.txt", 'r') as f:
        return f.read().splitlines()