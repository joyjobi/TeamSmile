
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


    ## Server-Side Architecture

    Before diving into the refactoring, it's essential to comprehend how the server manages the game:

    ### Server Components

    - **server.js**: Initializes the Express server and Socket.io, and binds incoming connections to the GameManager.
    - **gameManager.js**: Manages game state, handles game logic, and communicates with connected clients (both Game Testers and Admins).
    - **socketHandler.js**: Handles Socket.io events from clients, differentiating between Admin and Game Tester actions.

    ### Key Server Events

    #### Admin Events
    - `admin_join`
    - `admin_set_game_type`
    - `admin_start_game`
    - `admin_stop_game`
    - `admin_reset_game`
    - `admin_update_config`
    - `admin_request_update`

    #### Game Tester Events
    - `join`
    - `response`
    - `reset`

    #### Server-to-Client Events
    - `game_type`
    - `game_type_changed`
    - `prompt`
    - `result`
    - `player_scores`
    - `admin_message`
    - `admin_client_list`
    - `admin_player_scores`
    - `admin_round_started`
    - `config_updated`
    - `reset`
    
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
