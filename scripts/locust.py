import os
from locust import HttpUser, task, between

class PhotoUploadUser(HttpUser):
    wait_time = between(1, 5)
    host = "http://localhost:8000"
    IMAGE_PATH = "../data/images/elephant.jpg" 

    def on_start(self):
        """Executed when a user starts the test.Checks if test image exists"""
        if not os.path.exists(self.IMAGE_PATH):
            print(f"Error: {self.IMAGE_PATH} not found in the directory.")
            self.environment.runner.quit()

    @task
    def upload_photo(self):
        """Task to upload a photo to the server."""
        
        with open(self.IMAGE_PATH, "rb") as image_file:
            files = {
                "files": (os.path.basename(self.IMAGE_PATH), image_file, "image/jpeg")
            }
            
            # Perform the POST request
            with self.client.post(
                "/infer", 
                files=files, 
                catch_response=True
            ) as response:
                if response.status_code == 200:
                    response.success()
                else:
                    response.failure(f"Failed with status {response.status_code}")