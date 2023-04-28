import socket
import sys
import os
import random


# Default IP address
HOST = "local host"
# Default FTP port number
PORT = 21

# Main function, called at the end


def dataCONNECTION():
    dp = random.randint(1024, 65535)
    ds = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    ds.bind(('', dp))
    ds.listen(1)
    return ds, dp


def _ls(clientSOCKET):
    clientSOCKET.send('ls'.encode())
    ds, dp = dataCONNECTION()
    clientSOCKET.send(str(dp).encode())

    conn, _ = ds.accept()
    with conn:
        while True:
            data = conn.recv(1024)
            if not data:
                break
            print(data.decode(), end='')


def main():
    if len(sys.argv) != 3:
        print("[*] Usage: cli.py <server machine> <server port>")
        sys.exit(1)

    HOST = sys.argv[1]
    PORT = int(sys.argv[2])

    while True:
        clientSOCKET = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        clientSOCKET.connect((HOST, PORT))

        command = input("ftp> ")

        if command.startswith('get'):
            _get(clientSOCKET, command)
        elif command.startswith('put'):
            _put(clientSOCKET, command)
        elif command == 'ls':
            _ls(clientSOCKET)
        elif command == 'quit':
            clientSOCKET.send(command.encode())
            break
        else:
            print("Invalid command")

        clientSOCKET.close()


def controlCONN(HOST, PORT):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        print(f"[*] Connecting to {HOST}:{PORT}")
        s.connect((HOST, PORT))
        print("[+] Connected.")
        # Data connection is currently bugged
        # dataCONN(HOST, s)
        uploadFile(s)
    print(f"[-] Disconnected from {HOST}:{PORT}")

# enter CLI loop

# Data Connection Function


def dataCONN(HOST, s):
    dport = s.recv(4096).decode()
    dport = int(dport)
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as d:
        print(f"[+] Establishing data connection to {HOST}:{dport}")
        d.connect((HOST, dport))
        print("[+] Connected.")
        uploadFile(d)

# Test function to test transfering file to server
# creating the download function should be more or less the same as uploading,
# just reverse the client and server versions of the functions for upload (I assume)


def uploadFile(d):
    BUFFER_SIZE = 4096
    SEPARATOR = "<SEPARATOR>"
    # name of local text file on my computer, this is just for test purposes.
    # for the end product, the user would specify the name of the file to transfer
    fileName = "test1.txt"
    fileSize = os.path.getsize(fileName)
    d.send(f"{fileName}{SEPARATOR}{fileSize}".encode())
    fs = 0
    with open(fileName, "rb") as f:
        while True:
            bytes_read = f.read(BUFFER_SIZE)
            fsTemp = sys.getsizeof(bytes_read)
            fs += ifsTemp
            if not bytes_read:
                break
            d.sendall(bytes_read)
    print("[DEBUG] Sent", fs, "bytes.")


main()
