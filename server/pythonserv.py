import socket
import sys
import os

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
    shut = False
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
        while True:
            command = str()
            commandSize = str()
            commandSize = recvAll(clientSock, 10)
            if commandSize.decode():
                command = recvAll(clientSock, int(
                    commandSize.decode())).decode()
            if command == 'put':
                clientSock.send("150".encode())
                downloadFile(clientSock, addr)
            elif command == 'get':
                clientSock.send("150".encode())
                uploadFile(clientSock, addr)
            elif command == 'ls':
                clientSock.send("150".encode())
                dirList(clientSock)
            elif command == 'quit':
                print("closing connection to client: ", addr, "\n")
                clientSock.send("150".encode())
                break
            elif command == 'shut':
                shut = True
                print("Shutting down...\n")
                clientSock.send("150".encode())
                break
            else:
                print("Unexpected error: recieved unknown command\n")
                clientSock.send("404".encode())

        clientSock.close()
        if shut:
            print("Goodbye...\n")
            break

# Receive incoming bytes (including command, ephemeral port and file data)


def recvAll(clientSock, numBytes):
    data = str()
    tmpData = str()
    data = data.encode()
    while len(data) < numBytes:
        tmpData = clientSock.recv(numBytes)
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
    ephemeralPort = int(recvAll(clientSock, int(
        ephemeralPortSize.decode())).decode())
    dataSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    dataSock.connect((addr[0], ephemeralPort))
    return dataSock, ephemeralPort


def getFileName(clientSock):
    FileName = str()
    FileNameSize = str()
    FileNameSize = recvAll(clientSock, 10)
    FileName = recvAll(clientSock, int(FileNameSize.decode())).decode()
    return FileName

# Download file that client is uploading


def downloadFile(clientSock, addr):
    fileName = getFileName(clientSock)
    # Create data connection and connect to client to begin data transfer
    dataSock, ephemeralPort = createDataConnection(clientSock, addr)
    print("Data connection successfully established with client on ephemeral port #:",
          ephemeralPort, "\n")
    fileData = str()
    fileSize = str()
    fileSize = recvAll(dataSock, 10)

    print("Downloading...\n")
    print(f"fileSize: {fileSize}")

    fileData = recvAll(dataSock, int(fileSize.decode()))
    with open(fileName, "wb") as file:
        file.write(fileData)
    file.close()
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
