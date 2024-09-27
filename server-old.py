import os 
from fastapi import FastAPI, UploadFile, File, HTTPException
from typing import List, Optional
from github import Github
from dotenv import load_dotenv
import base64
import json

load_dotenv()

token = os.getenv('PAT')
g = Github(token)

app = FastAPI()

repo_one = "bozoten/repo1"
repo_two = "bozoten/repo2"

id_repo = g.get_repo(repo_one)
store_repo = g.get_repo(repo_two)

trojan_path = "./Trojan/horse.txt"

with open(trojan_path, 'r') as file:
    trojan_content = file.read()

# encode content to base 64 (github expects files this way) 
trojan_encoded = base64.b64encode(trojan_content.encode()).decode()

@app.get("/")
async def read_root():
    return {"message": "Welcome to Commit Cloud your free file storage provider!"}

@app.get("/all/")
async def all_files():
    commits = id_repo.get_commits()
    commits = list(commits)

    names = []
    for commit in commits:

        name = commit.commit.message[40:]
            
        names.append(name)

    return names
    

# Endpoint to create a new record in the database
@app.post("/upload/")
async def upload_file(file: UploadFile = File(...)):
    # Check if the file is valid
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file uploaded")

    # Read the file content
    contents = await file.read()
    file_data = base64.b64encode(contents)
    file_data = file_data.decode()

    commit_message = file_data
    branch = "main"

    # storage repo
    try:
        # if file exists get file & update it
        repo_contents = store_repo.get_contents(trojan_path, ref=branch)
        store_repo.update_file(repo_contents.path, commit_message, trojan_encoded, repo_contents.sha, branch=branch)
        sha_var = repo_contents.sha
        print("New File Added kiss kiss")
    except Exception as e:
        # if file doesn't exist create the file gahahahahahaha 
        store_repo.create_file(trojan_path, commit_message, trojan_encoded, branch=branch)
        repo_contents = store_repo.get_contents(trojan_path, ref=branch)
        sha_var = repo_contents.sha
        print("File Upload Done Succesfully. Heck yeah!")
        
    id_commit_message = sha_var + file.filename  

    # id repo
    try:
        # if existing repo
        repo_contents = id_repo.get_contents(trojan_path, ref=branch)
        id_repo.update_file(repo_contents.path, id_commit_message, trojan_encoded, repo_contents.sha, branch=branch)
        print("New File Added kiss kiss")
    except Exception as e:
        # if new repo
        id_repo.create_file(trojan_path, id_commit_message, trojan_encoded, branch=branch)
        print("File Upload Done Succesfully. Heck yeah!")

    return {"message": "File uploaded and record created", "filename": id_commit_message, "data": file_data}



# test