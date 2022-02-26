# TCP Client-Server Implementation

##Introduction

This project, is an implementation of the TCP protocol using Python, and was an assinment for the course "Internet Protocols", that I took during my 3rd year of undergraduate studies.

The server works as a calculator, and can perform 4 basic arithmetic calculations 
(addition, subtraction, division and multiplication). 

The client sends to the server  two integer numbers, as well as the arithmetic operation that should be used, and the server responds with the solution.

It is important to mention that the numbers should be integers, belonging to the following span: [0, 30.000]

## Client header

The format for the client's header:

![image](https://user-images.githubusercontent.com/26886095/155854397-4e27f97f-69e0-40be-b6c2-4202fca24f98.png)

In more detail:

- Type: The operation selected (2 bytes unsigned integer)
- Len1: Length of the 1st number (1 byte unsigned integer)
- Len2: Length of the 2nd number (1 byte unsigned integer)
- ID: Transaction ID (4 bytes unsigned integer)
- First number: The first number (string)
- Padd1: padding for the first number (0-3 bytes, depending on first number's length, all zeros)
- Second number: The second number (string)

## Server header

The format for the server's header:

![image](https://user-images.githubusercontent.com/26886095/155854705-7659b4d7-f783-4318-903c-cdcb580ad1ca.png)

In more detail:

- Type: The operation selected (2 bytes unsigned integer)
- Response: Error code or success message (2 bytes unsigned integer)
- ID: Transaction ID (4 bytes unsigned integer)
- Answer: The result of the operation (the length of it depends on the operation used)
  - Addition: 2 bytes unsigned integer
  - Subtraction: 2 bytes signed integer
  - Multiplication: 4 bytes unsigned integer
  - Division: 8 bytes signed double
 
## How the program works

1) Both python scripts should be run.
2) The client requests from the user to choose the operation, the two numbers and also a message ID.
3) The message will then be formed and send to the server.
4) The server unpacks the message and performs the calculation.
5) The response message is then formed and send to the client.
6) The client unpacks the response and outputs result to user.

## Example 1 (no errors)

Let's suppose, the user would like to perform the following multiplication: 30.000 * 30.000.

Client side console output:

![image](https://user-images.githubusercontent.com/26886095/155856438-963f3f51-8984-4182-8b73-f998c0ef38e1.png)

Server side console output:

![image](https://user-images.githubusercontent.com/26886095/155856440-d4b9cb63-723b-4437-a4d9-7c130caab8df.png)

As we can clearly see, the resalt is correct, and is accompanied by a success message.

## Example 2 (error detected)

Let's suppose, the user would like to perform the following multiplication: 123 * abc, the second number is not a valid input and therefore we expect an error.

Client side console output:

![image](https://user-images.githubusercontent.com/26886095/155856548-59b4d8b0-4aa7-4e48-b343-e690c12dc783.png)

Server side console output:

![image](https://user-images.githubusercontent.com/26886095/155856553-b246ed35-f2b7-414b-b731-80e80ac171f1.png)

As we can clearly see, the resalt is incorrect, and is accompanied by an error message.
