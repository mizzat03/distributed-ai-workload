from fastapi import UploadFile
import asyncio
import os

from .grpc_client import send_image_to_worker
from .aggregator import aggregate_results



raw_worker_string = os.getenv("WORKER_ADDRESSES", "localhost:50051")
LIST_OF_WORKERS = raw_worker_string.split(",")
NUM_OF_WORKERS = len(LIST_OF_WORKERS)

async def process_batch(files: list[UploadFile]):

    tasks = []
    
    # 1. Loop through the files
    for i, file in enumerate(files):
        # Read the bytes 
        image_bytes = await file.read()
        
        # We deal out the workers like a deck of cards
        worker_address = LIST_OF_WORKERS[i % NUM_OF_WORKERS]
        
        # 2. Create the coroutine
        coroutine = send_image_to_worker(
            image_bytes=image_bytes, 
            image_id=i, 
            worker_address=worker_address
        )
        
        # Add it to our list of tasks
        tasks.append(coroutine)
        
    # 3. Outside the loop, run them ALL concurrently!
    unordered_results = await asyncio.gather(*tasks) # It gathers into list of tuples
    
    # 4. Pass the messy results to your aggregator
    final_sorted_results = aggregate_results(unordered_results)
    
    return final_sorted_results


