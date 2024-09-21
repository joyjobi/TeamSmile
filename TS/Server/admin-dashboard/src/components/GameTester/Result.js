// src/components/GameTester/Result.js

import React from "react";
import { Typography, Card, CardContent } from "@mui/material";

function Result({ result }) {
  return (
    <Card variant="outlined" sx={{ padding: 2 }}>
      <CardContent>
        <Typography variant="h6" align="center">
          {result ? `Your Result: ${result}` : "Awaiting results..."}
        </Typography>
      </CardContent>
    </Card>
  );
}

export default Result;
