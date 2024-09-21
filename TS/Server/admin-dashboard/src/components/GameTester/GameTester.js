import React, { useEffect, useState, useContext } from "react";
import { SocketContext } from "../../contexts/SocketContext";
import Prompt from "./Prompt";
import Response from "./Response";
import Result from "./Result";
import Scores from "./Scores";
import PlayerList from "./PlayerList";
import "./GameTester.css";
import { toast } from "react-toastify";

// Material-UI Components
import {
  Container,
  Typography,
  TextField,
  Button,
  Card,
  CardContent,
  Grid,
  Box,
} from "@mui/material";
import SportsEsportsIcon from "@mui/icons-material/SportsEsports";

function GameTester() {
  const socket = useContext(SocketContext);
  const [playerId, setPlayerId] = useState("");
  const [joined, setJoined] = useState(false);
  const [gameType, setGameType] = useState("");
  const [gameState, setGameState] = useState("waiting"); // 'waiting', 'prompted', 'responded'
  const [prompt, setPrompt] = useState("");
  const [result, setResult] = useState("");
  const [players, setPlayers] = useState([]);
  const [playerScores, setPlayerScores] = useState([]);
  const [countdown, setCountdown] = useState("");
  const [countdownIntervalId, setCountdownIntervalId] = useState(null);

  useEffect(() => {
    // Handle socket events
    socket.on("game_type", (data) => {
      setGameType(data.gameType);
    });

    socket.on("game_type_changed", (data) => {
      setGameType(data.gameType);
      toast.info(
        `Game type changed to: ${
          data.gameType === "rps" ? "Rock-Paper-Scissors" : "Counting Game"
        }`
      );
    });

    socket.on("prompt", (data) => {
      console.log(
        "Received 'prompt' event with responseTimeout:",
        data.responseTimeout
      );
      setGameState("prompted");
      setPrompt(data.prompt);
      setResult("");
      startCountdown(data.responseTimeout);
    });

    socket.on("result", (data) => {
      const playerResult = data.results.find((r) => r.player_id === playerId);
      if (playerResult) {
        setResult(playerResult.result_text);
        toast.success(`Result: ${playerResult.result_text}`);
      } else {
        setResult("No result received.");
        toast.warn("No result received.");
      }
      setGameState("waiting");
      clearCountdown();
      setPrompt("");
    });

    socket.on("player_list", (data) => {
      setPlayers(data.clients);
    });

    socket.on("reset", () => {
      toast.info("Game has been reset.");
      resetGame();
    });

    // Listen for player_scores event
    socket.on("player_scores", (data) => {
      setPlayerScores(data.scores);
      console.log("Received player scores:", data.scores);
    });

    return () => {
      socket.off("game_type");
      socket.off("game_type_changed");
      socket.off("prompt");
      socket.off("result");
      socket.off("player_list");
      socket.off("reset");
      socket.off("player_scores");
    };
  }, [socket, playerId]);

  // Countdown timer functions
  const startCountdown = (duration) => {
    let timeRemaining = duration;
    setCountdown(`${(timeRemaining / 1000).toFixed(1)} seconds`);

    const interval = setInterval(() => {
      timeRemaining -= 100;
      if (timeRemaining <= 0) {
        clearInterval(interval);
        setCountdown("Time's up!");
        setGameState("waiting");
        toast.warn("Time's up! You didn't respond in time.");
      } else {
        setCountdown(`${(timeRemaining / 1000).toFixed(1)} seconds`);
      }
    }, 100);

    // Save interval ID to state for clearing later
    setCountdownIntervalId(interval);
  };

  const clearCountdown = () => {
    if (countdownIntervalId) {
      clearInterval(countdownIntervalId);
      setCountdownIntervalId(null);
      setCountdown("");
    }
  };

  const resetGame = () => {
    setJoined(false);
    setPlayerId("");
    setGameType("");
    setGameState("waiting");
    setPrompt("");
    setResult("");
    setPlayers([]);
    setPlayerScores([]);
    clearCountdown();
  };

  const handleJoin = () => {
    if (playerId.trim() === "") {
      toast.error("Please enter a Player ID.");
      return;
    }
    socket.emit("join", { player_id: playerId });
    setJoined(true);
    toast.success(`Joined the game as ${playerId}`);
  };

  const handleSubmitResponse = (gesture) => {
    if (gameState !== "prompted") {
      toast.error("It's not time to submit a response.");
      return;
    }

    const responseTime = Date.now(); // You can calculate actual response time if needed
    const confidenceScore = 1.0; // Adjust as necessary

    socket.emit("response", {
      player_id: playerId,
      gesture,
      response_time: responseTime,
      confidence_score: confidenceScore,
    });

    setGameState("responded");
    toast.info("Response submitted.");
  };

  return (
    <Container
      maxWidth="sm"
      sx={{
        minHeight: "100vh",
        backgroundColor: "#f5f5f5",
        paddingTop: 2,
        paddingBottom: 2,
      }}
    >
      <Box
        sx={{
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          marginBottom: 2,
        }}
      >
        <SportsEsportsIcon fontSize="large" sx={{ marginRight: 1 }} />
        <Typography variant="h4">
          {joined ? `Game Tester - ${playerId}` : "Game Tester"}
        </Typography>
      </Box>

      {!joined ? (
        <Card
          elevation={3}
          sx={{
            padding: 2,
            textAlign: "center",
          }}
        >
          <CardContent>
            <Typography variant="h6" gutterBottom>
              Join the Game
            </Typography>
            <TextField
              label="Player ID"
              variant="outlined"
              fullWidth
              value={playerId}
              onChange={(e) => setPlayerId(e.target.value)}
              sx={{ marginBottom: 2 }}
            />
            <Button
              variant="contained"
              color="primary"
              fullWidth
              onClick={handleJoin}
            >
              Join Game
            </Button>
          </CardContent>
        </Card>
      ) : (
        <Card
          elevation={3}
          sx={{
            padding: 2,
          }}
        >
          <CardContent>
            {countdown && (
              <Box mb={2} textAlign="center">
                <Typography variant="subtitle1">
                  Time Remaining: {countdown}
                </Typography>
              </Box>
            )}
            <Grid container spacing={2}>
              <Grid item xs={12}>
                <Typography variant="h5" align="center" gutterBottom>
                  {gameType === "rps" ? "Rock-Paper-Scissors" : "Counting Game"}
                </Typography>
              </Grid>
              <Grid item xs={12}>
                <Prompt prompt={prompt} />
              </Grid>
              <Grid item xs={12}>
                <Response
                  disabled={gameState !== "prompted"}
                  onSubmit={handleSubmitResponse}
                  countdown={typeof countdown === "string" ? countdown : ""}
                  gameType={gameType}
                />
              </Grid>
              <Grid item xs={12}>
                <Result result={result} />
              </Grid>
              <Grid item xs={12}>
                <PlayerList players={players} />
              </Grid>
              <Grid item xs={12}>
                <Scores
                  playerScores={playerScores}
                  currentPlayerId={playerId}
                />
              </Grid>
            </Grid>
          </CardContent>
        </Card>
      )}
    </Container>
  );
}

export default GameTester;
