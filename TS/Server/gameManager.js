// gameManager.js

class GameManager {
  constructor(io) {
    this.io = io;
    this.clients = {}; // { socket.id: { player_id, socket } }
    this.connectedPlayers = [];
    this.gameTypes = ["rps", "counting"];
    this.activeGameType = "rps"; // Default game type
    this.gameState = {
      promptInterval: 10000, // 10 seconds
      responseTimeout: 7000, // 7 seconds
      currentPrompt: null,
      state: "waiting", // 'waiting', 'prompted', 'responded'
      responses: [],
      gameLoop: null,
    };
    this.playerScores = {}; // { player_id: { score, wins, losses, ties } }
  }

  addClient(socket, player_id) {
    this.clients[socket.id] = { player_id, socket };
    this.connectedPlayers.push(player_id);
    socket.join("game"); // Join a common room
    this.broadcastPlayerList();
    // Send the active game type to the client
    socket.emit("game_type", { gameType: this.activeGameType });

    // Emit updated client list to Admin Dashboard
    this.io.emit("admin_client_list", { clients: this.connectedPlayers });
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
      this.io.emit("admin_client_list", { clients: this.connectedPlayers });
      return player_id;
    }
    return null;
  }

  broadcastPlayerList() {
    const clients = this.connectedPlayers.map((player_id) => ({ player_id }));
    this.io.emit("player_list", { clients });
  }

  setActiveGameType(gameType) {
    if (this.gameTypes.includes(gameType)) {
      this.activeGameType = gameType;
      console.log(`Active game type set to '${gameType}'.`);
      // Optionally, notify admin about the game type change
      this.io.emit("admin_message", {
        message: `Game type changed to '${gameType}'.`,
      });
      // Notify all clients of the game type change
      this.io.emit("game_type_changed", { gameType: this.activeGameType });
      // Optionally, start a new round if needed
      // this.startNewRound();
    }
  }

  startGame() {
    if (!this.gameState.gameLoop) {
      this.startGameLoop();
      console.log(`Game '${this.activeGameType}' started.`);
      this.io.emit("admin_message", {
        message: `Game '${this.activeGameType}' started.`,
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
    // Disconnect all clients
    Object.values(this.clients).forEach((client) => {
      client.socket.disconnect(true);
    });
    this.clients = {};
    this.connectedPlayers = [];
    // Reset player scores
    this.playerScores = {};
    console.log(`Game '${this.activeGameType}' reset.`);
    // Notify clients to reset
    this.io.emit("reset");
    // Broadcast updated player list
    this.broadcastPlayerList();
    // Emit admin message
    this.io.emit("admin_message", {
      message: `Game '${this.activeGameType}' reset.`,
    });

    // Emit updated player scores to Admin Dashboard
    this.io.emit("admin_player_scores", { scores: [] });
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
      `Game configuration updated: Prompt Interval=${promptInterval}, Response Timeout=${responseTimeout}`
    );
    this.io.emit("admin_message", {
      message: `Game configuration updated: Prompt Interval=${promptInterval}ms, Response Timeout=${responseTimeout}ms.`,
    });
    // Notify all clients about the updated configuration
    this.io.emit("config_updated", {
      promptInterval: this.gameState.promptInterval,
      responseTimeout: this.gameState.responseTimeout,
    });
  }

  startGameLoop() {
    this.gameState.gameLoop = setInterval(() => {
      if (this.connectedPlayers.length > 0) {
        this.startNewRound();
      }
    }, this.gameState.promptInterval + this.gameState.responseTimeout + 2000);
  }

  startNewRound() {
    const gameType = this.activeGameType;
    this.gameState.state = "prompted";
    this.gameState.responses = [];

    // Generate a prompt
    if (gameType === "rps") {
      const gestures = ["Rock", "Paper", "Scissors"];
      this.gameState.currentPrompt =
        gestures[Math.floor(Math.random() * gestures.length)];
    } else if (gameType === "counting") {
      this.gameState.currentPrompt = Math.floor(Math.random() * 5) + 1; // Random number between 1 and 5
    }

    console.log(`New Prompt: ${this.gameState.currentPrompt}`);

    // Broadcast prompt to all connected clients
    this.io.emit("prompt", {
      prompt: this.gameState.currentPrompt,
      responseTimeout: this.gameState.responseTimeout,
    });

    // Notify admin dashboard about the new round (for countdown)
    const nextRoundTime =
      Date.now() +
      this.gameState.promptInterval +
      this.gameState.responseTimeout +
      2000;
    this.io.emit("admin_round_started", {
      prompt: this.gameState.currentPrompt,
      nextRoundTime: nextRoundTime,
    });

    // Set a timeout to collect responses
    setTimeout(() => {
      this.collectResponses();
    }, this.gameState.responseTimeout);
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
        resultText = `${outcome} | Round Score: ${roundScore.toFixed(1)}`;

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
        resultText = `${correctness} | Round Score: ${roundScore.toFixed(1)}`;

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

    // Broadcast results to all clients
    this.io.emit("result", {
      results: results,
    });

    // Send updated player scores to admin dashboard
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

    // Emit updated player scores to Admin Dashboard
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
    this.io.emit("admin_player_scores", {
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
