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

1. Download the server.py and utils.py file in the same folder
2. Dowload the rest-clients
3. Install [PyMEOS](https://github.com/MobilityDB/PyMEOS)
4. Run the server :
    ```bash
    python3 server.py
5. Enjoy !
## Usage

Send http requests to the api using any http service.

## Developement

This project is in progress.

## License



