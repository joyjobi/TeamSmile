// src/components/AdminDashBoard/ControlPanel.js

import React from "react";
import { SocketContext } from "../../contexts/SocketContext"; // Adjust the import path as necessary

function ControlPanel({ gameType, setGameType }) {
  const socket = React.useContext(SocketContext); // Access socket via context
  const [promptInterval, setPromptInterval] = React.useState(3000);
  const [responseTimeout, setResponseTimeout] = React.useState(7000);

  const handleSetGameType = () => {
    if (socket) {
      console.log(`Setting game type to ${gameType}`);
      socket.emit("admin_set_game_type", { gameType });
    }
  };

  const handleStartGame = () => {
    if (socket) {
      console.log("Emitting 'admin_start_game' event.");
      socket.emit("admin_start_game");
    }
  };

  const handleResetGame = () => {
    if (socket) {
      console.log("Emitting 'admin_reset_game' event.");
      socket.emit("admin_reset_game");
    }
  };

  const handleUpdateConfig = () => {
    if (socket) {
      console.log("Emitting 'admin_update_config' event with data:", {
        promptInterval: parseInt(promptInterval),
        responseTimeout: parseInt(responseTimeout),
      });
      socket.emit("admin_update_config", {
        promptInterval: parseInt(promptInterval),
        responseTimeout: parseInt(responseTimeout),
      });
    }
  };

  return (
    <div id="controlPanel">
      <h2>Control Panel</h2>

      <div>
        <label htmlFor="gameSelect">Select Game Type:</label>
        <select
          id="gameSelect"
          value={gameType}
          onChange={(e) => setGameType(e.target.value)}
        >
          <option value="rps">Rock-Paper-Scissors</option>
          <option value="counting">Counting Game</option>
        </select>
        <button onClick={handleSetGameType}>Set Game Type</button>
      </div>

      <button onClick={handleStartGame}>Start Game</button>
      <button onClick={handleResetGame}>Reset Game</button>

      <div>
        <h3>
          Next Round Starts In: <span id="countdownTimer">N/A</span>
        </h3>
      </div>

      <div>
        <label htmlFor="promptIntervalInput">Prompt Interval (ms):</label>
        <input
          type="number"
          id="promptIntervalInput"
          value={promptInterval}
          onChange={(e) => setPromptInterval(e.target.value)}
        />
      </div>
      <div>
        <label htmlFor="responseTimeoutInput">Response Timeout (ms):</label>
        <input
          type="number"
          id="responseTimeoutInput"
          value={responseTimeout}
          onChange={(e) => setResponseTimeout(e.target.value)}
        />
      </div>
      <button onClick={handleUpdateConfig}>Update Configuration</button>
    </div>
  );
}

export default ControlPanel;
