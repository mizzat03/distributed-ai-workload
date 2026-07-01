import asyncio
import time
from pathlib import Path

import httpx

API_URL = "http://localhost:8000/infer" 
IMAGE_PATH = "../data/images/elephant.jpg" 
BATCH_SIZE = 200

async def run_benchmark():

    # Prepare the batch payload
    files = [('files', (f"img_{i}.jpg", open(IMAGE_PATH, 'rb'), 'image/jpeg')) for i in range(BATCH_SIZE)]

    for i in range(5):
        async with httpx.AsyncClient() as client:
            start_time = time.perf_counter()
            
            # Send the batch to the FastAPI master
            response = await client.post(API_URL, files=files, timeout=60.0)
            
            end_time = time.perf_counter()
            
        total_time = end_time - start_time
        throughput = BATCH_SIZE / total_time
        
        print(f"--- Benchmark Results ---")
        print(f"Result Number:{i+1}")
        print(f"Status Code: {response.status_code}")
        print(f"Total Time for {BATCH_SIZE} images: {total_time:.2f} seconds")
        print(f"Throughput: {throughput:.2f} images/second")

if __name__ == "__main__":
    asyncio.run(run_benchmark())