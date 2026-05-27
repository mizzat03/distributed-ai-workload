import grpc
from concurrent import futures
import sys
import os

# This path hack allows the worker node to find the proto folder 
root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

# Add BOTH the root folder and the proto folder to Python's searchable path
sys.path.append(root_dir)
sys.path.append(os.path.join(root_dir, 'proto'))

from proto import inference_pb2
from proto import inference_pb2_grpc

# Import your existing PyTorch logic
from ml_service import get_prediction 

class InferenceServer(inference_pb2_grpc.InferenceServiceServicer):
    """
    This class implements the 'Predict' RPC method we defined in the .proto file.
    It inherits from the auto-generated Servicer class.
    """
    def Predict(self, request, context):
        try:
            # 1. Extract the raw bytes from the gRPC request
            image_bytes = request.image_data
            
            # 2. Run the PyTorch inference (this blocks until finished)
            print("Received image chunk. Running inference...")
            class_name, confidence = get_prediction(image_bytes)
            print(f"Success -> {class_name}: {confidence:.4f}")
            
            # 3. Package and return the response in the exact format the Master expects
            return inference_pb2.InferenceResponse(
                prediction=class_name,
                confidence=confidence
            )
            
        except Exception as e:
            # 4. Error Handling: If PyTorch crashes, safely tell the Master
            print(f"Error processing image: {e}")
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"Worker PyTorch Error: {str(e)}")
            # Return an empty response so the channel doesn't hang
            return inference_pb2.InferenceResponse()

def serve():
    """
    Boots up the gRPC server and keeps it alive to listen for Master requests.
    """
    # 1. Create a server with a thread pool to handle concurrent requests
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    
    # 2. Attach our custom logic to the server engine
    inference_pb2_grpc.add_InferenceServiceServicer_to_server(InferenceServer(), server)
    
    # 3. Open port 50051 (the standard default port for gRPC)
    server.add_insecure_port('[::]:50051')
    
    print("Worker Node is live. Listening for master commands on port 50051...")
    server.start()
    
    # Keep the script running forever
    server.wait_for_termination()

if __name__ == '__main__':
    serve()