import sys
import socket
import select
import os

CHATSERVER_PORT = int(sys.argv[1]) # port chat server listens on (long-lived) for terminal # 8822
WEBSERVER_PORT = int(sys.argv[2]) # open short lived connection with this port # 8823
FILE_PATH = 'chat_history.txt'
BUFFER_SIZE = 1024

# Function to create and bind a socket
def createSocket(port):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setblocking(False)
    try:
        s.bind(('', port))
        s.listen(5)
    except Exception as e:
        print(f"Error creating socket on port {port}: {e}")
        sys.exit(1)
    return s

# Create server sockets
hostname = socket.gethostname()

terminal_socket = createSocket(CHATSERVER_PORT)
web_socket = createSocket(WEBSERVER_PORT)

print(f'Listening on interface {hostname}')
print(f'Terminal socket is listening on port {CHATSERVER_PORT}')
print(f'Web socket is listening on port {WEBSERVER_PORT}')

terminal_clients = []
web_clients = []
inputs = []

def loadChatHistory(path):
    with open(path, 'r') as file:
        chat = file.read()
        return chat

def writeToChat(path, message):
    with open(path, 'a') as file:
        file.write(message + '\n')

def broadcastMessage(message, receiver):
    for r in receiver:
        try:
            r.send(message.encode())
            print(f'Server sent message: {message}')
        except:
            removeConnection(r)

def addWebConnection(source):
    web_clients.append(source)

def addTerminalConnection(source):
    terminal_clients.append(source)
    
def removeConnection(source):
    if source in terminal_clients:
        terminal_clients.remove(source)
    if source in web_clients:
        web_clients.remove(source)
    if source in inputs:
        inputs.remove(source)
    source.close()
            
def removeTimeStamp(chat):
    buffer = []
    lines = chat.splitlines()
    for line in lines:
        if line:
            username, message, _ = line.split(': ')
            buffer.append(f"{username}: {message}")
    return '\n'.join(buffer)

def filterMessages(chat, time):
    messages = chat.strip().split('\n')
    messages_to_send = []
    for message in messages:
        # Split the message to get the timestamp
        parts = message.rsplit(': ', 1)  # Split only at the last ': '
        if len(parts) == 2:
            msg_content, timestamp_str = parts
            timestamp = int(timestamp_str.strip())  # Convert to integer
            # Check if the received timestamp is larger
            if time == timestamp:
                messages_to_send.append(': '.join([msg_content, timestamp_str]))  # Append only the message content
    return messages_to_send

try:
    # Check file existence and create
    if not os.path.exists(FILE_PATH):
        with open(FILE_PATH, 'w') as file:
            file.write('Welcome to Discordn\'t. Start chatting here\n\n')
        print('Chat History Created!')

    while True:
        print('Waiting for input...')
        inputs = [terminal_socket, web_socket] + terminal_clients + web_clients
        # print(f'inputs: {inputs}')
        readable, writable, exceptional = select.select(inputs, [], inputs)
        # print(f'readable: {readable}')
        for source in readable:
            # Turn it into a string of messages with new protocol
            chat_history = '\n'.join(loadChatHistory(FILE_PATH).split('\n')[1:])
            if source is terminal_socket: # new client
                client_socket, client_addr = source.accept()
                addTerminalConnection(client_socket)
                print(f'New terminal connection at {client_addr}')

                if chat_history:
                    client_socket.send(chat_history.encode())
                else:
                    welcome_message = 'Welcome to Discordn\'t'
                    writeToChat(FILE_PATH, welcome_message)
            elif source is web_socket:
                shortlived_socket, shortlived_address = source.accept()
                addWebConnection(shortlived_socket)
                # print(f'Web clients: {web_clients}')
                # print(f'Total web client(s): {len(web_clients)}')
                print(f'\nNew web connection at {shortlived_address}')

                data = shortlived_socket.recv(BUFFER_SIZE).decode()
                if data:
                    print(f'data: {data}')
                    elements = data.split(' - ')
                    if len(elements) == 2: # user request data
                        command, timestamp,  = data.split(' - ')
                        if int(timestamp) == 0: # send everything when first logged in
                            if not chat_history:
                                # chat_history = removeTimeStamp(chat_history)
                                welcome_message = 'Welcome to Discordn\'t'
                                writeToChat(FILE_PATH, welcome_message)                                
                            shortlived_socket.send(chat_history.encode())
                        # Received last=timestamp=xxxxxx != 0
                        # Similar usage of broadcastMessage for terminal clients
                        else:
                            last_message = chat_history.split('\n')[-2]
                            print(f'latest message: {last_message}')
                            for c in web_clients:
                                shortlived_socket.send(last_message.encode()) # send to web clients
                    elif len(elements) == 3: # User sent new message. write to chat
                        username, message, timestamp = data.split(' - ')
                        # Write to database
                        messageToWrite = ': '.join([username, message, timestamp])
                        print(f'messageToWrite: {messageToWrite}')
                        writeToChat(FILE_PATH, messageToWrite)
                        shortlived_socket.send('Data written successfully!'.encode())
                        # Then remove short-lived connection
                    removeConnection(shortlived_socket)              
                else:
                    print(f'Client {source.getpeername()} disconnected.')
                    removeConnection(shortlived_socket)
            else: # Terminal clients
                data = source.recv(1024).decode()
                # print(f'data: {data}')
                if data:
                    message = data.split(': ', 1)[1].strip()
                    print(f'Message received: {message}')
                    writeToChat(FILE_PATH, data)
                    broadcastMessage(data, terminal_clients)
                else:
                    print(f'Client {source.getpeername()} disconnected.')
                    removeConnection(source)
        for source in exceptional:
            print(f'Handling exception for {source.getpeername()}')
            removeConnection(source)

except KeyboardInterrupt:
    print("\nReceived KeyboardInterrupt, exiting...")
except Exception as e:
    print('Error:', e)
finally:
    terminal_socket.close()
    print('Closing socket! Exiting!')
    sys.exit(0) # successful termination 