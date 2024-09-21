// minimal_server.js

const express = require("express");
const http = require("http");
const { Server } = require("socket.io");

const app = express();
const server = http.createServer(app);
const io = new Server(server, {
  cors: {
    origin: "*", // Allow all origins for testing
    methods: ["GET", "POST"],
  },
});

io.on("connection", (socket) => {
  console.log(`Client connected [id=${socket.id}]`);

  socket.on("join", (data) => {
    const { player_id } = data;
    if (!player_id) {
      console.log(`Socket ${socket.id} attempted to join without a player_id.`);
      return;
    }
    socket.join("game");
    console.log(`Player joined: ${player_id} and joined 'game' room.`);

    // Emit a 'prompt' event after joining
    setTimeout(() => {
      io.to("game").emit("prompt", {
        prompt: "Rock",
        responseTimeout: 7000,
        currentRound: 1,
        totalRounds: 5,
      });
      console.log("Emitted 'prompt' event to 'game' room.");
    }, 2000);
  });

  socket.on("response", (data) => {
    console.log(`Received response from ${data.player_id}: Gesture=${data.gesture}`);
  });

  socket.on("disconnect", () => {
    console.log(`Client disconnected [id=${socket.id}]`);
  });
});

const PORT = 5000;
server.listen(PORT, () => {
  console.log(`Minimal Server listening on port ${PORT}`);
});
