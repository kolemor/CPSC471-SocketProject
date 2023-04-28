import socket
import sys
import os

# Default hostname
HOST = "localhost"
# Default FTP port
PORT = 21

# main function, is called at end of program


def main():
    if len(sys.argv) < 2:
        print("[*] Correct format: python " + sys.argv[0] + " <port number>\n")
    else:
        PORT = int(sys.argv[1])
        controlCONN(HOST, PORT)

# Function for handling the main connection between client and server


def controlCONN(HOST, PORT):
    # establish the socket
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        # bind the socket to the server ip and port number
        s.bind((HOST, PORT))
        # listen for connections, the number I believe handles concurrent connections
        s.listen(5)
        while True:
            print(f"[*] Listening as {HOST}:{PORT}")
            # accept connection from client, get the connection and address from client
            conn, addr = s.accept()
            # for test purposes, this leads directly into establishing a data connection for
            # testing file transfers. For our end product, after establishing a connection
            # with the client, the server would wait for commands from the client (ls, get, put)
            # before doing anything else
            with conn:
                print(f"[+] {addr} is connected.")
                # call the data connection function
                # Data connection is currently bugged, see related Issue in
                # github for more information
                # dataCONN(conn)
                fileUpload(conn)
            # close main connection. Once again, for our end product, the server would keep the
            # connection open so the client can run more commands, until it gets a command from
            # the client to close the connect, i.e. 'quit'
            print(f"[-] {addr} is disconnected.")
            break

# Function for handling temporary connections for file transfers


def dataCONN(conn):
    # create socket
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as d:
        # make it an ephemeral port, i.e. give it a random port number
        d.bind(('', 0))
        # store that random port number in a variable
        ephem = d.getsockname()[1]
        # send that port number to the client so it know which port to connect to
        conn.send(f"{ephem}".encode())
        # listen for the connection from the client
        d.listen(1)
        # most likely don't need this while loop, but was lazy and kept it in
        # from when I copied my code from the control connection
        while True:
            print(f"[*] Awaiting data connection as {HOST}:{ephem}")
            # establish connection
            dconn, addr = d.accept()
            # do the task the connection was established for, i.e. either file
            # upload or download
            with dconn:
                print(f"[+] data connection established with {addr}")
                fileUpload(dconn)
            # close connection, as this is a temporary connection, after the task
            # is complete automatically close the connection
            print(f"[-] data connection closed for {addr}")
            break

# Test function to test receiving file from client


def fileUpload(dconn):
    # buffer size for recieving data from client
    BUFFER_SIZE = 4096
    # a delimiter for when the client sends the file name / size, The way I coded it
    # the client sends both information at once, so need the separator for separating them
    SEPARATOR = "<SEPARATOR>"
    # recieve file information (which client sends first after connection is established)
    rcvTemp = dconn.recv(BUFFER_SIZE).decode()
    # separate the raw data into its apporiate parts
    filename, filesize = rcvTemp.split(SEPARATOR)
    # remove a path from the filename if it was sent with one, so we're left with just
    # the name of the file
    filename = os.path.basename(filename)
    fs = 0
    # this handles transfering of the file
    with open(filename, "wb") as f:
        while True:
            bytes_read = dconn.recv(BUFFER_SIZE)
            fsTemp = sys.getsizeof(bytes_read)
            fs += fsTemp
            if not bytes_read:
                break
            f.write(bytes_read)
    print(f"[+] File {filename} received")
    print(f"[DEBUG] Total file size: {filesize}")
    print(f"[DEBUG] file size received: {fs}")


if __name__ == '__main__':
    main()
