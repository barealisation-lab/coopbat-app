import React from "react";
import { Paper, Stack, Typography, Button } from "@mui/material";
import { useNavigate } from "react-router-dom";

export default function AfterSend() {
  const nav = useNavigate();
  return (
    <Paper sx={{ p: 3 }}>
      <Stack spacing={2} alignItems="center">
        <Typography variant="h5">Demande envoyée ✅</Typography>
        <Typography color="text.secondary" align="center">
          Vous pouvez aller plus loin pour un chiffrage détaillé.
        </Typography>
        <Button variant="contained" onClick={() => nav("/advanced")}>Aller plus loin</Button>
      </Stack>
    </Paper>
  );
}
