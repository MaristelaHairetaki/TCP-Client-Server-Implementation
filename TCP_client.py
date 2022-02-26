# -*- coding: utf-8 -*-
"""
Created on Mon Mar 22 12:48:22 2021

@author: ehalep
"""

# Maristela Hairetaki E18174

from struct import *
import socket 


# ---------------- Connection information ----------------

# Specify host IP
serverIP = '127.0.0.1'
# Specify the port
serverPort = 8000

# Create the client socket
# socket.AF_INET == IPv4
# socket.SOCK_STREAM == TCP
clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Connect. The server socket should be listening.
clientSocket.connect((serverIP, serverPort))


# ---------------- Packet header ----------------

#   0                    16                    31
#   +---------------------+---------------------+
#   |       Type (2)      | len1 (1) | len2 (1) |
#   +---------------------+---------------------+
#   |                  ID (4)                   |
#   +---------------------+---------------------+
#   |          First Number          |  Padd1   |
#   +---------------------+---------------------+
#   |          Second Number         |  Padd2   |
#   +---------------------+---------------------+


# ---------------- Collect the data for the header ----------------

# msg_type: a variable to specify the operation to be used
# 0 = addition
# 1 = subtraction
# 2 = division
# 3 = multiplication

print("\nEnter the type number: \n(0: addition, 1: subtraction, 2: division, 3: multiplication)")
msg_type = input()

# Check that the msg_type is one of the above options
while not msg_type.isdigit() or msg_type.__contains__("/") or (int(msg_type) > 3) or (int(msg_type) < 0):
    print("Please try again...")
    print("Enter the type number: \n(0: addition, 1: subtraction, 2: division, 3: multiplication)")
    msg_type = input()

msg_type = int(msg_type)

# Collect both numbers as strings and convert them to bytes
print("Enter the first number: ")
msg_num1 = input()
nb_num1 = bytes(msg_num1, 'utf-8')

print("Enter the second number: ")
msg_num2 = input()
nb_num2 = bytes(msg_num2, 'utf-8')

# Collect message ID and make sure it is a positive number
print("Enter message ID: ")
msg_id = input()

while not msg_id.isdigit() or msg_id.__contains__("/") or int(msg_id) < 0 or int(msg_id) > 4294967295:
    print("Please try again, ID out of bounds...")
    print("Enter a message ID: ")
    msg_id = input()

msg_id = int(msg_id)


# ---------------- Prepare the data for the header ----------------

# Calculate the padding sizes for both numbers
num1_pad_size = (4 - len(msg_num1) % 4) % 4
num2_pad_size = (4 - len(msg_num2) % 4) % 4

# Create a packing string
if num1_pad_size == 0 and num2_pad_size == 0:
    packString = 'HBBI' + str(len(msg_num1)) + 's' + str(len(msg_num2)) + 's'
elif num1_pad_size == 0:
    packString = 'HBBI' + str(len(msg_num1)) + 's' + str(num1_pad_size) + 'x' + str(len(msg_num2)) + 's'
elif num2_pad_size == 0:
    packString = 'HBBI' + str(len(msg_num1)) + 's' + str(len(msg_num2)) + 's' + str(num2_pad_size) + 'x'
else:
    packString = 'HBBI' + str(len(msg_num1)) + 's' + str(num1_pad_size) + 'x' + str(len(msg_num2)) + 's' \
                 + str(num2_pad_size) + 'x'

# Calculate the lengths for both numbers
msg_num1_len = len(msg_num1)
msg_num2_len = len(msg_num2)


# ---------------- Pack & send the message ----------------

# Pack the message
message = pack(packString, msg_type, msg_num1_len, msg_num2_len, msg_id, nb_num1, nb_num2)

# Send the message through the socket
clientSocket.sendall(message)


# ---------------- Get the response ----------------

# Collect the first 8 bytes of the message
resp = clientSocket.recv(8)

# We know that the first 8 bytes contain the type, the response code and the id of the message
msg_resp_type, msg_resp_code, msg_resp_id = unpack('HHI', resp)


# Make sure we got the correct response (compare the ids)
if msg_id == msg_resp_id:
    print("\n--------------------------------------")
    print("This is my response")
    print("--------------------------------------")

    # msg_resp_code can take values 0-6. When it has a value from 1-6 an error has occurred therefore we don't
    # need to perform the things bellow
    if not msg_resp_code:

        # Addition: worst case scenario -> 30.000 + 30.000 = 60.000 -> unsigned short = H
        if msg_resp_type == 0:
            unpack_string = "H"
            unpack_bytes = 2
        # Subtraction: worst case scenarios -> 30.000 - 0 = 30.000 or 0 - 30.000 = -30.000 -> short = h
        elif msg_resp_type == 1:
            unpack_string = "h"
            unpack_bytes = 2
        # Division: worst case scenario -> 1 / 30.000 = 3.3333333333333335e-05 -> double = d
        elif msg_resp_type == 2:
            unpack_string = "d"
            unpack_bytes = 8
        # Multiplication: worst case scenario -> 30.000 * 30.000 = 900.000.000 -> unsigned int = I
        else:
            unpack_string = "I"
            unpack_bytes = 4

        # Collect the rest of the message (Result)
        resp = clientSocket.recv(unpack_bytes)

        # Unpack the message
        msg_resp_ans = unpack(unpack_string, resp)

        # msg_resp_ans is a tuple, we only want the first element
        print("\nResult: ", msg_resp_ans[0])
    else:
        print("\nCould not provide an answer...")

    # Let the user know the operation that was used
    if msg_resp_type == 0:
        print("We performed: addition")
    elif msg_resp_type == 1:
        print("We performed: subtraction")
    elif msg_resp_type == 2:
        print("We performed: division")
    else:
        print("We performed: multiplication")

    # Let the user know whether or not an error occurred
    if msg_resp_code == 0:
        print("\nEverything went well!")
    elif msg_resp_code == 1:
        print("\nError:\nThe first number was more than 30000.")
    elif msg_resp_code == 2:
        print("\nError:\nThe first number was less than 0.")
    elif msg_resp_code == 3:
        print("\nError:\nThe second number was more than 30000.")
    elif msg_resp_code == 4:
        print("\nError:\nThe second number was less than 0.")
    elif msg_resp_code == 5:
        print("\nError:\nBoth numbers are out of bounds")
    elif msg_resp_code == 6:
        print("\nError:\nDivision by zero is not allowed!")
    elif msg_resp_code == 7:
        print("\nError:\nThe first number was not an integer!")
    elif msg_resp_code == 8:
        print("\nError:\nThe second number was not an integer!")
    elif msg_resp_code == 9:
        print("\nError:\nBoth numbers were not integers!")
else:
    print("\nThis is not my response, something went wrong...")

print("\n--------------------------------------")

# Close the socket
clientSocket.close()
