import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import random
import csv

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
)

'''@app.get("/")
def index():
    return "Hello, world!"'''

@app.get("/")
def get_questions(use: str, subject: str, number: int):
    # Get the questions from the database.
    questions = get_questions_from_database(use, subject, number)
    # Shuffle the questions.
    random.shuffle(questions)
    # Return the questions.
    return questions

def get_questions_from_database(use: str, subject: str, number: int):
    # Read the questions from the CSV file.
    with open("~data/questions.csv", "r") as f:
        reader = csv.reader(f, delimiter=",")
        questions = []
        for row in reader:
            questions.append({
                "question": row[0],
                "subject": row[1],
                "correct": row[2],
                "responseA": row[3],
                "responseB": row[4],
                "responseC": row[5],
                "responseD": row[6],
            })
    # Return the questions.
    return questions[0:number]

@app.post("/create-question")
def create_question(username: str, password: str, question: str, subject: str, correct: str, responseA: str,\
    responseB: str, responseC: str, responseD: str):
    # Check if the user is authenticated.
    if not check_authentication(username, password):
        return 401
    # Create the question.
    create_question_in_database(question, subject, correct, responseA, responseB, responseC, responseD)
    return 201

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
#    app.run(host="0.0.0.0", port=8000)