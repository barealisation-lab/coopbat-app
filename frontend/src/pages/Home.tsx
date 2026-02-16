import React from "react";
import { Stack, Typography, Button, Paper } from "@mui/material";
import { useNavigate } from "react-router-dom";

export default function Home() {
  const nav = useNavigate();
  return (
    <Paper sx={{ p: 3 }}>
      <Stack spacing={2} alignItems="center">
        <Typography variant="h4" align="center">Bienvenue sur Coop'Bat</Typography>
        <Typography align="center">
          Association / Coopérative du Bâtiment<br />
          Acteurs solidaires du secteur
        </Typography>
        <Typography align="center">
          Nos actions : mise en relation, optimisation des chantiers,<br />
          partage des volumes de travail...
        </Typography>

        <Stack spacing={1} sx={{ width: "100%", maxWidth: 360 }}>
          <Button variant="contained" onClick={() => nav("/decouvrir")}>Nous découvrir</Button>
          <Button variant="contained" onClick={() => nav("/metiers")}>Faire estimer ses travaux</Button>
          <Button variant="outlined" onClick={() => nav("/artisan")}>Compte artisan</Button>
        </Stack>
      </Stack>
    </Paper>
  );
}
