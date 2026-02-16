import React, { useState } from "react";
import { Paper, Stack, Typography, TextField, Button } from "@mui/material";
import { useNavigate } from "react-router-dom";
import { api, setArtisanToken, setArtisanId } from "../api";

export default function ArtisanLogin() {
  const nav = useNavigate();
  const [email, setEmail] = useState("");
  const [pw, setPw] = useState("");

  async function login() {
    const r = await api.post("/artisan/login", { email, password: pw });
    setArtisanToken(r.data.artisan_token);
    setArtisanId(r.data.artisan_id);
    nav("/artisan/menu");
  }

  return (
    <Paper sx={{ p: 3 }}>
      <Stack spacing={2}>
        <Typography variant="h5">Compte artisan</Typography>
        <TextField label="Email" value={email} onChange={e => setEmail(e.target.value)} />
        <TextField label="Mot de passe" type="password" value={pw} onChange={e => setPw(e.target.value)} />
        <Button variant="contained" onClick={login}>Se connecter</Button>
        <Button variant="outlined" onClick={() => nav("/artisan/register")}>Créer un compte artisan</Button>
      </Stack>
    </Paper>
  );
}
