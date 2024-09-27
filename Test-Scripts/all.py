import httpx
import asyncio

async def test_get_all_files():
    async with httpx.AsyncClient() as client:
        response = await client.get("http://127.0.0.1:8000/all/")  # Use your actual URL here
        print(response.status_code)
        print(response.text)

# Run the async function
asyncio.run(test_get_all_files())
