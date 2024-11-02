from flask import Flask, request, jsonify, render_template
from flask_socketio import SocketIO
from flask_graphql import GraphQLView
from flask_cors import CORS  # Import CORS
import graphene
import grpc
from concurrent import futures
import calculator_pb2_grpc as pb2_grpc
import calculator_pb2 as pb2

# Initialize Flask app and enable CORS
app = Flask(__name__)
CORS(app)  # Enable CORS for all routes
socketio = SocketIO(app, cors_allowed_origins='*')  # Allow all origins for Socket.IO

# REST API Endpoint for Addition
@app.route('/add', methods=['GET'])
def add():
    a = request.args.get('a', type=int)
    b = request.args.get('b', type=int)
    if a is None or b is None:
        return jsonify({"error": "Please provide both 'a' and 'b'."}), 400
    return jsonify({"result": a + b})

# REST API Endpoint for Subtraction
@app.route('/subtract', methods=['GET'])
def subtract():
    a = request.args.get('a', type=int)
    b = request.args.get('b', type=int)
    if a is None or b is None:
        return jsonify({"error": "Please provide both 'a' and 'b'."}), 400
    return jsonify({"result": a - b})

# SOAP API using Zeep for Addition and Subtraction
@app.route('/soap/add', methods=['POST'])
def soap_add():
    a = request.json.get('a')
    b = request.json.get('b')
    if a is None or b is None:
        return jsonify({"error": "Please provide both 'a' and 'b'."}), 400
    return jsonify({"result": a + b})

@app.route('/soap/subtract', methods=['POST'])
def soap_subtract():
    a = request.json.get('a')
    b = request.json.get('b')
    if a is None or b is None:
        return jsonify({"error": "Please provide both 'a' and 'b'."}), 400
    return jsonify({"result": a - b})

# GraphQL API Endpoint
class Query(graphene.ObjectType):
    add = graphene.Int(a=graphene.Int(), b=graphene.Int())
    subtract = graphene.Int(a=graphene.Int(), b=graphene.Int())

    def resolve_add(self, info, a, b):
        return a + b

    def resolve_subtract(self, info, a, b):
        return a - b

app.add_url_rule('/graphql', view_func=GraphQLView.as_view('graphql', schema=graphene.Schema(query=Query), graphiql=True))

# WebSocket API Endpoint for Addition and Subtraction
@socketio.on('add')
def handle_add(json):
    a = json.get('a')
    b = json.get('b')
    result = a + b
    socketio.emit('result', {'result': result})

@socketio.on('subtract')
def handle_subtract(json):
    a = json.get('a')
    b = json.get('b')
    result = a - b
    socketio.emit('result', {'result': result})

# gRPC Server Implementation with Addition and Subtraction
class Calculator(pb2_grpc.CalculatorServicer):
    def Add(self, request, context):
        return pb2.AddResponse(result=request.a + request.b)

    def Subtract(self, request, context):
        return pb2.SubtractResponse(result=request.a - request.b)

def run_grpc_server():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    pb2_grpc.add_CalculatorServicer_to_server(Calculator(), server)
    server.add_insecure_port('[::]:50051')
    server.start()
    server.wait_for_termination()

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    # Start gRPC server in a separate thread.
    import threading
    grpc_thread = threading.Thread(target=run_grpc_server)
    grpc_thread.start()
    
     # Start Flask application with SocketIO on port 80 using SSL.
    socketio.run(app, host='0.0.0.0', port=443, ssl_context=('cert.pem', 'key.pem'), debug=True)  # Listen on all interfaces.
