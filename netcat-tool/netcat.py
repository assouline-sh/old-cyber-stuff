import argparse
import socket
import shlex
import subprocess
import sys
import textwrap
import threading

# Run given command
def execute(cmd):
	if cmd:
    	try:
        	cmd.strip()
        	output = subprocess.check_output(shlex.split(cmd), stderr=subprocess.STDOUT, stdin=subprocess.PIPE)
        	return output.decode()
    	except subprocess.CalledProcessError as e:
        	return str(e.output)

# Netcat object
class Netcat:
	# Initialize Netcat object and create socket
	def __init__(self, args, buffer=None):
    	self.args = args
    	self.buffer = buffer
    	self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

	# Listen or send
	def run(self):
    	if self.args.listen:
        	self.listen()
    	else:
        	self.send()

	# Handle executing file uploads, commands, or an interactive shell
	def handle(self, client_socket):
    	# Execute command and send output back
    	if self.args.execute:
        	ouput = execute(self.args.execute)
        	client_socket.send(output.encode())

    	# Upload a file by receiving data and writing it to a new file
    	elif self.args.upload:
        	with open(self.args.upload, 'wb') as f:
            	while True:
                	data = client_socket.recv(4096)
                	if not data:
                    	break
                	f.write(data)

        	message = f'Saved file {self.args.upload}'
        	client_socket.send(message.encode())

    	# Launch an interactive shell
    	elif self.args.command:
        	cmd_buffer = b''
        	while True:
            	try:
                	# Prompt the sender and receive data
                	client_socket.send(b'\nMyNetcat: > ')
                	while '\n' not in cmd_buffer.decode():
                    	cmd_buffer += client_socket.recv(64)

                	# Execute the command and send output back
                	response = execute(cmd_buffer.decode())
                	if response:
                    	client_socket.send(response.encode())
                	cmd_buffer = b''
           	 
            	except Exception as e:
                	print(f"Closing connection. Error {e}")
                	self.socket.close()
                	sys.exit()

	# Run as a listener
	def listen(self):
    	# Connect to the target and port, and start listening
    	self.socket.bind((self.args.target, self.args.port))
    	self.socket.listen(5)

    	while True:
        	# Pass connected socket to handle method
        	client_socket, _ = self.socket.accept()
        	send_thread = threading.Thread(target=self.handle, args=(client_socket,))
        	send_thread.start()


	# Run as a sender
	def send(self):
    	# Connect to the target and port, and send the buffer if present
    	self.socket.connect((self.args.target, self.args.port))
    	if self.buffer:
        	self.socket.send(self.buffer)

    	try:
        	while True:
            	# Receive data from the target until there is no more
            	data = self.socket.recv(4096)
            	if not data:
                	break
       	 
            	# Print the response data
            	response = data.decode()
            	print(response)
       	 
            	# Get and send interactive input
            	buffer = input('> ')
            	buffer += '\n'
            	self.socket.send(buffer.encode())

    	except Exception as e:
        	self.socket.close()
        	sys.exit()

if __name__ == '__main__':
	parser = argparse.ArgumentParser()
	parser.add_argument('-c', '--command', action='store_true', help='interactive shell')
	parser.add_argument('-e', '--execute', type=str, help='execute command')
	parser.add_argument('-l', '--listen', action='store_true', help='listen')
	parser.add_argument('-p', '--port', type=int, default=5555, help='port')
	parser.add_argument('-t', '--target', help='target IP')
	parser.add_argument('-u', '--upload', type=str, help='file name to upload')
	args = parser.parse_args()
    
	# If listener, create Netcat object with empty buffer string, else set buffer to stdin input
	if args.listen:
    	buffer = ''
	else:
    	buffer = sys.stdin.read()

	# Create and run netcat object
	nc = Netcat(args, buffer.encode())
	nc.run()
	self.socket.close()
	sys.exit()


