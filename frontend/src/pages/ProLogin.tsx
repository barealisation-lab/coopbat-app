import React, { useState } from "react";
import { Paper, Stack, Typography, TextField, Button, Alert } from "@mui/material";
import { useNavigate } from "react-router-dom";
import axios from "axios";
import { API_BASE } from "../config";

export default function ProLogin() {
  const nav = useNavigate();

  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");

  async function login() {
    setError("");
    try {
      const res = await axios.post(`${API_BASE}/login`, {
        email,
        password,
      });

      // 🔐 Stockage simple (si tu veux aller plus loin ensuite)
      localStorage.setItem("pro_user", JSON.stringify(res.data));

      // ➜ redirection vers les métiers
      nav("/metiers");
    } catch (e: any) {
      setError(
        e?.response?.data?.detail ||
        "Erreur de connexion, vérifiez vos identifiants"
      );
    }
  }

  return (
    <Paper sx={{ p: 3, maxWidth: 420, mx: "auto" }}>
      <Stack spacing={2}>
        <Typography variant="h5" align="center">
          Connexion PRO
        </Typography>

        {error && <Alert severity="error">{error}</Alert>}

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
          onClick={login}
          disabled={!email || !password}
        >
          Se connecter
        </Button>

        <Button
          variant="text"
          onClick={() => nav("/register")}
        >
          Créer un compte
        </Button>
      </Stack>
    </Paper>
  );
}
