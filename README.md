# Commit Cloud - Free File Storage with Git Commits

## Introduction
**Commit Cloud** is a web-based application that allows users to upload, store, and manage files with infinite storage using GitHub Commits. It provides an easy interface to upload files, commit them to GitHub, and download them, all via a personal access token (PAT). The system uses two repositories (`repo1` and `repo2`) for storing file metadata and the actual file contents.

### Key Features:
- File Upload: Users can encode and upload files to the GitHub Commits.
- File Download: Users can decode and download previously uploaded files from GitHub Commits.
- Secure Authentication: Users authenticate via their GitHub username and PAT (Personal Access Token).
- Storage Management: File data is stored across GitHub commits, with large files split into chunks.

## HTML Interface

### `index.html`
The HTML file provides a simple UI where users can input their GitHub credentials (username and PAT) to interact with the file storage system.

#### Key Sections:
1. **GitHub Authentication Form:**
   - The user inputs their GitHub username and PAT. Once submitted, this information is used for authentication.
   
   ```html
   <form id="github-credentials">
       <label for="username">GitHub Username:</label>
       <input type="text" id="username" name="username" required><br><br>

       <label for="pat">Personal Access Token:</label>
       <input type="password" id="pat" name="pat" required><br><br>

       <input type="submit" value="Submit">
   </form>
   ```

2. **File Operations Interface:**
   - After submitting the credentials, users can upload files or view/download existing files in their repository.

   ```html
   <div id="file-operations" style="display: none;">
       <input type="file" id="file-input">
       <button onclick="uploadFile()">Upload</button>
       <button onclick="getAllFiles()">Refresh File List</button>
       <ul id="file-list"></ul>
   </div>
   ```

## JavaScript Functionality

### Authentication Handling
After the user submits their credentials, their GitHub username and PAT are saved for future API requests.

```javascript
document.getElementById('github-credentials').addEventListener('submit', function(e) {
    e.preventDefault();
    githubUsername = document.getElementById('username').value;
    githubPat = document.getElementById('pat').value;
    document.getElementById('file-operations').style.display = 'block';
    this.style.display = 'none';
    getAllFiles();
});
```

### File Upload
The `uploadFile` function handles uploading files. The file is read and encoded into Base64, and then committed to the GitHub repository (`repo2`) using the GitHub API.

```javascript
async function uploadFile() {
    const fileInput = document.getElementById('file-input');
    const file = fileInput.files[0];
    
    if (!file) {
        alert('Please select a file to upload');
        return;
    }
    
    const formData = new FormData();
    formData.append('file', file);
    formData.append('username', githubUsername);
    formData.append('pat', githubPat);
    
    try {
        const response = await fetch('/create/', {
            method: 'POST',
            body: formData
        });
        const result = await response.json();
        alert(`File uploaded successfully: ${result.filename}`);
        getAllFiles();
    } catch (error) {
        console.error('Error:', error);
        alert('An error occurred while uploading the file');
    }
}
```

### Fetching and Listing Files
`getAllFiles` retrieves all commit messages from `repo1` and displays them as a list. The list items have download buttons that trigger the `downloadFile` function.

```javascript
async function getAllFiles() {
    try {
        const response = await fetch(`/all/?username=${encodeURIComponent(githubUsername)}&pat=${encodeURIComponent(githubPat)}`);
        const files = await response.json();
        
        const fileList = document.getElementById('file-list');
        fileList.innerHTML = '';
        
        files.forEach(file => {
            const li = document.createElement('li');
            const fileNameSpan = document.createElement('span');
            fileNameSpan.textContent = file.substring(82);
            
            const downloadBtn = document.createElement('button');
            downloadBtn.textContent = 'Download';
            downloadBtn.className = 'download-btn';
            downloadBtn.onclick = () => downloadFile(file);
            
            li.appendChild(fileNameSpan);
            li.appendChild(downloadBtn);
            fileList.appendChild(li);
        });
    } catch (error) {
        console.error('Error:', error);
        alert('An error occurred while fetching the file list');
    }
}
```

### Downloading Files
`downloadFile` fetches a file from `repo2` using its commit message, decodes the file content from Base64, and triggers a download in the browser.

```javascript
async function downloadFile(fileId) {
    try {
        const response = await fetch(`/download/?id=${encodeURIComponent(fileId)}&username=${encodeURIComponent(githubUsername)}&pat=${encodeURIComponent(githubPat)}`, {
            method: 'POST'
        });

        if (response.ok) {
            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.style.display = 'none';
            a.href = url;
            a.download = fileId.substring(82); // File name
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
        } else {
            throw new Error('File download failed');
        }
    } catch (error) {
        console.error('Error:', error);
        alert('An error occurred while downloading the file');
    }
}
```

## Backend (FastAPI)

The backend uses **FastAPI** to interact with the GitHub API. It handles file uploads and downloads via GitHub commits.

### Key Endpoints:

1. **GET `/all/`**: Fetches all commit messages from `repo1` (used to list uploaded files).
   
   ```python
   @app.get("/all/")
   async def all_files(username: str, pat: str):
       g = Github(pat)
       repo = g.get_repo(f"{username}/repo1")
       commits = repo.get_commits()
       names = [commit.commit.message for commit in commits]
       return names
   ```

2. **POST `/create/`**: Uploads a file to `repo2`, splitting it into chunks if necessary, and commits it to GitHub.

   ```python
   @app.post("/create/")
   async def upload_file(file: UploadFile, username: str, pat: str):
       g = Github(pat)
       store_repo = g.get_repo(f"{username}/repo2")
       contents = await file.read()
       file_data = base64.b64encode(contents).decode()
       # Logic to commit the file to the repo
       ...
       return {"message": "File uploaded", "filename": id_commit_message}
   ```

3. **POST `/download/`**: Retrieves the file content from `repo2` based on the commit message, decodes it, and serves the file for download.

   ```python
   @app.post("/download/")
   async def download(id: str, username: str, pat: str):
       g = Github(pat)
       store_repo = g.get_repo(f"{username}/repo2")
       # Logic to retrieve and decode file content
       ...
       return FileResponse(file_name)
   ```

### Key Libraries:
- **FastAPI**: A modern web framework for building APIs with Python.
- **PyGithub**: A Python library to interact with the GitHub API.
- **Base64**: Used for encoding/decoding file content during upload/download.

## How to Use

1. **Create GitHub Repositories**: Create two repositories (`repo1` and `repo2`) on your GitHub account.
2. **Generate Personal Access Token**: Generate a GitHub PAT with permissions for commits, repo access, etc.
3. **Run the Application**: Deploy the application locally or on a server.
4. **Access via Browser**: Open the web interface, authenticate with GitHub credentials, and start uploading/downloading files.

