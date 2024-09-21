// src/components/AdminDashBoard/GameStats.js

import React from "react";
import {
  Card,
  CardContent,
  Typography,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
} from "@mui/material";

function GameStats({ clientCount, clients, playerScores }) {
  return (
    <Card>
      <CardContent>
        <Typography variant="h5" gutterBottom>
          Game Statistics
        </Typography>
        <Typography variant="body1" gutterBottom>
          <strong>Connected Clients:</strong> {clientCount}
        </Typography>

        {/* Clients Section */}
        <Typography variant="h6" gutterBottom style={{ marginTop: "20px" }}>
          Clients:
        </Typography>
        <TableContainer component={Paper}>
          <Table size="small" aria-label="clients table">
            <TableHead>
              <TableRow>
                <TableCell>Player ID</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {clients.length > 0 ? (
                clients.map((client, index) => (
                  <TableRow key={index}>
                    <TableCell component="th" scope="row">
                      {client.player_id}
                    </TableCell>
                  </TableRow>
                ))
              ) : (
                <TableRow>
                  <TableCell colSpan={1} align="center">
                    No players connected.
                  </TableCell>
                </TableRow>
              )}
            </TableBody>
          </Table>
        </TableContainer>

        {/* Player Scores Section */}
        <Typography variant="h6" gutterBottom style={{ marginTop: "20px" }}>
          Player Scores:
        </Typography>
        <TableContainer component={Paper}>
          <Table size="small" aria-label="player scores table">
            <TableHead>
              <TableRow>
                <TableCell>Player ID</TableCell>
                <TableCell align="right">Score</TableCell>
                <TableCell align="right">Wins</TableCell>
                <TableCell align="right">Losses</TableCell>
                <TableCell align="right">Ties</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {playerScores.length > 0 ? (
                playerScores.map((player, index) => (
                  <TableRow key={index}>
                    <TableCell component="th" scope="row">
                      {player.player_id}
                    </TableCell>
                    <TableCell align="right">{player.score}</TableCell>
                    <TableCell align="right">{player.wins}</TableCell>
                    <TableCell align="right">{player.losses}</TableCell>
                    <TableCell align="right">{player.ties}</TableCell>
                  </TableRow>
                ))
              ) : (
                <TableRow>
                  <TableCell colSpan={5} align="center">
                    No player scores available.
                  </TableCell>
                </TableRow>
              )}
            </TableBody>
          </Table>
        </TableContainer>
      </CardContent>
    </Card>
  );
}

export default GameStats;
