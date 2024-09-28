import httpx

id = "2ad4c324e7838b08ef562a009da5771c2d2f276cnew.png"  # Change this to your file path
upload_url = f"http://localhost:8000/download/?id={id}"  # Update this if your server runs on a different port or domain

response = httpx.post(upload_url)
response.raise_for_status()  # Raise an error for bad responses
print("Upload successful!")
print("Response:", response.json())
