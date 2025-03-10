#!/usr/bin/python3 
import sys
import random
import socket

if len(sys.argv[1:]) != 4:
    print(f"Usage : python3 {sys.argv[0]} <server_port> <qname> <qtype> <timeout>")
    sys.exit(0)

server_port = ("127.0.0.1", int(sys.argv[1]))
qname = sys.argv[2]
qtype = sys.argv[3]
time_out = float(sys.argv[4])

# create socket
client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
client_socket.settimeout(time_out)

# Bind to an ephemeral port
client_socket.bind(('', 0))
local_port = client_socket.getsockname()[1]
print(f"The ephemeral port : {local_port}")

def main():
    while True:
        qid = random.randint(0, 65535)
        # provided qname and qtype in its question section
        Question_section = f"{qid}\n {qname}\n {qtype}"

        try:
            # Send data to the server
            client_socket.sendto(Question_section.encode(), server_port)

            # Receive response from the server
            response, _ = client_socket.recvfrom(4096)
            
            if response:
                response_data = eval(response.decode())  # Convert string representation of dict to dict
                print_response(response_data)
            else:
                print("Not received data")

        except socket.error as e:
            print(f"Socket error: {e}")
            break

        except socket.timeout:
            print("Timeout")
            break

        finally:
            print("Close socket")
            client_socket.close()
            break

def print_response(response_data):
    print(f"QID: {response_data['query']}")
    print("Answer Section:")
    for record in response_data['answer']:
        print(record)
    print("Authority Section:")
    for record in response_data['authority']:
        print(record)
    print("Additional Section:")
    for record in response_data['additional']:
        print(record)
        
if __name__ == "__main__":
    main()
