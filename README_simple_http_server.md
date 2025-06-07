# 🌐 Simple HTTP Server

A lightweight HTTP server built using Python’s `socket` module to handle basic GET and POST requests without external libraries.

## 🚀 Features

- Serves static HTML content
- Handles basic `GET` and `POST` requests
- Returns appropriate HTTP status codes (200 OK, 404 Not Found, etc.)
- Minimalist and beginner-friendly structure
- Extendable with custom endpoints

## 📂 Repository Structure

```
├── server.py          # Main HTTP server file
├── index.html         # Sample HTML file served by the server
├── README.md
```

## 🛠 How to Run

### 1. Start the Server
```bash
python3 server.py
```

By default, the server runs on `localhost:8080`.

### 2. Test in Browser
Open your browser and navigate to:

```
http://localhost:8080
```

### 3. Sample POST Request (Using curl)
```bash
curl -X POST -d "name=TestUser" http://localhost:8080
```

## 🧠 Concepts Used

- Raw socket programming in Python
- Manual parsing of HTTP headers and bodies
- HTTP protocol basics (status codes, methods, headers)

## 🧱 Potential Extensions

- Add support for serving multiple file types
- Implement routing for different endpoints
- Add concurrency with threading

## 📄 License

This project is licensed under the MIT License.