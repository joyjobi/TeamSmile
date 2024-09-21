// socketHandler.js

module.exports = (io, socket, gameManager) => {
  console.log(`Client connected [id=${socket.id}]`);

  // Variable to track if the connected client is an admin
  let isAdmin = false;

  // Handle admin joining
  socket.on("admin_join", () => {
    isAdmin = true;
    console.log("Admin dashboard connected.");
    // Send current game status to Admin Dashboard
    gameManager.sendAdminUpdates(socket);
    // Optionally, emit a welcome message
    socket.emit("admin_message", { message: "Welcome Admin!" });
  });

  // Handle admin events
  socket.on("admin_set_game_type", (data) => {
    if (isAdmin) {
      console.log(`Received 'admin_set_game_type' event: ${data.gameType}`);
      gameManager.setActiveGameType(data.gameType);
    } else {
      console.log("Received 'admin_set_game_type' event from non-admin.");
      socket.emit("error", { message: "Unauthorized action." });
    }
  });

  socket.on("admin_start_game", (data) => {
    // Accept data containing rounds
    if (isAdmin) {
      const rounds = (data && data.rounds) || 5; // Default to 5 rounds if not specified
      console.log(
        `Received 'admin_start_game' event from admin with rounds: ${rounds}`
      );
      gameManager.startGame(rounds);
    } else {
      console.log("Received 'admin_start_game' event from non-admin.");
      socket.emit("error", { message: "Unauthorized action." });
    }
  });

  socket.on("admin_stop_game", () => {
    if (isAdmin) {
      console.log("Received 'admin_stop_game' event from admin.");
      gameManager.stopGame();
    } else {
      console.log("Received 'admin_stop_game' event from non-admin.");
      socket.emit("error", { message: "Unauthorized action." });
    }
  });

  socket.on("admin_reset_game", () => {
    if (isAdmin) {
      console.log("Received 'admin_reset_game' event from admin.");
      gameManager.resetGame();
    } else {
      console.log("Received 'admin_reset_game' event from non-admin.");
      socket.emit("error", { message: "Unauthorized action." });
    }
  });

  socket.on("admin_update_config", (data) => {
    if (isAdmin) {
      console.log("Received 'admin_update_config' event from admin:", data);
      gameManager.updateConfig(data.promptInterval, data.responseTimeout);
    } else {
      console.log("Received 'admin_update_config' event from non-admin.");
      socket.emit("error", { message: "Unauthorized action." });
    }
  });

  socket.on("admin_request_update", () => {
    if (isAdmin) {
      console.log("Received 'admin_request_update' event from admin.");
      gameManager.sendAdminUpdates(socket);
    } else {
      console.log("Received 'admin_request_update' event from non-admin.");
      socket.emit("error", { message: "Unauthorized action." });
    }
  });

  // Handle client joining the game (Game Tester)
  socket.on("join", (data) => {
    const { player_id } = data;
    console.log(`Player joined: ${player_id}`);
    gameManager.addClient(socket, player_id);
    io.emit("admin_message", {
      message: `Player '${player_id}' joined the game.`,
    });
  });

  // Handle player responses
  socket.on("response", (data) => {
    const { player_id } = data;
    console.log(`Received response from ${player_id}:`, data);
    gameManager.recordResponse(data);
    io.emit("admin_message", {
      message: `Received response from '${player_id}'.`,
    });
  });

  // Handle game reset initiated by a client
  socket.on("reset", () => {
    console.log("Received 'reset' event from client.");
    gameManager.resetGame();
    io.emit("admin_message", { message: "Game has been reset by a client." });
  });

  // Handle client disconnection
  socket.on("disconnect", () => {
    console.log(`Client disconnected [id=${socket.id}]`);
    if (isAdmin) {
      console.log("Admin dashboard disconnected.");
    } else {
      const player_id = gameManager.removeClient(socket);
      if (player_id) {
        io.emit("admin_message", {
          message: `Player '${player_id}' disconnected.`,
        });
      }
    }
  });
};
