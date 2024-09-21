// src/components/GameTester/Prompt.js

import React from "react";
import { Typography, Card, CardContent } from "@mui/material";

function Prompt({ prompt }) {
  return (
    <Card variant="outlined" sx={{ padding: 2 }}>
      <CardContent>
        <Typography variant="h6" align="center">
          {prompt ? `Current Prompt: ${prompt}` : "Waiting for prompt..."}
        </Typography>
      </CardContent>
    </Card>
  );
}

export default Prompt;
