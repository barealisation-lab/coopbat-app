import React, { useState } from "react";
import { Paper, Stack, Typography, TextField, Button } from "@mui/material";
import { api } from "../api";

export default function Advanced() {
  const [name, setName] = useState("");
  const [commune, setCommune] = useState("");
  const [email, setEmail] = useState("");
  const [payload, setPayload] = useState("{}");

  async function send() {
    const parsed = JSON.parse(payload || "{}");
    await api.post("/advanced", {
      contact_name: name,
      contact_commune: commune,
      contact_email: email,
      payload: parsed
    });
    alert("Demande chiffrage détaillé envoyée ✅");
  }

  return (
    <Paper sx={{ p: 3 }}>
      <Stack spacing={2}>
        <Typography variant="h5">Chiffrage détaillé</Typography>
        <Typography color="text.secondary">
          (Structure prête : tu rempliras ensuite les champs liés à tes feuilles Excel.)
        </Typography>

        <TextField label="Nom *" value={name} onChange={e => setName(e.target.value)} />
        <TextField label="Commune *" value={commune} onChange={e => setCommune(e.target.value)} />
        <TextField label="Email *" value={email} onChange={e => setEmail(e.target.value)} />
        <TextField
          label="Payload JSON (temporaire)"
          value={payload}
          onChange={e => setPayload(e.target.value)}
          multiline
          minRows={6}
        />

        <Button variant="contained" onClick={send}>Demander mon chiffrage</Button>
      </Stack>
    </Paper>
  );
}
