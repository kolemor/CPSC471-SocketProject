import socket
import sys

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
    #
    # User command handling code
    #

    uploadFile(connSocket)  # For testing connections
    # downloadFile(connSocket)
    # listDir(connSocket)

    connSocket.close()
    print("Control connection to FTP server closed.\n")

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
    # Get the file name from user command in live version
    fileName = input("Enter filename to upload:")
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
    return


def listDir(connSocket):
    return


main()
