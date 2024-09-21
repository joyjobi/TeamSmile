// src/index.js

import React from "react";
import ReactDOM from "react-dom";
import App from "./App";
import { SocketProvider } from "./contexts/SocketContext";
import ErrorBoundary from "./components/ErrorBoundary"; // Assuming you have this
import { ThemeProvider, createTheme } from "@mui/material/styles";
import CssBaseline from "@mui/material/CssBaseline";

const theme = createTheme({
  // Customize your theme here
  palette: {
    primary: {
      main: "#1976d2", // Default MUI primary color
    },
    secondary: {
      main: "#dc004e", // Default MUI secondary color
    },
  },
});

ReactDOM.render(
  <React.StrictMode>
    <ErrorBoundary>
      <ThemeProvider theme={theme}>
        <CssBaseline />
        <SocketProvider>
          <App />
        </SocketProvider>
      </ThemeProvider>
    </ErrorBoundary>
  </React.StrictMode>,
  document.getElementById("root")
);
