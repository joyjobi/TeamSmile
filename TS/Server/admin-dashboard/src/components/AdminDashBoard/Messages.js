// src/components/AdminDashboard/Messages.js

import React, { useEffect, useRef } from "react";
import { Typography, Box, Paper } from "@mui/material";

function Messages({ messages }) {
  const messagesEndRef = useRef(null);

  useEffect(() => {
    // Scroll to the bottom when messages change
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const getColorByType = (type) => {
    switch (type) {
      case "warning":
        return "orange";
      case "error":
        return "red";
      default:
        return "black";
    }
  };

  return (
    <Box sx={{ marginTop: 2 }}>
      <Typography variant="h6" gutterBottom>
        Admin Messages
      </Typography>
      <Paper
        elevation={3}
        sx={{
          padding: 2,
          maxHeight: 300, // Adjust as needed
          overflowY: "auto",
          backgroundColor: "#e8eaf6",
          borderRadius: 2,
        }}
      >
        <Typography
          variant="body2"
          sx={{ fontSize: "0.75rem", whiteSpace: "pre-wrap" }}
        >
          {messages.length > 0
            ? messages.map((msg, index) => (
                <div key={index} style={{ color: getColorByType(msg.type) }}>
                  <strong>{msg.timestamp}</strong>: {msg.message}
                </div>
              ))
            : "No messages."}
          <div ref={messagesEndRef} /> {/* Dummy div for auto-scrolling */}
        </Typography>
      </Paper>
    </Box>
  );
}

export default Messages;
