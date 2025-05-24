import socket
import threading
import sys
import os
import os.path
import mimetypes
import json
import re

WEBSERVER_PORT = int(sys.argv[1]) # the port used to server website # 8824
# open short lived connection with this host:port http://desktop-7rlmcg6/
ADDRESS = sys.argv[2] # host:8823
CHAT_HOST = sys.argv[2].split(':')[0]
SHORTLIVEDTCP_PORT = int(sys.argv[2].split(':')[1])
CURRENT_DIR = os.getcwd()
BUFFER_SIZE = 2048
WEBPAGE = 'index.html'

# -------------- API Endpoints -------------- #
API_BASE = '/api/'

API_ENDPOINTS = {
    'GET_MESSAGES': f'{API_BASE}messages',
    'GET_MESSAGES_LAST': f"{API_BASE}message?last=",
    'NEW_MESSAGE': f"{API_BASE}messages",
    'STATUS': f"{API_BASE}login"
}

# Create a webserver socket to listen to incoming messages
webserver_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
webserver_socket.bind(('', WEBSERVER_PORT)) # serve webpage on port 8824

hostname = socket.gethostname()
print(f'Webserver is listening on {hostname}:{WEBSERVER_PORT}')

webserver_socket.listen(5)

users = []

# -------------- Webserver Handlers -------------- #

def serveWebpage(dir, path, http_version):
    # Serve chat interface to user
    if os.path.exists(dir) and os.path.isdir(dir):
        # Get the whole path of file
        file_path = os.path.join(dir, path[1:])
        content_type, _ = mimetypes.guess_type(file_path)
        file_path += WEBPAGE
        with open(file_path, 'rb') as f:
            content = f.read()
        response = (f'{http_version} 200 OK\r\n'
                f'Content-Type: {content_type}\r\n'
                f'Content-Length: {len(content)}\r\n')
        return response + '\n' + content.decode()
    else:
        return notFoundResponse(http_version)
    
# -------------- Helper Handlers -------------- #

def convertToJSON(chat):
    lines = chat.strip().split('\n')
    messages = []
    for line in lines:
        if ': ' in line:
            user, message = line.split(': ', 1)
            messages.append({'user': user.strip(), 'message': message.strip()})
    return json.dumps(messages, indent=2)

def getCookie(headers):
    user = ''
    for header in headers:
        if header.startswith('Cookie'):
            cookies = header.split(': ')[1]
            user = cookies.split('=')[1]
    return user

def extractTimeStamp(url_string):
    # Regular expression to match the desired format and capture the timestamp
    pattern = r'^/api/message\?last=(\d+)$'
    match = re.match(pattern, url_string)
    
    if match:
        # If there's a match, return the captured timestamp
        return match.group(1)
    
    return ''  # Return None if the format does not match
            
# -------------- Requests Handlers -------------- #

# Method for displaying chat interface
def loadChatHistory(time, http_version):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as shortlived_tcp:
        shortlived_tcp.connect((CHAT_HOST, SHORTLIVEDTCP_PORT))
        # print(f'shortlived_tcp connected to {CHAT_HOST}:{SHORTLIVEDTCP_PORT}')
        command = 'GET_AFTER - ' + time
        shortlived_tcp.send(command.encode())
        data = shortlived_tcp.recv(BUFFER_SIZE).decode()
        if data:
            json_data = convertToJSON(data)
            response = (f'{http_version} 200 OK\r\n'
                    f'Content-Type: application/json\r\n'
                    f'Content-Length: {len(json_data.encode())}\r\n'
                    f'\r\n')
            return response + json_data
        else:
            return successResponse(http_version)

def sendMessage(user, message, time, http_version):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as shortlived_tcp:
        shortlived_tcp.connect((CHAT_HOST, SHORTLIVEDTCP_PORT))
        # print(f'shortlived_tcp connected to {CHAT_HOST}:{SHORTLIVEDTCP_PORT}')
        request = f'{user} - {message} - {time}'
        # print(f'request sent: {request}\n------------')
        shortlived_tcp.send(request.encode())
        data = shortlived_tcp.recv(BUFFER_SIZE).decode()
        if data:
            print(f'Received from chat server: {data}')
            return successResponse(http_version)
        else:
            return notFoundResponse(http_version)
              
# -------------- Thread Handler -------------- #

def handleThread(conn, addr, dir):
    with conn:        
        print(f"New web client at {addr}")
        data = conn.recv(BUFFER_SIZE).decode('latin-1')
        # print(f'data: {data}')
        
        headers = data.split('\r\n')
        # `print(f'headers: {headers}')

        message = ''
        timestamp = ''
        result = headers[len(headers)-1]
        if result:
            json_message = json.loads(result)
            message, timestamp = json_message['message'].split(': ')
        
        request = headers[0]
        print(f'{request}\n-------------')
        
        # Extract method, path, and HTTP version
        method, path, http_version = request.split(' ')
                
        # Only accept GET, POST, and DELETE requests
        if method not in ['GET', 'POST', 'DELETE']:
            response = notImplementedResponse(http_version)
            conn.send(response.encode())
            return # exit program
        
        if path == '/favicon.ico':
            response = successResponse(http_version)
            conn.send(response.encode())
        
        # Handle thread for different purposes
        if method == 'GET': # server static webpage
            if path == '/':
                response = serveWebpage(dir, path, http_version)
            elif path.startswith(API_ENDPOINTS['GET_MESSAGES']):
                response = loadChatHistory('0', http_version)
            elif path.startswith(API_ENDPOINTS['GET_MESSAGES_LAST']):
                timestamp = extractTimeStamp(path)
                response = loadChatHistory(timestamp, http_version)
            else: # other path for GET requests
                response = notImplementedResponse(http_version)
        elif method == 'POST': # communicate with chat server
            cookie = getCookie(headers)
            if len(users) == 0:
                users.append(cookie)
            if path == API_ENDPOINTS['STATUS']: # login user
                # print(f'Got cookie: {cookie}')
                response = successResponse(http_version)
            elif path == API_ENDPOINTS['NEW_MESSAGE']:
                # print(f'Got cookie2 : {users[0]}')
                # print(f'Got timestamp: {timestamp}')
                response = sendMessage(users[0], message, timestamp, http_version)
            else:
                response = notImplementedResponse(http_version)
        elif method == 'DELETE': # logout user and delete cookie
            response = successResponse(http_version)
        conn.send(response.encode())
            
# -------------- Response Handlers -------------- #

def successResponse(http_version):
    return f'{http_version} 200 OK\r\n'

def notImplementedResponse(http_version):
    return f'{http_version} 501 Not Implemented\r\n'

def notFoundResponse(http_version):
    return f'{http_version} 404 Not Found\r\n'

# -------------- Multi-threaded Webserver -------------- #
        
try:
    while True:
        client_socket, client_address = webserver_socket.accept()
        # Start a multi-threaded webserver
        thread = threading.Thread(target=handleThread, args=(client_socket, client_address, CURRENT_DIR)) 
        thread.start()  
            
except KeyboardInterrupt:
    print("\nReceived KeyboardInterrupt, exiting...")
except Exception as e:
    print('Error:', e)
finally:
    webserver_socket.close()
    print('Closing socket! Exiting!')
    sys.exit(0) # successful termination