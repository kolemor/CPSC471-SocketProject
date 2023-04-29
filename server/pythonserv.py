import socket, sys, os

# Main function, is called at end of program
def main():
  HOST = "localhost"
  if len(sys.argv) < 2:
    print("Correct format: python " + sys.argv[0] + " <port number>\n")
  else:
    PORT = int(sys.argv[1])
    createControlConnection(PORT)

def createControlConnection(port):
  HOST = "localhost"
  # Open socket for incoming connection from client
  welcomeSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  welcomeSock.bind((HOST, port))
  welcomeSock.listen(1)

  # Forever wait for incoming connection from client
  while True:
    print("\nWaiting for connection...\n")   
    clientSock, addr = welcomeSock.accept()
    print("Control connection accepted from client:", addr, "\n")

    # Receive a command from client through control connection here 
    # and call the get, put or list funcion accordingly
    #
    # Client command handling code
    #
    cmd = clientSock.recv(1024).decode()
    if cmd == 'LIST':
      dirList(clientSock)
    #elif cmd == 'PUT':
    #elif cmd == 'GET':
    elif cmd == 'QUIT':
      clientSock.close()
      break
    else:
       print("Unexpected error: recieved unknown command")
    #downloadFile(clientSock, addr) # For testing connections
    # uploadFile(clientSock, addr)
    # dirList(clientSock, addr)

# Receive incoming bytes (including command, ephemeral port and file data)
def recvAll(clientSock, numBytes):
  data = str()
  tmpData = str()
  data = data.encode()
  while len(data) < numBytes:
     tmpData =  clientSock.recv(numBytes)
     if not tmpData:
        break
     data += tmpData
  return data

# Server retrieves the ephemeral port and creates data connection when requested by client
# (ephemeral port generated and submited by client along with the request)
def createDataConnection(clientSock, addr):
    ephemeralPort = str()
    ephemeralPortSize = str()
    ephemeralPortSize = recvAll(clientSock, 10)
    ephemeralPort = int(recvAll(clientSock, int(ephemeralPortSize.decode())).decode())
    dataSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    dataSock.connect((addr[0], ephemeralPort))
    return dataSock, ephemeralPort

# Download file that client is uploading
def downloadFile(clientSock, addr):
    dataSock, ephemeralPort = createDataConnection(clientSock, addr)  # Create data connection and connect to client to begin data transfer
    print("Data connection successfully established with client on ephemeral port #:", ephemeralPort ,"\n")
    fileData = str()
    fileSize = str()
    fileSize = recvAll(dataSock, 10)
    print("Downloading...\n")
    fileData = recvAll(dataSock, int(fileSize.decode()))
    print("Data Content:", fileData.decode(), "\n")  # Save the file in the files\ directory in the live version
    print("Number of bytes received from client:", int(fileSize.decode()), "\n")
    print("Download Successful!\n")
    dataSock.close()
    print("Data connection to client closed.\n")
    return

# Upload file that client is downloading
def uploadFile(clientSock, addr):
  return

# Retrun a list of existing files in the files\ directory to client
def dirList(clientSock):
  files = os.listdir('.')
  response = '\n'.join(files).encode()
  clientSock.send(response)
  return

main()