# PG_MFSERVER

This server is a Python API that allows GET, POST, PUT, and DELETE operations on MobilityDB. The server utilizes the [PyMEOS](https://github.com/MobilityDB/PyMEOS) library.

This implementation follows the OGC API - Moving Features Standard

## Introduction

This Python API server provides endpoints for interacting with MobilityDB, a temporal extension for PostgreSQL. It allows users to perform CRUD operations (Create, Read, Update, Delete) on MobilityDB data using HTTP methods.

## Features

- Supports GET, POST, PUT, and DELETE operations.
- Integrates the PyMEOS library for seamless interaction with MobilityDB.
- Provides endpoints for managing data stored in MobilityDB.

## Prerequisites

- A recent version of Pyhton
- A MobilityDB running locally or on a server

## Installation

To install and run the server, follow these steps:

1. Download the server.py and utils.py file in the same folder.
2. Dowload the rest-clients and change the queries to match your MOBILITYDB collections.
3. Change the connection parameters in the server.py file.
4. Install [PyMEOS](https://github.com/MobilityDB/PyMEOS)
5. Run the server :
    ```bash
    python3 server.py
6. Enjoy !

## Usage

Send http requests to the api using any http service.

As an example, your can use the ais.sql that will create ships and ship2 tables containing ships data.
To do that you will have to change the path in the script to the path of your .csv file.
 
Here is a link to download ships datasets: [Denmark Ships DataSets](https://web.ais.dk/aisdata/)

## Developement

This project is in progress.

## License



