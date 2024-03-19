from http.server import BaseHTTPRequestHandler, HTTPServer

from pymeos.db.psycopg2 import MobilityDB
from psycopg2 import sql
import json
from pymeos import pymeos_initialize, pymeos_finalize, TGeomPoint
from urllib.parse import urlparse, parse_qs

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
    def do_GET(self):
        if self.path == '/':
            self.do_home()
        elif self.path == '/collections':
            self.do_collections()
        elif self.path.startswith('/collections') and '/items/' in self.path:
            collectionId = self.path.split('/')[2]
            feature_id = self.path.split('/')[-1]
            self.do_get_meta_data(collectionId, feature_id)
        elif '/items' in self.path and self.path.startswith('/collections/'):
            # Extract collection ID from the path
            collection_id = self.path.split('/')[2]
            self.do_get_collection_items(collection_id)
        elif self.path.startswith('/collections/'):
            # Extract collection ID from the path
            collection_id = self.path.split('/')[-1]
            self.do_collection_id(collection_id)

    # POST requests router
    def do_POST(self):
        if self.path == '/collections':
            self.do_post_collection()
        elif '/items' in self.path and self.path.startswith('/collections/'):

            # Extract collection ID from the path
            collection_id = self.path.split('/')[2]
            self.do_post_collection_items(collection_id)

    def do_DELETE(self):
        if self.path.startswith('/collections/') and 'items' not in self.path:
            collection_id = self.path.split('/')[-1]
            self.do_delete_collection(collection_id)
        elif '/items' in self.path and self.path.startswith('/collections/'):
            # Extract collection ID and mFeatureId from the path
            components = self.path.split('/')
            collection_id = components[2]
            mfeature_id = components[4]
            self.do_delete_feature(collection_id, mfeature_id)

    def do_PUT(self):
        if self.path.startswith('/collections/'):
            collection_id = self.path.split('/')[-1]
            self.do_put_collection(collection_id)

    def handle_error(self, code, message):
        # Format error information into a JSON string
        error_response = json.dumps({"code": str(code), "description": message})

        # Send the JSON response
        self.send_response(code)
        self.send_header("Content-type", "application/json")
        self.end_headers()
        self.wfile.write(bytes(error_response, "utf-8"))

    # Base route of the api
    def do_home(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(
            bytes("<html><head></head><p>Request: This is the base route of the pyApi</p>body></body></html>", "utf-8"))

    # Get all collections
    def do_collections(self):
        try:
            cursor.execute(
                "SELECT table_name FROM information_schema.tables WHERE table_schema='public' AND table_type='BASE TABLE';")
            fetched_collections = cursor.fetchall()
            # Construct the JSON data
            collections = [{'collection': row} for row in fetched_collections]
            json_data = json.dumps(collections)

            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            self.wfile.write(bytes(json_data, "utf-8"))
        except Exception as e:
            self.handle_error(500, 'Internal server error')

    def do_post_collection(self):
        try:
            content_length = int(self.headers['Content-Length'])  # <--- Gets the size of data
            post_data = self.rfile.read(content_length)  # <--- Gets the data itself
            print("POST request,\nPath: %s\nHeaders: %s\n\nBody: %s\n" % (
                self.path, self.headers, post_data.decode('utf-8')))

            data_dict = json.loads(post_data.decode('utf-8'))
            title_lower = data_dict["title"].lower().replace(" ", "_")

            cursor.execute(sql.SQL("DROP TABLE IF EXISTS public.{table}").format(table=sql.Identifier(title_lower)))
            cursor.execute(sql.SQL(
                "CREATE TABLE public.{table} (id SERIAL PRIMARY KEY, title TEXT, updateFrequency integer, description TEXT, itemType TEXT)").format(
                table=sql.Identifier(title_lower)))
            # cursor.execute("INSERT INTO public.moving_humans VALUES(DEFAULT, %s, %s, %s, %s)", (data_dict["title"], data_dict["updateFrequency"], data_dict["description"], data_dict["itemType"]))
            connection.commit()

            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            self.wfile.write(bytes(post_data.decode('utf-8'), "utf-8"))
        except Exception as e:
            self.handle_error(500, 'Internal server error')

    def do_collection_id(self, collectionId):
        try:
            cursor.execute(sql.SQL("SELECT * FROM public.{table};").format(table=sql.Identifier(collectionId)))
            r = cursor.fetchall()

            # Convert fetched data to JSON
            res = json.dumps(r)

            # Send response
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            self.wfile.write(res.encode('utf-8'))
        except Exception as e:
            # Handle any exceptions
            self.handle_error(404 if 'does not exist' in str(e) else 500,
                              'no collection was found' if 'does not exist' in str(e) else 'Server internal error')

    def do_delete_collection(self, collectionId):
        try:
            cursor.execute("DROP TABLE IF EXISTS public.%s" % collectionId)
            connection.commit()
            self.send_response(204)
            self.send_header("Content-type", "application/json")
            self.end_headers()
        except Exception as e:
            self.handle_error(500, str(e))

    def do_put_collection(self, collectionId):
        content_length = int(self.headers['Content-Length'])
        put_data = self.rfile.read(content_length)

        try:
            data_dict = json.loads(put_data)
            collectionId = collectionId.replace("'", "")

            cursor.execute(sql.SQL("UPDATE public.{table} SET title=%s, description=%s, itemtype=%s").format(
                table=sql.Identifier(collectionId)),
                (data_dict.get('title'), data_dict.get('description'), data_dict.get('itemType')))
            connection.commit()
            # Rows were updated successfully
            self.send_response(204)
            self.send_header("Content-type", "application/json")
            self.end_headers()
        except Exception as e:
            self.handle_error(404 if 'does not exist' in str(e) else 500,
                              'no collection was found' if 'does not exist' in str(e) else 'Server internal error')

    def do_get_collection_items(self, collectionId):
        parsed_url = urlparse(self.path)
        query_params = parse_qs(parsed_url.query)
        limit = 10 if query_params.get('limit') is None else query_params.get('limit')[0]
        x1, y1, x2, y2 = query_params.get('x1')[0], query_params.get('y1')[0], query_params.get('x2')[0], \
            query_params.get('y2')[0]
        subTrajectory = query_params.get('subTrajectory')[0]
        dateTime = query_params.get('dateTime')

        dateTime1 = dateTime[0].split(',')[0]
        dateTime2 = dateTime[0].split(',')[1]

        print("x1:", x1)
        print("y1:", y1)
        print("x2:", x2)
        print("y2:", y2)
        print("DateTime: ", dateTime1, "  ", dateTime2)
        print("limit: ", limit)
        print("subTraj: ", subTrajectory)

        query = (
            "SELECT mmsi, asMFJSON(trip) FROM public.{} WHERE atstbox(trip, stbox 'SRID=25832;STBOX XT((({},{}), ({},{})),[{},{}])') IS NOT NULL LIMIT {};").format(
            collectionId, x1, y1, x2, y2, dateTime1, dateTime2, limit)
        query_count = (
            "SELECT count(trip) as count FROM public.{} WHERE atstbox(trip, stbox 'SRID=25832;STBOX XT((({},{}), ({},{})),[{},{}])') IS NOT NULL  ;").format(
            collectionId, x1, y1, x2, y2, dateTime1, dateTime2)
        cursor.execute(query)
        row_count = cursor.rowcount
        data = cursor.fetchall()

        # Execute the query to get the count of rows
        cursor.execute(query_count)
        # Fetch the result of the count query
        count_result = cursor.fetchone()
        # Access the count value from the result
        total_row_count = count_result[0]

        crs = json.loads(data[0][1])["crs"]

        features = []
        for row in data:
            feature = json.loads(row[1])
            feature["id"] = row[0]
            feature.pop("datetimes", None)
            features.append(feature)

        # Convert the GeoJSON data to a JSON string
        geojson_data = {
            "type": "FeatureCollection",
            "features": features,
            "crs": crs,
            "timeStamp": "To be defined",
            "numberMatched": total_row_count,
            "numberReturned": row_count
        }

        # Convert the GeoJSON data to a JSON string
        geojson_string = json.dumps(geojson_data)

        # Define the coordinates of the polygon's vertices
        self.send_response(200)
        self.send_header("Content-type", "application/json")
        self.end_headers()
        self.wfile.write(geojson_string.encode('utf-8'))

    def do_post_collection_items(self, collectionId):
        try:
            content_length = int(self.headers['Content-Length'])  # <--- Gets the size of data
            post_data = self.rfile.read(content_length)
            print("POST request,\nPath: %s\nHeaders: %s\n" % (self.path, self.headers))

            data_dict = json.loads(post_data.decode('utf-8'))
            mmsi = data_dict.get("id")
            tempGeo = data_dict.get("temporalGeometry")

            if tempGeo is None:
                raise Exception("DataError")

            tGeomPoint = TGeomPoint.from_mfjson(json.dumps(tempGeo))
            string_query = f"INSERT INTO public.{collectionId} VALUES({mmsi}, '{tGeomPoint}');"

            cursor.execute(string_query)
            connection.commit()

            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.end_headers()

        except Exception as e:
            self.handle_error(400 if "DataError" in str(e) else 404 if "does not exist" in str(e) else 500, str(e))

    def do_get_meta_data(self, collecitonId, featureId):
        print("GET request,\nPath: %s\nHeaders: %s\n" % (self.path, self.headers))
        try:
            sqlString = f"SELECT asMFJSON(trip) FROM public.{collecitonId} WHERE mmsi={featureId};"
            cursor.execute(sqlString)

            rs = cursor.fetchall()
            if len(rs) == 0:
                raise Exception("feature does not exist")
            data = json.loads(rs[0][0])

            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            self.wfile.write(bytes(json.dumps(data), 'utf-8'))
        except Exception as e:
            self.handle_error(404 if "does not exist" in str(e) else 500,
                              "Collection or Feature does not exist" if "does not exist" in str(
                                  e) else str(e))

    def do_delete_feature(self, collection_id, mfeature_id):
        try:
            print("GET request,\nPath: %s\nHeaders: %s\n" % (self.path, self.headers))
            sqlString = f"DELETE FROM public.{collection_id} WHERE mmsi={mfeature_id}"
            cursor.execute(sqlString)
            connection.commit()

            self.send_response(204)
            self.send_header("Content-type", "application/json")
            self.end_headers()
        except Exception as e:
            self.handle_error(404 if "does not exist" in str(e) else 500,
                              "Collection or Item does not exist" if "does not exist" in str(
                                  e) else "Server Internal Error")


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
