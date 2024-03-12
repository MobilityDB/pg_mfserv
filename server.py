from http.server import BaseHTTPRequestHandler, HTTPServer
from pymeos.db.psycopg2 import MobilityDB

import json
import time
import matplotlib.pyplot as plt
import pandas as pd
from pymeos import *

pymeos_initialize()

hostName = "localhost"
serverPort = 8080

host = 'localhost'
port = 25432
db = 'postgres'
user = 'postgres'
password = 'postgres'

connection = MobilityDB.connect(host=host, port=port, database=db, user=user, password=password)
cursor = connection.cursor()


class MyServer(BaseHTTPRequestHandler):
    # GET requests router
    def do_GET(self):
       
        if self.path == '/':
            self.do_home()
        elif self.path == '/collections':
            self.do_collections()
        elif self.path.startswith('/collections/'):
            # Extract collection ID from the path
            collection_id = self.path.split('/')[-1]
            self.do_collection_id(collection_id)
            
        
    # POST requests router
    def do_POST(self):
        if self.path == '/collections':
            self.do_post_collection()
    
    def do_DELETE(self):
        if self.path.startswith('/collection/'):
            collection_id = self.path.split('/')[-1]
            self.do_delete_collection(collection_id)



    # Base route of the api
    def do_home(self):
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.wfile.write(bytes("<html><head></head>", "utf-8"))
            self.wfile.write(bytes("<p>Request: This is the base route of the pyApi</p>", "utf-8"))
            self.wfile.write(bytes("<body>", "utf-8"))
            self.wfile.write(bytes("</body></html>", "utf-8"))

    # Get all collections
    def do_collections(self):
        cursor.execute("SELECT table_name FROM information_schema.tables WHERE table_schema='public' AND table_type='BASE TABLE';")
        fetched_collections = cursor.fetchall()
        # Construct the JSON data
        collections = [{'collection': row} for row in fetched_collections]
        json_data = json.dumps(collections)

        # Send the HTTP response
        self.send_response(200)
        self.send_header("Content-type", "application/json")
        self.end_headers()
        self.wfile.write(bytes(json_data, "utf-8"))

    
    def do_post_collection(self):
        content_length = int(self.headers['Content-Length']) # <--- Gets the size of data
        post_data = self.rfile.read(content_length) # <--- Gets the data itself
        print("POST request,\nPath: %s\nHeaders: %s\n\nBody: %s\n" % (self.path, self.headers, post_data.decode('utf-8')))

        data_dict = json.loads(post_data.decode('utf-8'))
        title_lower = data_dict["title"].lower().replace(" ", "_")
        
        cursor.execute("DROP TABLE IF EXISTS public.%s" % title_lower)
        cursor.execute("CREATE TABLE public.%s (id SERIAL PRIMARY KEY, title TEXT, updateFrequency integer, description TEXT, itemType TEXT)" % title_lower)
        #cursor.execute("INSERT INTO public.moving_humans VALUES(DEFAULT, %s, %s, %s, %s)", (data_dict["title"], data_dict["updateFrequency"], data_dict["description"], data_dict["itemType"]))
        connection.commit()

        self.send_response(200)
        self.send_header("Content-type", "application/json")
        self.end_headers()
        self.wfile.write(bytes(post_data.decode('utf-8'), "utf-8"))
    
    def do_collection_id(self, collectionId):
        cursor.execute("SELECT * FROM public.%s;" % collectionId)
        r = cursor.fetchall()

        res = json.dumps(r)
        self.send_response(200)
        self.send_header("Content-type", "application/json")
        self.end_headers()
        self.wfile.write(res.encode('utf-8'))

    def do_delete_collection(self, collectionId):
        cursor.execute("DROP TABBLE IF EXISTS public.%s" %collectionId)
        connection.commit()


    





if __name__ == "__main__":        
    webServer = HTTPServer((hostName, serverPort), MyServer)
    print("Server started http://%s:%s" % (hostName, serverPort))

    try:
        webServer.serve_forever()
    except KeyboardInterrupt:
        pass
    
    connection.commit()
    cursor.close()
    pymeos_finalize()
    webServer.server_close()
    print("Server stopped.")