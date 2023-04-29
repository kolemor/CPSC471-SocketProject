import socket
import sys

BUFFER_SIZE = 1024

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
    print("Client Main Menu:")
    print("get <filename> - download a file from the server")
    print("put <filename> - upload a file to the server")
    print("ls - list files on the server")
    print("quit - exit the client")

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
        if command == "get":
            if len(args) == 1:
                print("get function called")
                downloadFile(connSocket)
            else:
                print("Invalid get command. Usage: 'get <filename>'.")
        elif command == "put":
            if len(args) == 1:
                print("Put command called. Usage: 'put <filename>'.")
                uploadFile(connSocket, args[0])
            else:
                print("Invalid command. Usage: 'put <filename>'.")
        elif command == "ls":
            print("LS command invoked in client")
            list_files(connSocket)
        elif command == "quit":
            return False
            # quit_ftp()
        else:
            print("Invalid command. Please enter 'get', 'put', 'ls', or 'quit'.")


# Main function, called at the end


def main():
    if len(sys.argv) < 2:
        print("\nCorrect format: python",
              sys.argv[0], "<server hostname> <server port>\n")
    else:
        host = sys.argv[1]
        port = int(sys.argv[2])
        controlCONN(host, port)


def list_files(connSocket):
    # Send the LIST command to the server
    connSocket.sendall(b'LIST')

    # Receive the response from the server
    data = connSocket.recv(BUFFER_SIZE).decode()

    # Print the response to the console
    print(data)

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

# Upload the file that server will be downloading using the data connection
# established by server


def uploadFile(connSocket):
    print("Requesting data connection from FTP server...\n")
    serverSock, addr, ephemeralPort = requestDataConnection(connSocket)
    print("Data connection accepted from server on ephemeral port #:",
          ephemeralPort, "\n")
    fileName = "test1.txt"  # Get the file name from user command in live version
    fileObj = open("files/" + fileName, "rb")
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
                # Using the server socket for data connection established by server to send data back
                numSent += serverSock.send(fileData[numSent:])
        else:
            break
    print("Upload completed.\n")
    print("Uploaded file:", fileName, "\n")
    print("Number of bytes sent to FTP server:", numSent, "\n")
    serverSock.close()
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


def listDir(connSocket):
    return


if __name__ == '__main__':
    main()
