// src/components/GameTester/PlayerList.js

import React from "react";
import { Typography, List, ListItem, ListItemText, Card, CardContent } from "@mui/material";

function PlayerList({ players }) {
  return (
    <Card variant="outlined" sx={{ padding: 2 }}>
      <CardContent>
        <Typography variant="h6" gutterBottom>
          Connected Players
        </Typography>
        {players.length > 0 ? (
          <List>
            {players.map((player, index) => (
              <ListItem key={index}>
                <ListItemText primary={player.player_id} />
              </ListItem>
            ))}
          </List>
        ) : (
          <Typography variant="body2">No players connected.</Typography>
        )}
      </CardContent>
    </Card>
  );
}

export default PlayerList;
