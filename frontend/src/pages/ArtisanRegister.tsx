import React, { useState } from "react";
import { Paper, Stack, Typography, TextField, Button } from "@mui/material";
import { useNavigate } from "react-router-dom";
import { api } from "../api";

export default function ArtisanRegister() {
  const nav = useNavigate();
  const [contact_name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [commune, setCommune] = useState("");
  const [radius_km, setRadius] = useState("30");
  const [phone, setPhone] = useState("");
  const [zone_note, setZoneNote] = useState("");
  const [password, setPassword] = useState("");

  async function register() {
    await api.post("/artisan/register", {
      contact_name, email, password, commune,
      radius_km: Number(radius_km || 30),
      phone, zone_note
    });
    nav("/artisan");
  }

  return (
    <Paper sx={{ p: 3 }}>
      <Stack spacing={2}>
        <Typography variant="h5">Créer compte artisan</Typography>
        <TextField label="Nom / Société *" value={contact_name} onChange={e => setName(e.target.value)} />
        <TextField label="Email *" value={email} onChange={e => setEmail(e.target.value)} />
        <TextField label="Commune *" value={commune} onChange={e => setCommune(e.target.value)} />
        <TextField label="Zone intervention (km)" value={radius_km} onChange={e => setRadius(e.target.value)} />
        <TextField label="Téléphone" value={phone} onChange={e => setPhone(e.target.value)} />
        <TextField label="Zone (note)" value={zone_note} onChange={e => setZoneNote(e.target.value)} />
        <TextField label="Mot de passe *" type="password" value={password} onChange={e => setPassword(e.target.value)} />
        <Button variant="contained" onClick={register}>Créer</Button>
      </Stack>
    </Paper>
  );
}
