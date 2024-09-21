// src/components/GameTester/Scores.js

import React from "react";
import { Typography, Box, Card } from "@mui/material";

function Scores({ playerScores, currentPlayerId }) {
  // Sort players by score in descending order
  const sortedScores = [...playerScores].sort((a, b) => b.score - a.score);

  return (
    <Card variant="outlined" sx={{ padding: 2 }}>
      <Typography variant="h6" gutterBottom>
        Player Scores
      </Typography>
      {sortedScores.length > 0 ? (
        <Box sx={{ maxHeight: 200, overflowY: "auto" }}>
          {sortedScores.map((player, index) => (
            <Box
              key={index}
              sx={{
                display: "flex",
                justifyContent: "space-between",
                padding: 1,
                borderBottom: "1px solid #ccc",
                backgroundColor: player.player_id === currentPlayerId ? "#d1e7dd" : "transparent",
                borderRadius: 1,
              }}
            >
              <Typography variant="body2">
                {player.player_id}
              </Typography>
              <Typography variant="body2">
                Score: {player.score} | Wins: {player.wins} | Losses: {player.losses} | Ties: {player.ties}
              </Typography>
            </Box>
          ))}
        </Box>
      ) : (
        <Typography variant="body2">No scores available.</Typography>
      )}
    </Card>
  );
}

export default Scores;
