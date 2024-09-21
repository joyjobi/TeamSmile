// src/components/AdminDashBoard/AdminDashboard.js

import React, { useEffect, useState, useContext } from "react";
import { SocketContext } from "../../contexts/SocketContext";
import ControlPanel from "./ControlPanel";
import GameStats from "./GameStats";
import Messages from "./Messages";
import CurrentPrompt from "./CurrentPrompt";
import { toast } from "react-toastify"; // Import toast
import { Container, Typography, Grid } from "@mui/material"; // MUI Components

function AdminDashboard() {
  const socket = useContext(SocketContext);
  const [gameType, setGameType] = useState("rps");
  const [nextRoundTime, setNextRoundTime] = useState(null);
  const [currentPrompt, setCurrentPrompt] = useState("N/A");
  const [clientCount, setClientCount] = useState(0);
  const [clients, setClients] = useState([]);
  const [playerScores, setPlayerScores] = useState([]);
  const [messages, setMessages] = useState([]);

  useEffect(() => {
    if (!socket) return;

    socket.on("connect", () => {
      socket.emit("admin_join");
      socket.emit("admin_request_update");
    });

    socket.on("admin_message", (data) => {
      setMessages((prevMessages) => {
        const updatedMessages = [...prevMessages, data];
        return updatedMessages.length > 100
          ? updatedMessages.slice(updatedMessages.length - 100)
          : updatedMessages;
      });
      toast.info(`${data.timestamp} - ${data.message}`); // Show toast with timestamp
    });

    socket.on("admin_client_list", (data) => {
      setClients(data.clients);
      setClientCount(data.clients.length);
    });

    socket.on("game_type_changed", (data) => {
      setGameType(data.gameType);
      setNextRoundTime(null);
      setCurrentPrompt("N/A");
      socket.emit("admin_request_update");
    });

    socket.on("admin_round_started", (data) => {
      setNextRoundTime(data.nextRoundTime);
      setCurrentPrompt(data.prompt);
    });

    socket.on("admin_player_scores", (data) => {
      setPlayerScores(data.scores);
    });

    socket.on("reset", () => {
      setNextRoundTime(null);
      setCurrentPrompt("N/A");
      toast.info("Game has been reset.");
    });

    return () => {
      socket.off("connect");
      socket.off("admin_message");
      socket.off("admin_client_list");
      socket.off("game_type_changed");
      socket.off("admin_round_started");
      socket.off("admin_player_scores");
      socket.off("reset");
    };
  }, [socket]);

  return (
    <Container maxWidth="lg" style={{ marginTop: "20px" }}>
      <Typography variant="h4" gutterBottom>
        Admin Dashboard
      </Typography>
      <Grid container spacing={3}>
        <Grid item xs={12} md={6}>
          <ControlPanel gameType={gameType} setGameType={setGameType} />
        </Grid>
        <Grid item xs={12} md={6}>
          <CurrentPrompt
            currentPrompt={currentPrompt}
            nextRoundTime={nextRoundTime}
          />
        </Grid>
        <Grid item xs={12}>
          <GameStats
            clientCount={clientCount}
            clients={clients}
            playerScores={playerScores}
          />
        </Grid>
        <Grid item xs={12}>
          <Messages messages={messages} /> {/* Integrate Messages here */}
        </Grid>
      </Grid>
    </Container>
  );
}

export default AdminDashboard;
