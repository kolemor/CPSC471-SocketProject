import socket, sys, os

BUFFER_SIZE = 1024

# Main function, called at the end
def main():
    if len(sys.argv) < 2:
        print("\nCorrect format: python",
              sys.argv[0], "<server hostname> <server port>\n")
    else:
        host = sys.argv[1]
        port = int(sys.argv[2])
        controlCONN(host, port)

# Control connection function
def controlCONN(host, port):
    connSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    print(f"\nConnecting to FTP server: ({host}, {port})\n")
    connSocket.connect((host, port))
    print("Control connection to FTP server successful.\n")

    # Process user commands here and send ...
    handle_user_input(connSocket)

    connSocket.close()
    print("Control connection to FTP server closed.\n")


def handle_user_input(connSocket):
    menuCMD()
    """Asks the user for input and sends the correct command to other functions for get, put, ls, and quit.
       """
    while True:
        # Ask for user input
        user_input = input("ftp> ")

        # Split the user input into command and arguments
        input_parts = user_input.split()
        command = input_parts[0].lower()
        args = input_parts[1:]

        # Check which command was given and call the appropriate function
        if command == "menu":
            menuCMD()
        elif command == "get":
            if len(args) == 1:
                print("get function called")
                downloadFile(connSocket)
            else:
                print("Invalid get command. Usage: 'get <filename>'.")
        elif command == "put":
            if len(args) == 1:
                print("Put command called. Usage: 'put <filename>'.")
                if putCMD(connSocket, args[0]):
                    print("Server error code encountered: resubmit command")
            else:
                print("Invalid command. Usage: 'put <filename>'.")
        elif command == "ls":
            print("LS command invoked in client")
            if lsCMD(connSocket):
                print("Server error code encountered: resubmit command")
        elif command == "quit":
            if quitCMD(connSocket):
                print("Server error code encountered: resubmit command")
            else:
                print('Goodbye...\n')
                return False
        elif command == "shut":
            if shutCMD(connSocket):
                print("Server error code encountered: resubmit command")
            else:
                print('Goodbye...\n')
                return False
        else:
            print("Invalid command. Please enter 'get', 'put', 'ls', or 'quit'.")

# Send commmand to server using control connection socket
def sendCommand(connSock, command):
    commandSizeStr = str(len(str(command)))
    while len(commandSizeStr) < 10:
        commandSizeStr = "0" + commandSizeStr
    command = commandSizeStr.encode() + str(command).encode()
    numSent = 0 
    while len(command) > numSent:
        numSent += connSock.send(command[numSent:])
    CODE = int(connSock.recv(1024).decode())
    if CODE == 150:
        return True
    else:
        return False

# Handles menu command
def menuCMD():
    print("Client Main Menu:")
    print("menu - list commands")
    print("get <filename> - download a file from the server")
    print("put <filename> - upload a file to the server")
    print("ls - list files on the server")
    print("quit - exit the client")
    print("shut - shutdown both client and server\n")

# Handles put command
def putCMD(connSocket, fileName):
    if sendCommand(connSocket, 'put'):
        uploadFile(connSocket, fileName)
    else:
        return True

# Handles ls command
def lsCMD(connSocket):
    # Send the LIST command to the server
    if sendCommand(connSocket, 'ls'):
        # Receive the response from the server
        data = connSocket.recv(BUFFER_SIZE).decode()
        # Print the response to the console
        print(data)
    else:
        return True

# handles quit command
def quitCMD(connSocket):
    if sendCommand(connSocket, 'quit'):
        print("Closing connection between client and server...\n")
    else:
        return True

# Handles shutdown command
def shutCMD(connSocket):
    if sendCommand(connSocket, 'shut'):
        print("Shutting down server and client...\n")
    else:
        return True

# Client requests data connection from server and creates socket with
# ephemeral prot for incoming connection from server
def requestDataConnection(connSocket):
    # Generate random ephemeral port for data connection from server
    welcomeSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    welcomeSocket.bind(('', 0))
    ephemeralPort = welcomeSocket.getsockname()[1]
    ephemeralPortCopy = ephemeralPort

    # Send the ephemeral port to server and wait for data connection
    ephemeralPortSizeStr = str(len(str(ephemeralPort)))
    while len(ephemeralPortSizeStr) < 10:
        ephemeralPortSizeStr = "0" + ephemeralPortSizeStr
    ephemeralPort = ephemeralPortSizeStr.encode() + str(ephemeralPort).encode()
    numSent = 0
    while len(ephemeralPort) > numSent:
        numSent += connSocket.send(ephemeralPort[numSent:])
    print("Waiting for data connection from server on ephemeral port#:",
          ephemeralPortCopy, "\n")
    welcomeSocket.listen(1)
    serverSock, addr = welcomeSocket.accept()
    return serverSock, addr, ephemeralPortCopy

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

# Upload the file that server will be downloading using the data connection
# established by server
def uploadFile(connSocket, fileName):
    sendFileName(connSocket, fileName)
    print("Requesting data connection from FTP server...\n")
    serverSock, addr, ephemeralPort = requestDataConnection(connSocket)
    print("Data connection accepted from server on ephemeral port #:",
          ephemeralPort, "\n")
    fileSize = os.path.getsize(fileName)
    #serverSock.send(f"{fileSize}".encode())
    fileObj = open(fileName, "rb")
    print("Uploading...\n")
    numSent = 0
    fileData = 0
    while True:
        fileData = fileObj.read(65536)
        if fileData:
            dataSizeStr = str(len(fileData))
            while len(dataSizeStr) < 10:
                dataSizeStr = "0" + dataSizeStr
            fileData = dataSizeStr.encode() + fileData
            numSent = 0
            while len(fileData) > numSent:
                # Using the server socket for data connection established by server to send data back
                numSent += serverSock.send(fileData[numSent:])
        else:
            break
    print("Upload completed.\n")
    print("Uploaded file:", fileName, "\n")
    print("Number of bytes sent to FTP server:", numSent, "\n")
    serverSock.close()
    fileObj.close()
    print("Data connection closed.\n")
    return


def downloadFile(connSocket):
    serverSock, addr, ephemeralPort = requestDataConnection(connSocket)
    print("download function working??")
    fileName = input("enter dl file: ")
    try:
        with open(fileName, "wb") as file:
            print("Downloading...\n")
            serverSock.send(fileName.encode())
            fileSize = int(serverSock.recv(1024))
            data = b''
            while len(data) < fileSize:
                packet = serverSock.recv(1024)
                if not packet:
                    break
                data += packet
            file.write(data)
            print("File downloaded sucessfully. \n")
    except FileNotFoundError:
        print(f"Error: {fileName} not found. \n")
    serverSock.close()
    print("Data connection closed. \n")
    return

if __name__ == '__main__':
    main()
