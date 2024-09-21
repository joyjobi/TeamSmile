// src/components/AdminDashboard/CurrentPrompt.js

import React from "react";
import { Typography, Box } from "@mui/material";

function CurrentPrompt({ currentPrompt, timer }) {
  // Updated props
  return (
    <Box sx={{ padding: 2, backgroundColor: "#e3f2fd", borderRadius: 2 }}>
      <Typography variant="h6" gutterBottom>
        Current Prompt
      </Typography>
      <Typography variant="body1" gutterBottom>
        {currentPrompt}
      </Typography>
      {timer && (
        <Typography variant="subtitle1" color="textSecondary">
          Time Remaining: {timer}
        </Typography>
      )}
    </Box>
  );
}

export default CurrentPrompt;
