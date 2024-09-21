// src/components/AdminDashboard/CurrentPrompt.js

import React, { useEffect, useState } from "react";
import { Typography, Box } from "@mui/material";

function CurrentPrompt({ currentPrompt, nextRoundTime }) {
  const [timeRemaining, setTimeRemaining] = useState("");

  useEffect(() => {
    if (!nextRoundTime) {
      setTimeRemaining("");
      return;
    }

    const updateTimer = () => {
      const now = Date.now();
      const difference = nextRoundTime - now;

      if (difference <= 0) {
        setTimeRemaining("Time's up!");
        clearInterval(intervalId);
        return;
      }

      const seconds = Math.floor((difference / 1000) % 60);
      const minutes = Math.floor((difference / (1000 * 60)) % 60);
      const hours = Math.floor(difference / (1000 * 60 * 60));

      let timeString = "";
      if (hours > 0) timeString += `${hours}h `;
      if (minutes > 0) timeString += `${minutes}m `;
      timeString += `${seconds}s`;

      setTimeRemaining(timeString);
    };

    // Initial call
    updateTimer();

    // Update every second
    const intervalId = setInterval(updateTimer, 1000);

    // Cleanup on unmount or when nextRoundTime changes
    return () => clearInterval(intervalId);
  }, [nextRoundTime]);

  return (
    <Box sx={{ padding: 2, backgroundColor: "#e3f2fd", borderRadius: 2 }}>
      <Typography variant="h6" gutterBottom>
        Current Prompt
      </Typography>
      <Typography variant="body1" gutterBottom>
        {currentPrompt}
      </Typography>
      {timeRemaining && (
        <Typography variant="subtitle1" color="textSecondary">
          Time Remaining: {timeRemaining}
        </Typography>
      )}
    </Box>
  );
}

export default CurrentPrompt;
