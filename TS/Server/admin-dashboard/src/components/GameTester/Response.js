// src/components/GameTester/Response.js

import React from "react";
import { Button, ButtonGroup, Typography, Box } from "@mui/material";

function Response({ disabled, onSubmit, countdown, gameType }) {
  const gestures = {
    rps: ["Rock", "Paper", "Scissors"],
    counting: ["1", "2", "3", "4", "5"],
  };

  const currentGestures = gestures[gameType] || [];

  return (
    <Box>
      <Typography variant="subtitle1" align="center" gutterBottom>
        {disabled ? "Respond Now!" : "Awaiting Response..."}
      </Typography>
      <ButtonGroup
        variant="contained"
        color="primary"
        disabled={disabled} // Correct logic: disabled when not prompting
        sx={{
          display: "flex",
          justifyContent: "center",
          marginTop: 2,
        }}
      >
        {currentGestures.map((gesture, index) => (
          <Button
            key={index}
            onClick={() => onSubmit(gesture)}
            sx={{ margin: 1 }}
          >
            {gesture}
          </Button>
        ))}
      </ButtonGroup>
    </Box>
  );
}

export default Response;
