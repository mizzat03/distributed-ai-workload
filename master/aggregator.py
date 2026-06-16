def aggregate_results(unordered_results: list[tuple]):
    
    # Sort the list based on the ID
    sorted_results = sorted(unordered_results, key=lambda x: x[2])
    
    # Clean it up into a dictionary for the FastAPI response
    json_response = []
    for result in sorted_results:
        json_response.append({
            "image_id": result[2],
            "prediction": result[0],
            "confidence": result[1]
        })
        
    return json_response