// src/components/ErrorBoundary.js

import React from "react";
import { Typography, Box } from "@mui/material";

class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false };
  }

  static getDerivedStateFromError(error) {
    return { hasError: true };
  }

  componentDidCatch(error, info) {
    console.error("ErrorBoundary caught an error:", error, info);
    // You can also log the error to an error reporting service
  }

  render() {
    if (this.state.hasError) {
      return (
        <Box textAlign="center" mt={5}>
          <Typography variant="h4" color="error" gutterBottom>
            Something went wrong.
          </Typography>
          <Typography variant="body1">
            Please refresh the page or try again later.
          </Typography>
        </Box>
      );
    }

    return this.props.children;
  }
}

export default ErrorBoundary;
