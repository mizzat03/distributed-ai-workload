import grpc
import sys
import os

DEFAULT_WORKER = os.getenv("WORKER_ADDRESS", "localhost:50051")

# This path hack allows the worker node to find the proto folder 
root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

# Add BOTH the root folder and the proto folder to Python's searchable path
sys.path.append(root_dir)
sys.path.append(os.path.join(root_dir, 'proto'))

from proto import inference_pb2
from proto import inference_pb2_grpc



def send_image_to_worker(image_bytes: bytes, worker_address: str = DEFAULT_WORKER) -> tuple:
    """
    Acts as the client. Takes raw image bytes, sends them to the gRPC worker,
    and returns the prediction and confidence.
    """
    
    # 1. Open the network connection (The Channel)
    # Using 'insecure_channel' because we aren't using SSL/HTTPS certificates locally
    with grpc.insecure_channel(worker_address) as channel:
        
        # 2. Create the Stub (The Translator)
        stub = inference_pb2_grpc.InferenceServiceStub(channel)
        
        # 3. Package the data into the Protocol Buffer format
        request = inference_pb2.InferenceRequest(image_data=image_bytes)
        
        try:
            # 4. Make the actual RPC call! 
            # We set a timeout of 10 seconds so the master doesn't freeze forever if a worker dies
            response = stub.Predict(request, timeout=10.0)
            
            # Return exactly what FastAPI expects
            return response.prediction, response.confidence
            
        except grpc.RpcError as e:
            # If the worker crashes or the network drops, gRPC throws an RpcError
            print(f"gRPC call failed: {e.details()}")
            raise