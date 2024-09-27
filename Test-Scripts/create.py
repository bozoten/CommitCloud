import httpx
import os

# Define the path of the file you want to upload
file_path = "target.png"  # Change this to your file path
upload_url = "http://localhost:8000/create/"  # Update this if your server runs on a different port or domain

# Check if the file exists
if not os.path.isfile(file_path):
    print(f"Error: File '{file_path}' not found.")
else:
    # Prepare the file for upload
    with open(file_path, 'rb') as file:
        files = {'file': (os.path.basename(file_path), file)}

        # Send the POST request
        try:
            response = httpx.post(upload_url, files=files)
            response.raise_for_status()  # Raise an error for bad responses
            print("Upload successful!")
            print("Response:", response.json())
        except httpx.HTTPStatusError as e:
            print(f"HTTP Error: {e.response.status_code} - {e.response.text}")
        except Exception as e:
            print(f"An error occurred: {str(e)}")
