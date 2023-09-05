import aiofiles
import asyncio
import os
import requests
import pandas as pd
from fastapi import FastAPI, HTTPException, Header, Query, Depends
from pydantic import BaseModel, Field
import csv
import random
from typing import Optional, List
import Backup.csvreview as csvreview
import html
from enum import Enum

app = FastAPI(
    title="API pour la base de questions",
    description="API pour consultation de la base de questions et insertion de nouvelles questions",
    version="1.0",
    debug=True)

local_csv_path = "/root/Coding/FastAPI/Eval/Data/questions.csv"
#Import du csv d'origine
def is_csv_empty(file_path):
    return os.path.exists(file_path) and os.path.getsize(file_path) == 0
def download_csv_from_url(url, destination_path):
    response = requests.get(url)
    if response.status_code == 200:
        with open(destination_path, 'wb') as file:
            file.write(response.content)
        print(f"CSV file downloaded and saved to {destination_path}")
    else:
        print(f"Failed to download CSV file from {url}")

# Vérification que le tableau n'est pas vide
if is_csv_empty(local_csv_path):
    replacement_csv_url = "https://dst-de.s3.eu-west-3.amazonaws.com/fastapi_fr/questions.csv"
    download_csv_from_url(replacement_csv_url, local_csv_path)
else:
    print("Local CSV file is not empty, no replacement needed.")
    df=pd.read_csv('/root/Coding/FastAPI/Eval/Data/questions.csv')
    df.head()

list_use=csvreview.list_use
list_subject=csvreview.list_subject

# Dictionnaire d'utilisateurs tels que définis dans l'énoncé, mot de passe admin 'escaped'
USERS = {
    "alice":"rabbit",
    "bob":"builder",
    "clementine":"mandarine",
    "admin":"{}".format(html.escape("4dm1N"))
    }

class User(BaseModel):
    user: str
    password: str
    subscription: Optional[str] = None

# Définition d'un énumérateur à partir d'un tableau de données
def define_enum_from_array(array):
  enum = Enum(
      "Enum",
      [(value, value) for value in array]
      )
  return enum

enum_use = define_enum_from_array(list_use)
enum_subject = define_enum_from_array(list_subject)

# Access and print the actual values of the Enum
for member in enum_subject:
    print(member.value)

# Iterate through Enum members and print their values
for member in enum_use:
    print(f"{member.name}: {member.value}")

async def authentification(username: str = Header(None), password: str = Header(None)):
    ''' vérifie que l'utilisateur est enregistré te correctement identifié'''
    if username in USERS and USERS[username] == password:
        return username
    raise HTTPException(status_code=401, detail="Utilisateur ne faisant pas partie des utilisateurs enregistrés, ou identifiants incorrects, merci de contacter l'administrateur")

async def is_valid_answer_format(correct_answer: str) -> bool:
    ''' vérifie que la réponse correcte est bien parmi les 4 possibilités.'''
    return correct_answer in ['A', 'B', 'C', 'D']

#@api changed into app
@app.get('/', name='Bienvenue')
async def get_index():
    '''Bienvenue'''
    return {'greetings': 'Bienvenue'}

@app.get('/users', name='Utilisateurs enregistrés')
async def get_users():
    ''' Retourne la liste des utilisateurs enregistrés'''
    return USERS

@app.get("/check", name= 'vérification fonctionnalité API')
async def check():
    ''' Vérification que l'API est bien fonctionnelle'''
    return {"message": "l'API est bien fonctionelle"}


async def check_subject(subject:str):
    ''' vérifie que le sujet renseigné figure parmi ceux déjà existants'''
    if subject not in list_subject:
        raise HTTPException(status_code=400, detail="Rejected: Le sujet proposé ne fait pas partie de ceux déjà existants")
        print("Merci de bien vouloir sélectionner une option parmi celles-ci:")
        for values in list_subject:
            print(values)
    else:
        print("Accepted: Subjet validé")

async def check_use(use:str):
    ''' vérifie que l'utilisation renseignée figure parmi celle déjà existante.'''
    if use not in list_use:
        raise HTTPException(status_code=400, detail="Le 'Use' proposé ne fait pas partie de ceux existants")
        print("Merci de bien vouloir sélectionner une option parmi celles-ci:")
        for values in list_use:
            print(values)        
    else:
        print("Accepted: Use validé")

async def load_questions_from_csv():
    ''' récupère le csv questions dans le répertoire Data'''
    with open("/root/Coding/FastAPI/Eval/Data/questions.csv", "r") as f:
        reader = csv.DictReader(f, delimiter=",")
        questions = list(reader)
    return questions
    await asyncio.sleep(1)

class Requested_Questions(BaseModel):
    subject: str = Field(default='Streaming de données')
    use: str = Field(default='Test de validation')
    num_questions: int = Field(default=5, description="Number of questions should be either 5, 10, or 20", enum=[5, 10, 20])

@app.get("/get_questions/", name='Demande de questions')
async def get_questions(
    subject: str = Query(default='Streaming de données'),
    use: str = Query(default='Test de validation'),
    num_questions: int = Query(default=5, description="Number of questions should be either 5, 10, or 20", enum=[5, 10, 20])
):
    '''Obtention d'une série de questions issues de la bases questions.csv'''
    await check_use(use)
    await check_subject(subject)
    await load_questions_from_csv()
    filtered_questions = [q for q in questions if q['use'] == use and q['subject'] == subject]
    num_requested_questions = min(num_questions, len(filtered_questions))
    selected_questions = random.sample(filtered_questions, num_requested_questions)
    return selected_questions

# Ajout de nouvelles questions à la base de données
async def save_questions_to_csv(questions):
    '''Ajoute une nouvelle question au csv questions existant.'''
    fieldnames = questions[0].keys()
    async with aiofiles.open("/root/Coding/FastAPI/Eval/Data/questions.csv", "w", newline='') as csv_file:
        csv_writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        csv_writer.writeheader()
        for row in questions:
            csv_writer.writerow(row)

class New_Question(BaseModel):
    question: str
    subject: str
    use: str
    correct: Enum = Field (description="Spécifier la bonne réponse soit A, B, C ou D",enum=['A','B','C','D'])
    response_A: str = Field(max_length=150)
    response_B: str = Field(max_length=150)
    response_C: str = Field(max_length=150)
    response_D: Optional[str] = None
    remark: Optional[str] = None

#API endpoint pour l'ajout de questions par un administrateur
@app.post("/create_question/", name='création de nouvelles questions par un administrateur')
async def create_question(
    question: str = Query(description='Texte de la nouvelle question'),
    subject: str = Query(default='BDD',description='Sujet parmi ceux existant'), 
    use: str = Query(default='Total Bootcamp',description='Destination parmi ceux existant'),
    correct: str = Query(default='C', description="Merci de spécifier la bonne réponse", enum=['A','B','C','D']),
    response_A: str = Query(max_length=150, description='libellé de la réponse A'),
    response_B: str = Query(max_length=150, description='libellé de la réponse B'),
    response_C: str = Query(max_length=150, description='libellé de la réponse C'),
    response_D: Optional[str]=Query(default='Null', max_length=150, description='libellé de la réponse D'),
    remark: Optional[str] = None,
    username: str = Query (None), 
    password: str = Query (None)
    ):
    ''' Création de nouvelle questions.'''
    if username != 'admin':
        raise HTTPException(status_code=401, detail="Vous n'êtes pas autorisés à rentrer une nouvelle question. Seul l'utilisateur admin l'est")
    if username not in USERS or USERS[username] != password:
        raise HTTPException(status_code=401, detail="Vous n'êtes pas enregistrés ou vos identifiants / mot de passe incorrect(s)")
    if not is_valid_answer_format(correct):
        raise HTTPException(status_code=400, detail="Format de la question incorrecte")
    await check_use(use)
    await check_subject(subject)
    questions = await load_questions_from_csv()
    new_question={
        "question":question,
        'subject':subject,
        'use':use,
        'correct':correct,
        'responseA': response_A,
        'responseB': response_B,
        'responseC': response_C,
        'responseD': response_D,
        'remark':remark
    }
    questions=questions.append(new_question)
#    await save_questions_to_csv(questions)
    return {"message": "Merci, question ajoutée avec succès"}

# initiation FastAPI application
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)