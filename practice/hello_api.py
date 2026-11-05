from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI(title="Hello API")


# The simplest endpoint. Visit http://127.0.0.1:8000/
@app.get("/")
def home() -> dict:
    return {"message": "Hello, CSC10014!"}


# A path parameter. Visit http://127.0.0.1:8000/hello/Lan
@app.get("/hello/{name}")
def hello(name: str) -> dict:
    return {"message": f"Hello, {name}!"}


# A query parameter. Visit http://127.0.0.1:8000/square?n=7
@app.get("/square")
def square(n: int) -> dict:
    return {"n": n, "square": n * n}


# A request body. Send JSON {"a": 2, "b": 3} with POST.
class Numbers(BaseModel):
    a: float
    b: float


@app.post("/add")
def add(nums: Numbers) -> dict:
    return {"sum": nums.a + nums.b}


# Errors. Visit http://127.0.0.1:8000/courses/CSC10014 and /courses/XYZ
COURSES = {"CSC10014": "Computational Thinking", "CSC10001": "Fundamentals of Programming"}


@app.get("/courses/{code}")
def course(code: str) -> dict:
    if code not in COURSES:
        raise HTTPException(status_code=404, detail="Course not found")
    return {"code": code, "name": COURSES[code]}