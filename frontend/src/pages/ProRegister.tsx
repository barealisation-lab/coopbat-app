import React, { useState } from "react";
import { Paper, Stack, Typography, TextField, Button, Alert } from "@mui/material";
import { useNavigate } from "react-router-dom";
import axios from "axios";
import { API_BASE } from "../config";

export default function ProRegister() {
  const nav = useNavigate();

  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");

  const [error, setError] = useState("");
  const [ok, setOk] = useState("");

  async function register() {
    setError("");
    setOk("");
    try {
      await axios.post(`${API_BASE}/register`, {
        name,
        email,
        password,
      });

      setOk("Compte créé ✅ Vous pouvez vous connecter.");
      // petite redirection automatique vers /login
      setTimeout(() => nav("/login"), 800);
    } catch (e: any) {
      setError(
        e?.response?.data?.detail ||
        "Erreur à l'inscription, vérifiez les champs"
      );
    }
  }

  return (
    <Paper sx={{ p: 3, maxWidth: 420, mx: "auto" }}>
      <Stack spacing={2}>
        <Typography variant="h5" align="center">
          Inscription PRO
        </Typography>

        {error && <Alert severity="error">{error}</Alert>}
        {ok && <Alert severity="success">{ok}</Alert>}

        <TextField
          label="Nom / Société"
          value={name}
          onChange={(e) => setName(e.target.value)}
          fullWidth
        />

        <TextField
          label="Email"
          type="email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          fullWidth
        />

        <TextField
          label="Mot de passe"
          type="password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          fullWidth
        />

        <Button
          variant="contained"
          size="large"
          onClick={register}
          disabled={!name || !email || !password}
        >
          Créer mon compte
        </Button>

        <Button variant="text" onClick={() => nav("/login")}>
          J’ai déjà un compte
        </Button>
      </Stack>
    </Paper>
  );
}
