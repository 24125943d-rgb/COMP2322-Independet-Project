# Comp 2322 Project: Multi-thread Web Server

## Student Information
* **Name:** [Your Name Here]
* **Student ID:** [Your Student ID Here]

## Environment Setup
* **Language:** Python 3.x
* **Dependencies:** None (Only built-in libraries like socket, threading, os, time are used).

## Project Structure
* `server_final.py`: The main source code for the multi-threaded web server.
* `www/`: The document root directory containing test files (e.g., HTML, images).
* `server_log.txt`: The log file recording all client request history and statuses.

## How to Run the Server
1. Open a terminal or command prompt.
2. Navigate to the directory containing `server_final.py`.
3. Ensure the `www` folder exists in the same directory and contains some test files.
4. Execute the following command to start the server: 
   `python server_final.py`
5. The server will start listening on `127.0.0.1` at port `8080`.

## How to Test
Open a web browser and access the following URLs:
* **200 OK (GET file):** http://127.0.0.1:8080/index.html
* **404 Not Found:** http://127.0.0.1:8080/random_missing_file.html
* **304 Not Modified:** Refresh the index.html page (the browser will automatically send the If-Modified-Since header).
* **Multi-threading & Keep-Alive:** Open multiple tabs or browsers simultaneously to see concurrent handling in the terminal output.
