// gameManager.js

// Notify admins about the game type change
const getCurrentTimestamp = () => new Date().toISOString();

class GameManager {
  constructor(io) {
    this.io = io;
    this.clients = {}; // { socket.id: { player_id, socket } }
    this.connectedPlayers = [];
    this.gameTypes = ["rps", "counting"];
    this.activeGameType = "rps"; // Default game type
    this.gameState = {
      promptInterval: 3000, // 3 seconds
      responseTimeout: 7000, // 7 seconds
      currentPrompt: null,
      state: "waiting", // 'waiting', 'prompted', 'responded'
      responses: [],
      gameLoop: null,
      totalRounds: 5, // Default number of rounds
      currentRound: 0, // Tracks the current round
    };
    this.playerScores = {}; // { player_id: { score, wins, losses, ties } }
  }

  addClient(socket, player_id) {
    this.clients[socket.id] = { player_id, socket };
    this.connectedPlayers.push(player_id);
    socket.join("game"); // Join the 'game' room for Game Testers
    this.initializePlayerScore(player_id);
    this.broadcastPlayerList();
    // Send the active game type to the client
    socket.emit("game_type", { gameType: this.activeGameType });

    // Emit updated client list to Admin Dashboard
    this.io
      .to("admins")
      .emit("admin_client_list", { clients: this.connectedPlayers });
  }

  removeClient(socket) {
    if (this.clients[socket.id]) {
      const { player_id } = this.clients[socket.id];
      delete this.clients[socket.id];
      const index = this.connectedPlayers.indexOf(player_id);
      if (index !== -1) {
        this.connectedPlayers.splice(index, 1);
      }
      this.broadcastPlayerList();

      // Emit updated client list to Admin Dashboard
      this.io
        .to("admins")
        .emit("admin_client_list", { clients: this.connectedPlayers });
      return player_id;
    }
    return null;
  }

  broadcastPlayerList() {
    const clients = this.connectedPlayers.map((player_id) => ({ player_id }));
    this.io.to("admins").emit("admin_client_list", { clients });
    this.io.to("game").emit("player_list", { clients }); // Optionally send to Game Testers
  }

  initializePlayerScore(player_id) {
    if (!this.playerScores[player_id]) {
      this.playerScores[player_id] = {
        score: 0,
        wins: 0,
        losses: 0,
        ties: 0,
      };
    }
  }

  setActiveGameType(gameType) {
    if (this.gameTypes.includes(gameType)) {
      this.activeGameType = gameType;
      console.log(`Active game type set to '${gameType}'.`);

      this.io.to("admins").emit("admin_message", {
        message: `Game '${this.activeGameType}' has been stopped.`,
        timestamp: getCurrentTimestamp(), // Added timestamp
        type: "info", // Added type (e.g., 'info', 'warning', 'error')
      });
      // Notify all clients of the game type change
      this.io
        .to("game")
        .emit("game_type_changed", { gameType: this.activeGameType });
      // Optionally, start a new round if needed
      // this.startNewRound();
    }
  }

  startGame(totalRounds = 5) {
    // Default to 5 rounds if not specified
    if (!this.gameState.gameLoop) {
      this.gameState.totalRounds = totalRounds;
      this.gameState.currentRound = 0;
      this.startGameLoop();
      console.log(
        `Game '${this.activeGameType}' started for ${totalRounds} rounds.`
      );
      this.io.to("admins").emit("admin_message", {
        message: `Game '${this.activeGameType}' started for ${totalRounds} rounds.`,
        timestamp: getCurrentTimestamp(),
        type: "info",
      });
    }
  }

  resetGame() {
    if (this.gameState.gameLoop) {
      clearInterval(this.gameState.gameLoop);
      this.gameState.gameLoop = null;
    }
    this.gameState.state = "waiting";
    this.gameState.currentPrompt = null;
    this.gameState.responses = [];
    this.gameState.currentRound = 0; // Reset current round
    this.gameState.totalRounds = 5; // Reset to default rounds
    // Disconnect all Game Testers
    Object.values(this.clients).forEach((client) => {
      client.socket.disconnect(true);
    });
    this.clients = {};
    this.connectedPlayers = [];
    // Reset player scores
    this.playerScores = {};
    console.log(`Game '${this.activeGameType}' reset.`);
    // Notify all clients to reset
    this.io.to("game").emit("reset");
    this.io.to("admins").emit("reset");
    // Broadcast updated player list
    this.broadcastPlayerList();
    // Emit admin message
    this.io.to("admins").emit("admin_message", {
      message: `Game '${this.activeGameType}' reset.`,
      timestamp: getCurrentTimestamp(),
      type: "info",
    });

    // Emit updated player scores to Admin Dashboard and Game Testers
    this.broadcastPlayerScores();
  }
  updateConfig(promptInterval, responseTimeout) {
    this.gameState.promptInterval = promptInterval;
    this.gameState.responseTimeout = responseTimeout;
    // Restart the game loop to apply new configurations
    if (this.gameState.gameLoop) {
      clearInterval(this.gameState.gameLoop);
      this.startGameLoop();
    }
    console.log(
      `Game configuration updated: Prompt Interval=${promptInterval}ms, Response Timeout=${responseTimeout}ms.`
    );
    this.io.to("admins").emit("admin_message", {
      message: `Game configuration updated: Prompt Interval=${promptInterval}ms, Response Timeout=${responseTimeout}ms.`,
      timestamp: getCurrentTimestamp(),
      type: "info",
    });
    // Notify all clients about the updated configuration
    this.io.to("game").emit("config_updated", {
      promptInterval: this.gameState.promptInterval,
      responseTimeout: this.gameState.responseTimeout,
    });
  }

  startGameLoop() {
    this.gameState.gameLoop = setInterval(() => {
      if (this.connectedPlayers.length > 0) {
        if (this.gameState.currentRound < this.gameState.totalRounds) {
          this.startNewRound();
        } else {
          this.stopGame(); // Automatically stop the game after reaching totalRounds
        }
      }
    }, this.gameState.promptInterval + this.gameState.responseTimeout + 2000);
  }

  stopGame() {
    if (this.gameState.gameLoop) {
      clearInterval(this.gameState.gameLoop);
      this.gameState.gameLoop = null;
    }
    this.gameState.state = "waiting";
    this.gameState.currentPrompt = null;
    this.gameState.responses = [];
    this.gameState.currentRound = 0;
    this.gameState.totalRounds = 5; // Reset to default rounds if desired
    console.log(`Game '${this.activeGameType}' has been stopped.`);
    this.io.to("admins").emit("admin_message", {
      message: `Game '${this.activeGameType}' has been stopped.`,
      timestamp: getCurrentTimestamp(),
      type: "info",
    });
  }

  startNewRound() {
    const gameType = this.activeGameType;
    this.gameState.state = "prompted";
    this.gameState.responses = [];
    this.gameState.currentRound += 1; // Increment the current round

    // Generate a prompt
    if (gameType === "rps") {
      const gestures = ["Rock", "Paper", "Scissors"];
      this.gameState.currentPrompt =
        gestures[Math.floor(Math.random() * gestures.length)];
    } else if (gameType === "counting") {
      this.gameState.currentPrompt = Math.floor(Math.random() * 5) + 1; // Random number between 1 and 5
    }

    console.log(
      `Round ${this.gameState.currentRound}: New Prompt: ${this.gameState.currentPrompt}`
    );

    // Calculate relative timeout
    const responseTimeout = this.gameState.responseTimeout; // 7000ms

    // Broadcast prompt to all Game Testers
    this.io.to("game").emit("prompt", {
      prompt: this.gameState.currentPrompt,
      responseTimeout: responseTimeout,
      currentRound: this.gameState.currentRound, // Added current round
      totalRounds: this.gameState.totalRounds, // Added total rounds
    });

    // Notify admin dashboard about the new round (for countdown)
    const countdownDuration = responseTimeout; // e.g., 7000ms
    this.io.to("admins").emit("admin_round_started", {
      prompt: this.gameState.currentPrompt,
      countdownDuration: countdownDuration,
      currentRound: this.gameState.currentRound, // Optionally send current round number
      totalRounds: this.gameState.totalRounds, // Optionally send total rounds
    });

    // Set a timeout to collect responses
    setTimeout(() => {
      this.collectResponses();
    }, responseTimeout);
  }

  collectResponses() {
    const gameType = this.activeGameType;
    this.gameState.state = "responded";

    // Process responses
    let results = [];

    this.gameState.responses.forEach((response) => {
      let resultText = "";
      let roundScore = 0;

      if (gameType === "rps") {
        const outcome = this.determineWinner(
          response.gesture,
          this.gameState.currentPrompt
        );
        const confidenceWeight = 0.7;
        const timeWeight = 0.3;
        const timeScore = Math.max(
          0,
          (this.gameState.responseTimeout - response.response_time) /
            this.gameState.responseTimeout
        );
        roundScore =
          (response.confidence_score * confidenceWeight +
            timeScore * timeWeight) *
          100;
        resultText = `${outcome}`;

        // Update player scores
        this.updatePlayerScore(response.player_id, outcome);
      } else if (gameType === "counting") {
        const correctness =
          parseInt(response.gesture) === this.gameState.currentPrompt
            ? "Correct"
            : "Incorrect";
        const confidenceWeight = 0.7;
        const timeWeight = 0.3;
        const timeScore = Math.max(
          0,
          (this.gameState.responseTimeout - response.response_time) /
            this.gameState.responseTimeout
        );
        roundScore =
          (response.confidence_score * confidenceWeight +
            timeScore * timeWeight) *
          100;
        resultText = `${correctness}`;

        // Update player scores
        this.updatePlayerScore(
          response.player_id,
          correctness === "Correct" ? "Win" : "Loss"
        );
      }

      results.push({
        player_id: response.player_id,
        result_text: resultText,
        round_score: roundScore,
      });
    });

    // Broadcast results to all Game Testers
    this.io.to("game").emit("result", {
      results: results,
    });

    // Send updated player scores to Admin Dashboard and Game Testers
    this.broadcastPlayerScores();

    this.gameState.state = "waiting";
  }

  determineWinner(playerGesture, systemGesture) {
    if (playerGesture === systemGesture) {
      return "Tie";
    } else if (
      (playerGesture === "Rock" && systemGesture === "Scissors") ||
      (playerGesture === "Paper" && systemGesture === "Rock") ||
      (playerGesture === "Scissors" && systemGesture === "Paper")
    ) {
      return "You Win!";
    } else {
      return "You Lose!";
    }
  }

  updatePlayerScore(player_id, outcome) {
    if (!this.playerScores[player_id]) {
      this.playerScores[player_id] = { score: 0, wins: 0, losses: 0, ties: 0 };
    }
    const playerScore = this.playerScores[player_id];
    if (outcome === "You Win!" || outcome === "Win" || outcome === "Correct") {
      playerScore.score += 1;
      playerScore.wins += 1;
    } else if (
      outcome === "You Lose!" ||
      outcome === "Loss" ||
      outcome === "Incorrect"
    ) {
      playerScore.losses += 1;
    } else if (outcome === "Tie") {
      playerScore.ties += 1;
    }

    // Emit updated player scores to Admin Dashboard and Game Testers
    this.broadcastPlayerScores();
  }

  broadcastPlayerScores() {
    const scores = this.connectedPlayers.map((player_id) => {
      const playerScore = this.playerScores[player_id] || {
        score: 0,
        wins: 0,
        losses: 0,
        ties: 0,
      };
      return { player_id, ...playerScore };
    });
    this.io.to("admins").emit("admin_player_scores", {
      scores,
    });
    this.io.to("game").emit("player_scores", {
      scores,
    });
  }

  recordResponse(data) {
    this.gameState.responses.push({
      player_id: data.player_id,
      gesture: data.gesture,
      response_time: data.response_time,
      confidence_score: data.confidence_score,
    });
  }

  sendAdminUpdates(socket) {
    // Send connected clients
    const clients = this.connectedPlayers.map((player_id) => ({ player_id }));
    socket.emit("admin_client_list", { clients });

    // Send player scores
    const scores = clients.map((client) => {
      const player_id = client.player_id;
      const playerScore = this.playerScores[player_id] || {
        score: 0,
        wins: 0,
        losses: 0,
        ties: 0,
      };
      return { player_id, ...playerScore };
    });
    socket.emit("admin_player_scores", {
      scores,
    });
  }
}

module.exports = GameManager;
