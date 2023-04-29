import socket, sys

# Main function, called at the end
def main():
    if len(sys.argv) < 3:
        print("\nCorrect format: python", sys.argv[0], "<server hostname> <server port>\n")
    else:
        host = sys.argv[1]
        port = int(sys.argv[2])
        connSock = controlCONN(host, port)

    # User terminal command handling
    while True:
        userInput = input("\nftp> ").split()
        if len(userInput) > 1:
            command = userInput[0]
            fileName = userInput[1]
        else:
            command = userInput[0]
        if command == "put":
            uploadFile(connSock, fileName)
        if command == "get":
            downloadFile(connSock, fileName)
        if command == "ls":
            listDir(connSock)
        if command == "quit":
            quit(connSock)
            break

    connSock.close()
    print("Control connection to FTP server closed.\n")
    print("Bye.\n")
    return

# Control connection function
def controlCONN(host, port):
    connSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    print(f"\nConnecting to FTP server: ({host}, {port})\n")
    connSock.connect((host, port))
    print("Control connection to FTP server successful.")
    return connSock

# Client requests data connection from server and creates socket with 
# ephemeral prot for incoming connection from server
def requestDataConnection(connSock):
    # Generate random ephemeral port for data connection from server
    welcomeSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    welcomeSock.bind(('',0))
    ephemeralPort = welcomeSock.getsockname()[1]
    ephemeralPortCopy = ephemeralPort

    # Send ephemeral port to server and wait for data connection
    ephemeralPortSizeStr = str(len(str(ephemeralPort)))
    while len(ephemeralPortSizeStr) < 10:
        ephemeralPortSizeStr = "0" + ephemeralPortSizeStr
    ephemeralPort = ephemeralPortSizeStr.encode() + str(ephemeralPort).encode()
    numSent = 0 
    while len(ephemeralPort) > numSent:
        numSent += connSock.send(ephemeralPort[numSent:])
    print("Waiting for data connection from server on ephemeral port #", ephemeralPortCopy, "\n")
    welcomeSock.listen(1)
    serverSock, addr = welcomeSock.accept()
    return serverSock, addr, ephemeralPortCopy

# Send commmand to server using control connection socket
def sendCommand(connSock, command):
    commandSizeStr = str(len(str(command)))
    while len(commandSizeStr) < 10:
        commandSizeStr = "0" + commandSizeStr
    command = commandSizeStr.encode() + str(command).encode()
    numSent = 0 
    while len(command) > numSent:
        numSent += connSock.send(command[numSent:])
    return

# Send file name being uploaded or downloaded to server
def sendFileName(connSock, fileName):
    fileNameSizeStr = str(len(str(fileName)))
    while len(fileNameSizeStr) < 10:
        fileNameSizeStr = "0" + fileNameSizeStr
    fileName = fileNameSizeStr.encode() + str(fileName).encode()
    numSent = 0 
    while len(fileName) > numSent:
        numSent += connSock.send(fileName[numSent:])
    return

# Receive incoming bytes from data connection socket initiated by server
def recvAll(serverSock, numBytes):
  data = str()
  tmpData = str()
  data = data.encode()
  while len(data) < numBytes:
     tmpData =  serverSock.recv(numBytes)
     if not tmpData:
        break
     data += tmpData
  return data

# Upload file that server will be receiving using data connection established by server
def uploadFile(connSock, fileName):
    sendCommand(connSock, 'put')
    sendFileName(connSock, fileName)
    print("Requesting data connection from FTP server...\n")
    serverSock, addr, ephemeralPort = requestDataConnection(connSock)
    print("Data connection accepted from server on ephemeral port #", ephemeralPort, "\n")
    fileObj = open("client_files\\" + fileName, "rb")
    print("Uploading...\n")
    while True:
        fileData = fileObj.read(65536)
        if fileData:
            dataSizeStr = str(len(fileData))
            while len(dataSizeStr) < 10:
                dataSizeStr = "0" + dataSizeStr
            fileData = dataSizeStr.encode() + fileData
            numSent = 0
            while len(fileData) > numSent:
                numSent += serverSock.send(fileData[numSent:])  # Using server socket for data connection established by server to send data back to client
        else:
            break
    print("Upload Successful.\n")
    serverSock.close()
    print("Data connection closed.\n")
    return

# Download file that server will be sending using data connection established by server
def downloadFile(connSock, fileName):
    sendCommand(connSock, 'get')
    sendFileName(connSock, fileName)
    print("Requesting data connection from FTP server...\n")
    serverSock, addr, ephemeralPort = requestDataConnection(connSock)
    print("Data connection accepted from server on ephemeral port #", ephemeralPort, "\n")
    fileData = str()
    fileSize = str()
    fileSize = recvAll(serverSock, 10)
    fileData = recvAll(serverSock, int(fileSize.decode()))
    print("Downloading...\n")
    with open("client_files\\" + fileName, "wb") as file:
       file.write(fileData)
    file.close()
    print("Download Successful!\n")
    serverSock.close()
    print("Data connection closed.\n")
    return

# Get list of files in server file directory (server_files)
def listDir(connSock):
    sendCommand(connSock, 'ls')
    print("Requesting data connection from FTP server...\n")
    serverSock, addr, ephemeralPort = requestDataConnection(connSock)
    print("Data connection accepted from server on ephemeral port #", ephemeralPort, "\n")
    print("Server files:\n")
    while True:
        fileName = str()
        fileNameSize = str()
        fileNameSize = recvAll(serverSock, 10)
        if fileNameSize.decode():
            fileName = recvAll(serverSock, int(fileNameSize.decode())).decode()
        if fileName:
            print("   ", fileName)
        else:
            break
    serverSock.close()
    print("\nData connection closed.\n")
    return

# Send quit command to server to let server know contoll connection has ended
def quit(connSock):
    sendCommand(connSock, 'quit')
    return

main()