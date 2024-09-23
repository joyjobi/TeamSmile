# TeamSmile Game Platform

## Description
This project is a multi-player game platform featuring two main games currently: Rock-Paper-Scissors and a Hand Gesture Counting Game to stream through Conferencing Video Feed. It consists of two primary components:

1. **Client**: Python-based application for game logic and gesture detection.
2. **Server**: Node.js-based server for managing game states, communication, and an admin dashboard.


## Project Structure 
├── Client
│   ├── game_logic.py
│   ├── game_manager.py
│   ├── gesture_detection.py
│   ├── main.py
│   ├── network_client.py
│   └── README.md
├── Server
│   ├── admin-dashboard
│   ├── gameManager.js
│   ├── minimal_server.js
│   ├── server.js
│   ├── socketHandler.js
│   └── README.md
└── README.md


### Prerequisites
- **Node.js** and **npm**: Make sure you have Node.js installed.
- **Python 3.x**: Required for running the client application.
- **OpenCV**: Required for gesture detection on the client side.

### Installing Dependencies
#### Server
```bash
cd Server
npm install
