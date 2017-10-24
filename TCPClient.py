import socket

import sys

HOST = "192.168.0.202"
PORT = 9999

if __name__ == "__main__":
    if len(sys.argv) == 3:
        HOST = sys.argv[1]
        PORT = int(sys.argv[2])
        socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            socket.connect((HOST, PORT))
            while True:
                data = raw_input("message>")
                if data != "":
                    socket.sendall(data + "\n")
                    print "Sent: '{}'".format(data)


        finally:
            socket.close()
    try:
        socket.connect((HOST, PORT))
        while True:
            data = raw_input("message>")
            if data != "":
                socket.sendall(data + "\n")
                print "Sent:     {}".format(data)
                break

        received = socket.recv(1024)
    finally:
        socket.close()

    print "Received: {}".format(received)
