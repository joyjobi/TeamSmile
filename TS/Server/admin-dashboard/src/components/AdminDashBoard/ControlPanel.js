// src/components/AdminDashboard/ControlPanel.js

import React, { useState, useContext } from "react";
import {
  Button,
  TextField,
  Grid,
  Box,
  MenuItem,
  Typography,
} from "@mui/material";
import { SocketContext } from "../../contexts/SocketContext"; // Adjust the import path as necessary
import { toast } from "react-toastify";

function ControlPanel({ gameType, setGameType }) {
  const socket = useContext(SocketContext); // Access socket via context
  const [promptInterval, setPromptInterval] = useState(3000);
  const [responseTimeout, setResponseTimeout] = useState(7000);
  const [rounds, setRounds] = useState(5); // Default rounds

  const handleUpdateConfig = () => {
    if (socket) {
      console.log("Emitting 'admin_update_config' event with data:", {
        gameType,
        promptInterval: parseInt(promptInterval),
        responseTimeout: parseInt(responseTimeout),
      });
      socket.emit("admin_set_game_type", { gameType }); // Emit game type change
      socket.emit("admin_update_config", {
        gameType,
        promptInterval: parseInt(promptInterval),
        responseTimeout: parseInt(responseTimeout),
      });
      toast.success("Configuration updated successfully.");
    }
  };

  const handleStartGame = () => {
    if (socket) {
      console.log("Emitting 'admin_start_game' event.");
      socket.emit("admin_start_game", { rounds: parseInt(rounds) });
      toast.info(`Game started for ${rounds} rounds.`);
    }
  };

  const handleStopGame = () => {
    if (socket) {
      console.log("Emitting 'admin_stop_game' event.");
      socket.emit("admin_stop_game");
      toast.info("Game has been stopped.");
    }
  };

  const handleResetGame = () => {
    if (socket) {
      console.log("Emitting 'admin_reset_game' event.");
      socket.emit("admin_reset_game");
      toast.info("Game has been reset.");
    }
  };

  return (
    <Box sx={{ padding: 3, backgroundColor: "#f5f5f5", borderRadius: 2 }}>
      <Typography variant="h5" gutterBottom>
        Control Panel
      </Typography>
      <Grid container spacing={2}>
        {/* Game Type Selection */}
        <Grid item xs={12} sm={6}>
          <TextField
            select
            label="Game Type"
            value={gameType}
            onChange={(e) => setGameType(e.target.value)}
            fullWidth
            variant="outlined"
          >
            <MenuItem value="rps">Rock-Paper-Scissors</MenuItem>
            <MenuItem value="counting">Counting Game</MenuItem>
          </TextField>
        </Grid>

        {/* Prompt Interval */}
        <Grid item xs={12} sm={6}>
          <TextField
            label="Prompt Interval (ms)"
            type="number"
            value={promptInterval}
            onChange={(e) => setPromptInterval(e.target.value)}
            fullWidth
            variant="outlined"
            InputProps={{ inputProps: { min: 1000 } }}
          />
        </Grid>

        {/* Response Timeout */}
        <Grid item xs={12} sm={6}>
          <TextField
            label="Response Timeout (ms)"
            type="number"
            value={responseTimeout}
            onChange={(e) => setResponseTimeout(e.target.value)}
            fullWidth
            variant="outlined"
            InputProps={{ inputProps: { min: 1000 } }}
          />
        </Grid>

        {/* Number of Rounds */}
        <Grid item xs={12} sm={6}>
          <TextField
            label="Number of Rounds"
            type="number"
            value={rounds}
            onChange={(e) => setRounds(e.target.value)}
            fullWidth
            variant="outlined"
            InputProps={{ inputProps: { min: 1 } }}
          />
        </Grid>

        {/* Update Configuration Button */}
        <Grid item xs={12}>
          <Button
            variant="contained"
            color="primary"
            onClick={handleUpdateConfig}
            fullWidth
          >
            Update Configuration
          </Button>
        </Grid>

        {/* Start and Stop Game Buttons */}
        <Grid item xs={6}>
          <Button
            variant="contained"
            color="success"
            onClick={handleStartGame}
            fullWidth
          >
            Start Game
          </Button>
        </Grid>
        <Grid item xs={6}>
          <Button
            variant="outlined"
            color="error"
            onClick={handleStopGame}
            fullWidth
          >
            Stop Game
          </Button>
        </Grid>

        {/* Reset Game Button */}
        <Grid item xs={12}>
          <Button
            variant="outlined"
            color="secondary"
            onClick={handleResetGame}
            fullWidth
          >
            Reset Game
          </Button>
        </Grid>
      </Grid>
    </Box>
  );
}

export default ControlPanel;
