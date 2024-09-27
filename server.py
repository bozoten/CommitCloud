import os 
from fastapi import FastAPI, UploadFile, File, HTTPException
from github import Github
from dotenv import load_dotenv
import base64
import json

load_dotenv()

token = os.getenv('PAT')
g = Github(token)

app = FastAPI()
repo_two = os.getenv('STORAGEREPO')

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
     ids = []
     with open(trojan_path, 'r') as file:
            lines = file.readlines() 
            id_list = [line.strip() for line in lines]
            
            for id in id_list:              
                ids.append(id[40:])
     return ids
    

@app.post("/create/")
async def upload_file(file: UploadFile = File(...)):
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file uploaded")

    contents = await file.read()
    file_data = base64.b64encode(contents)
    file_data = file_data.decode()

    commit_message = file_data
    branch = "main"

    try:
        repo_contents = store_repo.get_contents(trojan_path, ref=branch)
        store_repo.update_file(repo_contents.path, commit_message, trojan_encoded, repo_contents.sha, branch=branch)
        sha_var = repo_contents.sha
        print("New File Added kiss kiss")
    except Exception as e:
        store_repo.create_file(trojan_path, commit_message, trojan_encoded, branch=branch)
        repo_contents = store_repo.get_contents(trojan_path, ref=branch)
        sha_var = repo_contents.sha
        print("File Upload Done Succesfully. Heck yeah!")

    id_commit_message = sha_var + file.filename  

    with open(trojan_path, 'a') as id_file:
            id_file.write("\n" + id_commit_message)

    with open(trojan_path, "rb") as trojan_file:
        id_content = trojan_file.read()
        id_encoded = base64.b64encode(id_content)
        id_encoded = id_encoded.decode()    

    try:
        repo_contents = store_repo.get_contents(trojan_path, ref=branch)
        store_repo.update_file(repo_contents.path, "id_updated", id_encoded, repo_contents.sha, branch=branch)
        print("New ID Added kiss kiss")
    except Exception as e:
        store_repo.create_file(trojan_path, "id_updated", id_encoded, branch=branch)
        print("File Upload Done Succesfully. Heck yeah!")

    return {"message": "File uploaded and record created", "filename": id_commit_message, "data": file_data}



# test