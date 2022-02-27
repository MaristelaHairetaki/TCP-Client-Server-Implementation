# Maristela Hairetaki E18174

# Import the socket library
from struct import *
import socket


# Host IP to listen to
serverIP = '127.0.0.1'
# Specify the port to listen to
serverPort = 8000

# Flag to close the socket. Normally we don't close the socket. We keep on listening.
# This flag is used to simply terminate the program and close the socket as we don't need it after
# the message exchange
close = False

# Create the server socket
# socket.AF_INET == IPv4
# socket.SOCK_STREAM == TCP
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as serverSocket:

    # Bind the socket
    serverSocket.bind((serverIP, serverPort))
    print("\nServer is ready to receive at port: ", str(serverPort))

    # Listen for connections
    # If we don't specify in the listen a number e.g. serverSocket.listen(5), it goes to the system default
    serverSocket.listen()

    while not close:

        # Listen and wait for connection
        # Once a connection is made it returns two values, the conn will have the connection socket and the addr
        # will have the address
        conn, addr = serverSocket.accept()

        print("\n--------------------------------------")

        # Print info: Connected address, Server IP & Port, Client IP & Port
        info = conn.getsockname()
        print("\nServer IP address: ", info[0])
        print("Server Socket port: ", info[1])
        info = conn.getpeername()
        print("Client IP address: ", info[0])
        print("Client Socket port: ", info[1])

        # Receive the first 8 bytes
        msg = conn.recv(8)

        # Unpack the message
        msg_type, msg_num1_len, msg_num2_len, msg_id = unpack('HBBI', msg)

        # Calculate the padding size for the 2 numbers
        num1_pad_size = (4 - msg_num1_len % 4) % 4
        num2_pad_size = (4 - msg_num2_len % 4) % 4

        # Initial message response code is 0 - everything is ok
        msg_resp_code = 0

        # num1_int & num2_int: Two flag variables to check if the numbers are integers
        # TRUE: the number is an integer
        # FALSE: the number is not an integer
        num1_int = True
        num2_int = True

        # Receive the first number
        msg = conn.recv(msg_num1_len + num1_pad_size)

        # Calculate the unpackString
        if num1_pad_size == 0:
            unpackString = str(msg_num1_len)+'s'
        else:
            unpackString = str(msg_num1_len)+'s'+str(num1_pad_size)+'x'

        # Unpack message
        msg_num1 = unpack(unpackString, msg)
        # Decode message
        msg_num1 = msg_num1[0].decode('utf-8')

        # Make sure we received a number
        if not msg_num1.isdigit() or msg_num1.__contains__("/"):
            msg_resp_code = 7   # num1 was not an int
            msg_num1 = 0
            num1_int = False

        # Convert string to int
        msg_num1 = int(msg_num1)

        # Receive second number
        msg = conn.recv(msg_num2_len + num2_pad_size)

        if num2_pad_size == 0:
            unpackString = str(msg_num2_len) + 's'
        else:
            unpackString = str(msg_num2_len) + 's' + str(num2_pad_size) + 'x'

        # Unpack message
        msg_num2 = unpack(unpackString, msg)
        # Decode message
        msg_num2 = msg_num2[0].decode('utf-8')

        # Make sure we received a number
        if not msg_num2.isdigit() or msg_num2.__contains__("/"):
            msg_resp_code = 8   # num2 was not an int
            msg_num2 = 0
            num2_int = False

        # Convert string to int
        msg_num2 = int(msg_num2)

        if not num1_int and not num2_int:
            msg_resp_code = 9   # Both numbers not integers

        # Create the data for the header

        #   0             16             31
        #   +--------------+--------------+
        #   |   Type (2)   | Response (2) |
        #   +--------------+--------------+
        #   |           ID (4)            |
        #   +--------------+--------------+
        #   |         Answer  (?)         |
        #   +--------------+--------------+

        print("\n--------------------------------------")

        print("\nThe message ID is: ", msg_id)

        if msg_type == 0:
            print("\nWe will perform: addition")
        elif msg_type == 1:
            print("\nWe will perform: subtraction")
        elif msg_type == 2:
            print("\nWe will perform: division")
        else:
            print("\nWe will perform: multiplication")

        print("\nThe length of the first number is: ", msg_num1_len)
        if num1_int:
            print("The first number is: ", msg_num1)
        else:
            print("The first number is not an integer...")
        print("\nThe length of the second number is: ", msg_num2_len)
        if num2_int:
            print("The second number is: ", msg_num2)
        else:
            print("The second number is not an integer...")

        print("\n--------------------------------------")

        # num1_ok & num2_ok: Two flag variables to check if the numbers are in bounds
        # TRUE: the number is within bounds
        # FALSE: the number is out of bounds
        num1_ok = True
        num2_ok = True

        if msg_num1 > 30000 or msg_num1 < 0:
            num1_ok = False

        if msg_num2 > 30000 or msg_num2 < 0:
            num2_ok = False

        if not num1_ok and not num2_ok:
            msg_resp_code = 5       # Both numbers are out of bounds
        elif not num1_ok:
            if msg_num1 > 30000:
                msg_resp_code = 1   # Num1 is above 30000
            else:
                msg_resp_code = 2   # Num1 is below 0
        elif not num2_ok:
            if msg_num2 > 30000:
                msg_resp_code = 3   # Num2 is above 30000
            else:
                msg_resp_code = 4   # Num2 is below 0

        if msg_type == 2 and msg_num2 == 0 and num2_int:
            msg_resp_code = 6       # We used 0 as divisor

        # The initial package string
        pack_string = "HHI"

        # We initiate the msg_resp_ans as 0, if one or both numbers is out of bounds, it will remain 0
        msg_resp_ans = 0

        # Perform addition
        if msg_type == 0:
            # If both numbers are within bounds, we perform the given operation
            if num1_ok and num2_ok:
                msg_resp_ans = msg_num1 + msg_num2
            # Addition: worst case scenario -> 30.000 + 30.000 = 60.000 -> unsigned short = H
            pack_string += "H"
        # Perform subtraction
        elif msg_type == 1:
            if num1_ok and num2_ok:
                msg_resp_ans = msg_num1 - msg_num2
            # Subtraction: worst case scenario -> 30.000 - 0 = 30.000 or 0 - 30.000 = -30.000 -> short = h
            pack_string += "h"
        # Perform division
        elif msg_type == 2:
            if msg_num2 != 0 and num1_ok and num2_ok:
                msg_resp_ans = msg_num1 / msg_num2
            # Division: worst case scenario -> 1 / 30.000 = 3.3333333333333335e-05 -> double = d
            pack_string += "d"
        # Perform multiplication
        else:
            if num1_ok and num2_ok:
                msg_resp_ans = msg_num1 * msg_num2
            # Multiplication: worst case scenario -> 30.000 * 30.000 = 900.000.000 -> unsigned int = I
            pack_string += "I"

        # Pack the message
        message = pack(pack_string, msg_type, msg_resp_code, msg_id, msg_resp_ans)

        # Print the result to console
        print("\nResult: ", msg_resp_ans)

        # Send the message through the same connection
        err = conn.sendall(message)

        # Print any errors if any exist
        print("\nErrors: ", err)

        print("\n--------------------------------------")

        # Signal (with the flag) to close the socket
        close = True

        # And closing
        conn.close()
        serverSocket.close()
