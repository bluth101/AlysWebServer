import socket
from subprocess import check_output

sites = []
sitedirs = []

def loadini():
	try:
		port = 80
	
		ini = open("alys.ini", "r")
		
		for line in ini:
			line = line.split("=")
			
			if( len(line) > 1 ):
				if( line[0] == "port" ):
					print("- Will bind to port: " + line[1].strip())
					port = int(line[1])
				if( line[0] == "host" ):
					print("- New Host: " + line[1].strip())
					sites.append(line[1].strip())
				if( line[0] == "dir" ):
					sitedirs.append(line[1].strip())
					
		print("Alys.ini loaded")
		ini.close()
		return port
					
		
	except:
		print("Can't find alys.ini - Using default values")
		return 80;

def doesFileExist(_filepath):
	try:
		f = open("html" + _filepath, "r")
		f.close()
		return True
	except:
		return False

def readFile(_filepath, _extradir, _vars = ""):
	file_type = _filepath.split(".")[-1]
	
	if( file_type == "php" ):
		try:
			consoleInput = ["php-cgi", "-f", "html" + _extradir + _filepath]
			consoleInput = consoleInput + _vars.split("&")
			
			result = check_output(consoleInput)
			return result
		except:
			print("Error compiling PHP file - " + _extradir + _filepath)
			return False
	
	try:
		# Prepare filepath and try to open the file
		if( _filepath[0] != "/" ):
			_filepath = "/" + _filepath
			
		f = open("html" + _extradir + _filepath, "rb")
		result = f.read()
		f.close()
		return result
	except:
		print("Unable to read file - " + _extradir + _filepath)
		return False

def waitForConnection(_sock):
	conn, addr = _sock.accept()

	request = conn.recv(1024)
	request = request.decode("utf8", "replace").split()
	
	# Make sure it's a valid request
	if( len(request) <= 1 ):
		print("Invalid request received - " + ",".join(request))
		conn.close()
		return
	
	print("Item requested - " + request[1])
	
	# Security and stability stuff
	supported_image_types = ["jpg", "jpeg", "png", "ico"]
	supported_file_types = supported_image_types + ["html", "php", "css", "js", "ogg", "mp3", "wav"]
	
	extra_dir = ""
	cmd_vars = ""
	
	# Check for a host
	if( len(sites) > 0 ):
		if( "Host:" in request ):
			pos = request.index("Host:")
			pos = request[pos+1]
			# Try and remove port numbers, just incase
			pos = pos.split(":")[0]
			
			if( pos in sites ):
				pos = sites.index(pos)
				extra_dir = sitedirs[pos]
				
				# Check formatting
				if( extra_dir[0] != "/" ):
					extra_dir = "/" + extra_dir
			
	# Check if the requested page is valid
	page_req = request[1]
	
	# Check for GET variables
	if( "?" in page_req ):
		getvars = page_req.split("?")
		# Assign vars into respective parts
		page_req = getvars[0]
		cmd_vars = getvars[1]
	
	if( page_req == "/" ):
		if( doesFileExist(extra_dir + "/index.php") ):
			page_req += "index.php"
		else:
			page_req += "index.html"
			
	# Check what type is being requested
	file_type = page_req.split(".")
	file_type = file_type[-1]
	
	# Inspect and handle the request
	page_buffer = ""
	content_type = ""
	status = "200 OK"
	
	if( file_type in ["html", "php"] ):
		content_type = "text/html"

		page_buffer = readFile(page_req, extra_dir, cmd_vars)
		if not page_buffer:
			# Page not found, look for a 404 page
			status = "404 NOT FOUND"
			
			page_buffer = readFile("404.html", extra_dir)
			if not page_buffer:
				page_buffer = readFile("404.html", "")
				if not page_buffer:
					# There's no 404 page.. all hope is lost! D:
					page_buffer = "404 Page not found".encode()
	
	elif( file_type in supported_file_types ):
		content_type = "text/" + file_type
		if file_type in supported_image_types:
			content_type = "image/" + file_type
		
		page_buffer = readFile(page_req, extra_dir)
		if not page_buffer:
			status = "404 NOT FOUND"
			page_buffer = "".encode()
			
	else:
		# Unsupported file type requested!
		status = "415 Unsupported Media Type"
		page_buffer = "".encode()
	
	# Prepare HTTP header and join it with the data
	header_buffer = "HTTP/1.x "+ status +"\r\n"
	header_buffer += "Server: Alys\r\n"
	header_buffer += "Connection: close\r\n"
	header_buffer += "Content-Type: "+content_type+"; charset=UTF-8\r\n"
	header_buffer += "\r\n"
	
	page_buffer = header_buffer.encode() + page_buffer

	# Send to browser
	conn.send(page_buffer)
	conn.close()

def main():
	port = loadini()

	try:
		sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	except:
		print("Unable to create socket")
		return

	try:	
		sock.bind(('', port))
	except:
		print("Unable to bind socket")
		return

	sock.listen(5)
	
	while True:
		waitForConnection(sock)
	
	sock.shutdown(socket.SHUT_RDWR)

main()

