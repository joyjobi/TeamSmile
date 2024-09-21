// server.js

const express = require("express");
const http = require("http");
const { Server } = require("socket.io");
const GameManager = require("./gameManager"); // Ensure correct path and casing
const socketHandler = require("./socketHandler"); // Function to handle sockets

const app = express();
const server = http.createServer(app);
const io = new Server(server, {
  cors: {
    //origin: "http://localhost:3000", // Adjust based on your setup
    origin: "*",
    methods: ["GET", "POST"],
  },
});

// Correct instantiation using 'new'
const gameManager = new GameManager(io);

// Pass the instance to socketHandler
io.on("connection", (socket) => {
  socketHandler(io, socket, gameManager);
});

const PORT = process.env.PORT || 5000;
server.listen(PORT, () => {
  console.log(`Server listening on port ${PORT}`);
});
