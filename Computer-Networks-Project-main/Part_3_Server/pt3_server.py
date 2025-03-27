import socket
import threading
import os


PORTNUM = 6060

SERVER_IP = '127.0.0.1'
ADDRESS = (SERVER_IP, PORTNUM)
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # OUR SOCKET
server.bind(ADDRESS)  # we connected our socket to ADDRESS , so anything that hit this address will hit our socket



def handle_requests(request, client_addr):


    content_types = {

        ".html": "text/html",
        ".css": "text/css",
        ".png": "image/png",
        ".jpg": "image/jpeg"

    }


    redirects = {

        "/so": "https://stackoverflow.com/",
        "/itc": "https://itc.birzeit.edu/"

    }

    path_mapping = {

        "/": "main_en.html",
        "/index.html": "main_en.html",
        "/en": "main_en.html",
        "/main_en.html": "main_en.html",
        "/ar": "main_ar.html"

    }




    if request in redirects:
        redirect_to = redirects[request]
        response = (f"HTTP/1.1 307 Temporary Redirect\r\n"
                    f"Location: {redirect_to}\r\n\r\n")

        return response.encode()


    if request in path_mapping:
        file_path = path_mapping[request]
    else:
        file_path = request[1:]

    if os.path.isfile(file_path):
        _, fextension = os.path.splitext(file_path)  # to store the file extension
        ctype = content_types.get(fextension, "application//octet-stream")  # to store the content type
        with open(file_path, "rb") as file:
            file_content = file.read()
        return f"HTTP/1.1 200 OK\r\nContent-Type: {ctype}\r\n\r\n".encode() + file_content

    return f"HTTP/1.1 404 Not Found\r\nContent-Type: text/html\r\n\r\n".encode() + error_not_found(client_addr)


def get_image_name(request):
    headers, _, body = request.partition("\r\n\r\n")
    image_name = {kv.split('=')[0]: kv.split('=')[1] for kv in body.split('&')}
    image_name = str(image_name)
    image_name = image_name.split(':')[1]
    image_name= image_name.replace("'","")
    image_name = image_name.replace("{", "")
    image_name = image_name.replace("}", "")
    image_name = image_name.replace(" ", "")
    return image_name





def get_image(name,client_addr):



     types = {


        ".png": "image/png",
        ".jpg": "image/jpeg"

     }


     path = os.path.join("images",name)



     if os.path.exists(path):
        _, extension = os.path.splitext(path)  # to store the file extension
        ctype = types.get(extension, "application//octet-stream")  # to store the content type
        with open(path,'rb') as image_location:
            image = image_location.read()

        return f"HTTP/1.1 200 OK\r\nContent-Type: {ctype}\r\n\r\n".encode() + image


     return f"HTTP/1.1 404 Not Found\r\nContent-Type: text/html\r\n\r\n".encode() + error_not_found(client_addr)








def handle_client_request(client_socket):

    request = client_socket.recv(2048).decode('utf-8')
    print(f"The received request:\n{request}\n\n")
    # print('\n\n')
    line = request.split('\r\n')[0]
    # print(line)  # the first line
    line1 = line.split(" ")[0]
    if line1 == "GET":
        line = request.split('\r\n')[0]
        # print(line)  # the first line
        line1 = line.split(" ")[0]
        # print(line1)  # the method
        _, path, _ = line.split(' ')
        # print(path)  # object name
        response = handle_requests(path, client_socket.getpeername())
        client_socket.sendall(response)
        print("The response message: \n")
        #  print()
        line2 = response.split(b'\r\n')[0].decode('utf-8')
        print(line2)
        print('\n\n')
        client_socket.close()

    if line1 == "POST":
        # path = path.replace("/","")
        path = get_image_name(request)

        response = get_image(path,client_socket.getpeername())

        client_socket.sendall(response)
        print("The response message: \n")
        #  print()
        line2 = response.split(b'\r\n')[0].decode('utf-8')
        print(line2)
        print('\n\n')
        client_socket.close()



def error_not_found(client_addr):

    with open("Error.html", "r") as file:
        error_file_content = file.read()
    error_file_content = error_file_content.replace("[Client IP and Port]", f"{client_addr[0]}:{client_addr[1]}")

    return error_file_content.encode()


def start():
    server.listen()
    print(f'The server is now listening on port {PORTNUM}...')
    print()
    while True:
        client_socket, client_addr = server.accept()
        thread = threading.Thread(target=handle_client_request, args=(client_socket, ))
        thread.start()

if __name__== "__main__":
    print("server is starting..")
start()
