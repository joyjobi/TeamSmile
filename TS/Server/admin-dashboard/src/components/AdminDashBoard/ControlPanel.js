import React, { useState, useContext } from "react";
import {
  Button,
  TextField,
  MenuItem,
  Box,
  Typography,
  Grid,
} from "@mui/material";
import { SocketContext } from "../../contexts/SocketContext"; // Adjust the import path as necessary

function ControlPanel({ gameType, setGameType }) {
  const socket = useContext(SocketContext); // Access socket via context
  const [promptInterval, setPromptInterval] = useState(3000);
  const [responseTimeout, setResponseTimeout] = useState(7000);
  const [rounds, setRounds] = useState(5); // Default rounds

  const handleUpdateConfig = () => {
    if (socket) {
      console.log("Updating configuration with the following values:", {
        gameType,
        promptInterval: parseInt(promptInterval),
        responseTimeout: parseInt(responseTimeout),
        rounds: parseInt(rounds),
      });
      socket.emit("admin_set_game_type", { gameType });
      socket.emit("admin_update_config", {
        promptInterval: parseInt(promptInterval),
        responseTimeout: parseInt(responseTimeout),
      });
    }
  };

  const handleStartGame = () => {
    if (socket) {
      console.log("Starting game with rounds:", rounds);
      socket.emit("admin_start_game", { rounds: parseInt(rounds) });
    }
  };

  const handleStopGame = () => {
    if (socket) {
      console.log("Stopping game.");
      socket.emit("admin_stop_game");
    }
  };

  const handleResetGame = () => {
    if (socket) {
      console.log("Resetting game.");
      socket.emit("admin_reset_game");
    }
  };

  return (
    <Box
      sx={{
        padding: 3,
        maxWidth: 600,
        margin: "0 auto",
        backgroundColor: "#f9f9f9",
        borderRadius: 2,
        boxShadow: 3,
      }}
    >
      <Typography variant="h5" align="center" gutterBottom>
        Control Panel
      </Typography>

      <Grid container spacing={2}>
        {/* Game Type Selection */}
        <Grid item xs={12}>
          <TextField
            select
            fullWidth
            label="Select Game Type"
            value={gameType}
            onChange={(e) => setGameType(e.target.value)}
            variant="outlined"
          >
            <MenuItem value="rps">Rock-Paper-Scissors</MenuItem>
            <MenuItem value="counting">Counting Game</MenuItem>
          </TextField>
        </Grid>

        {/* Prompt Interval */}
        <Grid item xs={6}>
          <TextField
            fullWidth
            label="Prompt Interval (ms)"
            type="number"
            value={promptInterval}
            onChange={(e) => setPromptInterval(e.target.value)}
            variant="outlined"
          />
        </Grid>

        {/* Response Timeout */}
        <Grid item xs={6}>
          <TextField
            fullWidth
            label="Response Timeout (ms)"
            type="number"
            value={responseTimeout}
            onChange={(e) => setResponseTimeout(e.target.value)}
            variant="outlined"
          />
        </Grid>

        {/* Number of Rounds */}
        <Grid item xs={12}>
          <TextField
            fullWidth
            label="Number of Rounds"
            type="number"
            value={rounds}
            onChange={(e) => setRounds(e.target.value)}
            variant="outlined"
            inputProps={{ min: 1 }}
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

        {/* Start, Stop, and Reset Game Buttons */}
        <Grid item xs={12}>
          <Box sx={{ display: "flex", justifyContent: "space-between" }}>
            <Button
              variant="contained"
              color="primary"
              onClick={handleStartGame}
              sx={{ width: "48%" }}
            >
              Start Game
            </Button>
            <Button
              variant="outlined"
              color="secondary"
              onClick={handleStopGame}
              sx={{ width: "48%" }}
            >
              Stop Game
            </Button>
          </Box>
        </Grid>

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
