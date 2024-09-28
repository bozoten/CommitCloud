import os
from fastapi import FastAPI, UploadFile, File, HTTPException, Form, Query
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, HTMLResponse
from typing import List, Optional
from github import Github
import base64
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],  
    allow_headers=["*"],  
)

repo_one = "bozoten/repo1"
repo_two = "bozoten/repo2"

trojan_path = "./Trojan/horse.txt"

with open(trojan_path, 'r') as file:
    trojan_content = file.read()

trojan_encoded = base64.b64encode(trojan_content.encode()).decode()

@app.get("/", response_class=HTMLResponse)
async def read_root():
    with open('index.html', 'r') as f:
        return f.read()

@app.get("/all/")
async def all_files(username: str = Query(...), pat: str = Query(...)):
    g = Github(pat)
    id_repo = g.get_repo(f"{username}/repo1")
    commits = id_repo.get_commits()
    commits = list(commits)

    names = []
    for commit in commits:
        name = commit.commit.message
        names.append(name)

    return names
    
@app.post("/create/")
async def upload_file(
    file: UploadFile = File(...),
    username: str = Form(...),
    pat: str = Form(...)
):
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file uploaded")

    g = Github(pat)
    id_repo = g.get_repo(f"{username}/repo1")
    store_repo = g.get_repo(f"{username}/repo2")

    contents = await file.read()
    file_data = base64.b64encode(contents).decode()
    branch = "main"
    batch_size = 10000

    if len(file_data) > batch_size:
        sha_start = None
        for i in range(0, len(file_data), batch_size):
            batch = file_data[i:i + batch_size]
            commit_message = batch
            print("Batch Upload is going smoothly bbg :3 ")
            try:
                repo_contents = store_repo.get_contents(trojan_path, ref=branch)
                store_repo.update_file(repo_contents.path, commit_message, batch, repo_contents.sha, branch=branch)
            except:
                store_repo.create_file(trojan_path, commit_message, batch, branch=branch)
            if i == 0:
                sha_start = store_repo.get_commits()[0].sha
        sha_end = store_repo.get_commits()[0].sha
        id_commit_message = f"{sha_start}+{sha_end}+{file.filename}"
    else:
        commit_message = file_data
        try:
            repo_contents = store_repo.get_contents(trojan_path, ref=branch)
            store_repo.update_file(repo_contents.path, commit_message, file_data, repo_contents.sha, branch=branch)
        except:
            store_repo.create_file(trojan_path, commit_message, file_data, branch=branch)
        sha = store_repo.get_commits()[0].sha
        id_commit_message = f"{sha}{file.filename}"

    try:
        repo_contents = id_repo.get_contents(trojan_path, ref=branch)
        id_repo.update_file(repo_contents.path, id_commit_message, file_data, repo_contents.sha, branch=branch)
    except:
        id_repo.create_file(trojan_path, id_commit_message, file_data, branch=branch)

    return {"message": "File uploaded and record created", "filename": id_commit_message, "data": file_data}

@app.post("/download/")
async def download(id: str, username: str = Query(...), pat: str = Query(...)):
    g = Github(pat)
    store_repo = g.get_repo(f"{username}/repo2")

    if '+' in id:
        sha_start, sha_end, file_name = id.split('+')
        commits = store_repo.get_commits(sha_end)

        commit_messages = []
        for commit in commits:
            commit_messages.append(commit.commit.message)
            if commit.sha == sha_start:
                break

        commit_messages.reverse()
        file_data = "".join(commit_messages)
    else:
        sha = id[:40]
        file_name = id[40:]
        commit = store_repo.get_commit(sha)
        file_data = commit.commit.message

    decoded_data = base64.b64decode(file_data)

    with open(file_name, 'wb') as file:
        file.write(decoded_data)    

    response = FileResponse(file_name, media_type='application/octet-stream', filename=file_name)

    async def delete():
        os.remove(file_name)
    response.background = delete    

    return response