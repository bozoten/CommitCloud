import httpx
import os

# Define the ID of the item you want to delete
item_id = 1  # Change this to the ID you want to delete
delete_url = f"http://localhost:8000/delete/?id={item_id}"  # Update this if your server runs on a different port or domain

# Send the DELETE request
try:
    response = httpx.delete(delete_url)
    response.raise_for_status()  # Raise an error for bad responses
    print("Delete successful!")
    print("Response:", response.text)  # Change to response.json() if the response is in JSON format
except httpx.HTTPStatusError as e:
    print(f"HTTP Error: {e.response.status_code} - {e.response.text}")
except Exception as e:
    print(f"An error occurred: {str(e)}")
