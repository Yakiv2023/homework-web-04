import json
import os
import urllib.parse
from datetime import datetime
from http.server import BaseHTTPRequestHandler, HTTPServer


class MyHttpRequestHandler(BaseHTTPRequestHandler):
    def send_html_file(self, filename, status=200):
        self.send_response(status)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        with open(filename, 'rb') as fd:
            self.wfile.write(fd.read())

    def send_static_file(self, filename):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        with open(os.path.join('static', filename), 'rb') as fd:
            self.wfile.write(fd.read())

    def do_GET(self):
        pr_url = urllib.parse.urlparse(self.path)
        if pr_url.path == '/':
            self.send_html_file('templates/index.html')
        elif pr_url.path == '/message.html':
            self.send_html_file('templates/message.html')
        elif pr_url.path.startswith('/static/'):
            self.send_static_file(pr_url.path[8:])  # Removing '/static/' prefix
        else:
            self.send_html_file('templates/error.html', 404)

    def do_POST(self):
        if self.path == '/message':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            post_data = post_data.decode('utf-8')
            parsed_data = urllib.parse.parse_qs(post_data)
            
            username = parsed_data.get('username', [''])[0]
            message = parsed_data.get('message', [''])[0]

            if username and message:
                timestamp = str(datetime.now())
                new_entry = {
                    timestamp: {
                        "username": username,
                        "message": message
                    }
                }
                
                # Save the new entry to the data.json file
                with open('storage/data.json', 'r+') as file:
                    data = json.load(file)
                    data.update(new_entry)
                    file.seek(0)
                    json.dump(data, file, indent=4, ensure_ascii=False)
                    file.truncate()
                
                self.send_response(302)
                self.send_header('Location', '/message.html')
                self.end_headers()
            else:
                self.send_response(400)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                self.wfile.write("Bad Request: Username and message are required".encode('utf-8'))

        else:
            self.send_response(404)
            self.send_header('Content-type', 'text/html')
            self.end_headers()

def main():
    PORT = 3000

    # Create an HTTP server with our custom handler
    with HTTPServer(("", PORT), MyHttpRequestHandler) as httpd:
        print("HTTP server listening on ('', 3000)")
        httpd.serve_forever()

if __name__ == '__main__':
    main()