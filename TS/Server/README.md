
# Server Component

## Description
The server component is a Node.js-based server that manages game states, handles client-server communication, and provides an admin dashboard for game control.

## Table of Contents
- [Installation](#installation)
- [Setup](#setup)
- [Usage](#usage)
- [Project Structure](#project-structure)
- [License](#license)

## Installation

### Prerequisites
- **Node.js**: Make sure you have Node.js installed.

### Installing Dependencies
1. Navigate to the `Server` directory.
2. Install the dependencies:
    ```bash
    npm install
    ```

## Setup
1. Run the server using:
    ```bash
    npm start
    ```
2. The server will be available at `http://localhost:5000`.

### Scripts
- **Start**: `npm start` - Runs the server.
- **Development**: `npm run dev` - Runs the server with Nodemon for development.

## Usage
- The server uses `socket.io` for real-time communication between the clients and server.
- The admin dashboard can be accessed through `http://localhost:5000/admin-dashboard`.
- Admins can start, stop, and configure games using the dashboard.

## Project Structure


![image](https://github.com/user-attachments/assets/c12438ba-494c-4d44-bfd6-269cffc13270)
