import socket, sys, os

# Main function, is called at end of program
def main():
    listenPort = str()
    # Open socket for incoming connection from client with desired port #
    if len(sys.argv) < 2:
        print("\nCorrect format: python", sys.argv[0], "<server port>\n")
    else:
        listenPort = sys.argv[1]
    welcomeSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    welcomeSock.bind(('', int(listenPort)))
    welcomeSock.listen(1)

    # Forever wait for incoming connection from client
    while True:
        print("\nWaiting for connection...\n")   
        clientSock, addr = welcomeSock.accept()
        print("Control connection accepted from client:", addr, "\n")

        # Receive command from client through control connection 
        # and call a funcion accordingly
        while True:
          command = str()
          commandSize = str()
          commandSize = recvAll(clientSock, 10)
          if commandSize.decode():
            command = recvAll(clientSock, int(commandSize.decode())).decode()
          if command == 'put':
            downloadFile(clientSock, addr)
          if command == 'get':
            uploadFile(clientSock, addr)
          if command == 'ls':
            dirList(clientSock, addr)
          if command == 'quit':
             break

        clientSock.close()
        print("Control connection closed.\n")
        print("Bye.\n")
        return

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

# Server retrieves ephemeral port and creates data connection when requested by client
# (ephemeral port generated and submited by client along with the request)
def createDataConnection(clientSock, addr):
    ephemeralPort = str()
    ephemeralPortSize = str()
    ephemeralPortSize = recvAll(clientSock, 10)
    ephemeralPort = int(recvAll(clientSock, int(ephemeralPortSize.decode())).decode())
    dataSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    dataSock.connect((addr[0], ephemeralPort))
    return dataSock, ephemeralPort

# Get file name for files being uploaded or downloaded by client
def getFileName(clientSock):
    FileName = str()
    FileNameSize = str()
    FileNameSize = recvAll(clientSock, 10)
    FileName = recvAll(clientSock, int(FileNameSize.decode())).decode()
    return FileName

# Receive file that client is uploading
def downloadFile(clientSock, addr):
    fileName = getFileName(clientSock)
    dataSock, ephemeralPort = createDataConnection(clientSock, addr)  # Create data connection and connect to client to begin data transfer
    print("Data connection successfully established with client on ephemeral port #", ephemeralPort ,"\n")
    fileData = str()
    fileSize = str()
    fileSize = recvAll(dataSock, 10)
    fileData = recvAll(dataSock, int(fileSize.decode()))
    print("Receiving...\n")
    with open("server_files\\" + fileName, "wb") as file:
       file.write(fileData)
    file.close()
    print("File transfer completed.\n")
    print("File name:", fileName, "\n")
    print("Bytes received from client:", int(fileSize.decode()), "\n")
    dataSock.close()
    print("Data connection to client closed.\n")
    return

# Send file that client is downloading
def uploadFile(clientSock, addr):
    fileName = getFileName(clientSock)
    dataSock, ephemeralPort = createDataConnection(clientSock, addr)  # Create data connection and connect to client to begin data transfer
    print("Data connection successfully established with client on ephemeral port #", ephemeralPort ,"\n")
    fileObj = open("server_files\\" + fileName, "rb")
    print("Sending...\n")
    while True:
        fileData = fileObj.read(65536)
        if fileData:
            dataSizeStr = str(len(fileData))
            while len(dataSizeStr) < 10:
                dataSizeStr = "0" + dataSizeStr
            fileData = dataSizeStr.encode() + fileData
            numSent = 0
            while len(fileData) > numSent:
                numSent += dataSock.send(fileData[numSent:])  # Using server socket for data connection established by server to send data back to client
        else:
            break
    print("File transfer completed.\n")
    print("File name:", fileName, "\n")
    print("Bytes sent to client:", numSent, "\n")
    dataSock.close()
    print("Data connection to client closed.\n")
    return

# Send list of files in server file directory (server_files) to client
def dirList(clientSock, addr):
  dataSock, ephemeralPort = createDataConnection(clientSock, addr)  # Create data connection and connect to client to begin data transfer
  print("Data connection successfully established with client on ephemeral port #", ephemeralPort ,"\n")
  print("Sending...\n")
  for fileName in os.listdir("server_files"):  # "commands" module has been depreciated in Python 3, using "os" instead
    fileNameSizeStr = str(len(fileName))
    while len(fileNameSizeStr) < 10:
        fileNameSizeStr = "0" + fileNameSizeStr
    fileName = fileNameSizeStr.encode() + str(fileName).encode()
    numSent = 0
    while len(fileName) > numSent:
        numSent += dataSock.send(fileName[numSent:])  # Using server socket for data connection established by server to send data back to client
  dataSock.close()
  print("Data connection to client closed.\n")
  return

main()