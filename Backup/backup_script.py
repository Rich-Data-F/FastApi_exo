## Not necessary / used at this time
#from msilib.sequence import InstallUISequence
#pip3 InstallUISequence --upgrade pydantic
#installation de aiofiles dans le terminal

"""
#async def get_questions(Requested_Questions.use,Requested_Questions.subject,Requested_Questions.num_questions):
async def get_questions(
    subject: str = Query(default='BDD', description='Subject'),
    use: str = Query(default='Total Bootcamp', description='Use'),
    num_questions: int = Query(default=5, description='Number of questions should be either 5, 10, or 20')
):
#requested_questions = Requested_Questions(subject=subject, use=use, num_questions=num_questions)
"""

#    async with asyncio.to_thread(open,"/root/Coding/FastAPI/Eval/Data/questions.csv", "w", newline='') as csv_file:


'''@app.get("/get_questions/",name='Demande de questions')
async def get_questions(requested_questions=Requested_Questions):
#    requested_questions: Requested_Questions = Depends(Requested_Questions)
#    if Requested_Questions.num_questions not in [5, 10, 20]:
#        raise HTTPException(status_code=400, detail="Invalid value for num_questions")
    await check_use(Requested_Questions.use)
    await check_subject(Requested_Questions.subject)
    questions = await load_questions_from_csv()
    filtered_questions = [q for q in questions if q['use'] == Requested_Questions.use and q['subject'] == Requested_Questions.subject]
    questions = get_questions_from_database(Requested_Questions.subject, Requested_Questions.use, Requested_Questions.num_questions)
    num_requested_questions=min(Requested_Questions.num_questions, len(filtered_questions))
    selected_questions = random.sample(filtered_questions, num_requested_questions)
    return selected_questions
'''


'''class Requested_Questions(BaseModel):
#    subject: Enum = enum_subject
    subject: str = Field(default='BDD')
    use: str = Field(default='Total Bootcamp')
    num_questions: int = Field(default=5, description="Number of questions should be either 5, 10, or 20)")
'''

'''
users_db = [
    {        'user_id': 1,
        'name': 'Alice',
        'subscription': 'free tier'
    },
    {
        'user_id': 2,
        'name': 'Bob',
        'subscription': 'premium tier'
    },
    {
        'user_id': 3,
        'name': 'Clementine',
        'subscription': 'free tier'
    }
]

@api.get('/users/{userid:int}')
def get_user(userid):
    try:
        user = list(filter(lambda x: x.get('user_id') == userid, users_db))[0]
        return user
    except IndexError:
        return {}

@api.get('/users/{userid:int}/name')
def get_user_name(userid):
    try:
        user = list(filter(lambda x: x.get('user_id') == userid, users_db))[0]
        return {'name': user['name']}
    except IndexError:
        return {}

@api.get('/users/{userid:int}/subscription')
def get_user_suscription(userid):
    try:
        user = list(filter(lambda x: x.get('user_id') == userid, users_db))[0]
        return {'subscription': user['subscription']}
    except IndexError:
        return {}
'''
