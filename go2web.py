import socket
from bs4 import BeautifulSoup
import sys
from urllib.parse import unquote


HELP_MESSAGE = """Usage: python3 go2web.py OPTION [ARGUMENT]
Makes HTTP requests and Google searches.

Options:
  -u <URL>             Makes an HTTP request to URL and prints the response
  -s <search-term>     Searches the term using Google search engine and prints top 10 results
  -h                   Shows this help menu"""


def search(term):
    target_port = 80  
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  
    client.settimeout(2)
    
    # connect the client 
    client.connect(("www.google.com",target_port))  
    
    # send some data 
    request = "GET /search?q=%s HTTP/1.1\r\nHost: www.google.com\r\n\r\n" % term
    client.send(request.encode())  
    
    # receive some data 
    response = b""
    try:
        while True:
            response = response + client.recv(4096)
    except socket.timeout as e:
        pass
    http_response = repr(response)
    http_response_len = len(http_response)

    # extract the html
    start = response.find(b'<!doctype html>')
    end = response.find(b'</html>') + 7
    html_response = response[start:end]
    soup = BeautifulSoup(html_response, 'html.parser')
    # get the result elements
    tags = soup.find_all(class_="egMi0")

    print("Here are the first page results:")
    for i, elem in enumerate(tags):
        print("%d. " % int(i+1), end='')
        whole_url = str(elem.a['href'])
        start_url = whole_url.find("http")
        end_url = whole_url.find("&sa=")
        url = whole_url[start_url:end_url]
        print(elem.a.h3.div.string)
        url = unquote(url)
        print("Link:", url, end='\n\n')

def access(url):
    target_port = 80
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  
    client.settimeout(4)
    
    # find the host part an the pth part
    http_len = 7
    http = url.find("http://")
    if http == -1:
    	# it is https
        http_len = 8
        
    path_start = url[http_len:].find("/")
    #print("path_start", path_start)
    path = str()
    if path_start == -1:
    	# there is no path
    	path_start = len(url) + 1
    	path = "/"
    else:
        path_start += http_len
        path = url[path_start:]
    host = url[http_len:path_start]
    
    print("Making request to", host, "at", path, "\n")
    
    # connect the client
    client.connect((host,target_port))  
    
    # send some data  
    request = "GET " + path + " HTTP/1.1\r\nHost: " + host + "\r\n\r\n"
    client.send(request.encode())  
    
    # receive some data 
    response = b""
    try:
        while True:
            response = response + client.recv(4096)
    except socket.timeout as e:
        pass
    http_response = repr(response)
    http_response_len = len(http_response)

    # extract the html       
    start = response.find(b'<html')
    end = response.find(b'</html>') + 7
    html_response = response[start:end]
    soup = BeautifulSoup(html_response, 'html.parser')
    #remove styles
    for el in soup.find_all("style"):
        el.replaceWith("")
    # remove head
    for el in soup.find_all("head"):
        el.replaceWith("")
    # remove scripts
    for el in soup.find_all("script"):
        el.replaceWith("")

    for child in soup.recursiveChildGenerator():
        name = getattr(child, "name", None)
        if name is not None:
            if name == "a":
                link = child['href']
                if link[0] == '/':
                    link = "https://" + host + link
                print(link)
        elif not child.isspace(): # leaf node, don't print spaces
            print(child)   
    
        
if __name__ == "__main__":
    n = len(sys.argv)

    if n == 2 and sys.argv[1] == '-h':
        print(HELP_MESSAGE)

    if n == 3 and sys.argv[1] == '-s':
        term = sys.argv[2]
        search(term)
        
    if n == 3 and sys.argv[1] == '-u':
        url = sys.argv[2]
        access(url)
        
