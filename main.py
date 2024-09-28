import os
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from typing import List, Optional
from github import Github
from dotenv import load_dotenv
import base64
from fastapi.middleware.cors import CORSMiddleware
load_dotenv()


token = os.getenv('PAT')
g = Github(token)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # You can specify the allowed origins here
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods (GET, POST, OPTIONS, etc.)
    allow_headers=["*"],  # Allows all headers
)

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
    return FileResponse('index.html')

@app.get("/all/")
async def all_files():
    commits = id_repo.get_commits()
    commits = list(commits)

    names = []
    for commit in commits:

        name = commit.commit.message
            
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
        commits = store_repo.get_commits()
        last_commit = commits[0]
        sha_var = last_commit.sha
        print("New File Added kiss kiss")
    except Exception as e:
        # if file doesn't exist create the file gahahahahahaha 
        store_repo.create_file(trojan_path, commit_message, trojan_encoded, branch=branch)
        commits = store_repo.get_commits()
        last_commit = commits[0]
        sha_var = last_commit.sha
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


@app.post("/download/")
async def download(id: str):
    file_name = id[40:]
    sha_one = id[:40]
    commit = store_repo.get_commit(sha_one)

    file_data = base64.b64decode(commit.commit.message)

    with open(file_name, 'wb') as file:
        file.write(file_data)

      # Return the file as a response
    
    return FileResponse(file_name, media_type='application/octet-stream', filename=file_name)


'''
High Res Endpoints
'''

@app.post("/create/")
async def upload_file(file: UploadFile = File(...)):
    # Check if the file is valid
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file uploaded")

    # Read the file content
    contents = await file.read()
    target_encode = base64.b64encode(contents)
    target_encode = target_encode.decode()

    batch_size = 10000

    commit_message = target_encode
    branch = "main"
    sha_one = ""
    for i in range(0, len(target_encode), batch_size):
        batch = target_encode[i: i + batch_size]
        commit_message = batch
        try:
            # if file exists get file & update it
            repo_contents = store_repo.get_contents(trojan_path, ref=branch)
            store_repo.update_file(repo_contents.path, commit_message, trojan_encoded, repo_contents.sha, branch=branch)
            if (i==0):
                commits = store_repo.get_commits()
                first_commit = commits[0]
                sha_one = first_commit.sha
            print("Upload is going charmingly :3")
        except:
            # if file doesn't exist create the file gahahahahahaha 
            store_repo.create_file(trojan_path, commit_message, trojan_encoded, branch=branch)
            if (i==0):
                commits = store_repo.get_commits()
                first_commit = commits[0]
                sha_one = first_commit.sha
            print("Upload has started pookie bear kiss kiss")
        
    commits = store_repo.get_commits()
    last_commit = commits[0]
    sha_two = last_commit.sha

    id_commit_message = sha_one + "hr" + sha_two + file.filename  

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

    return {"message": "File uploaded and record created", "filename": id_commit_message, "data": target_encode}


    
    
# test