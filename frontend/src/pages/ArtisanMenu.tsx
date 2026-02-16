import React, { useEffect, useState } from "react";
import {
  Paper, Stack, Typography, Button, Chip, Dialog, DialogTitle,
  DialogContent, DialogActions
} from "@mui/material";
import { api, artisanHeaders, getArtisanId, getArtisanToken, setArtisanToken, setArtisanId } from "../api";
import { useNavigate } from "react-router-dom";

type Item = {
  kind: string;
  id: number;
  date: string;
  work_type: string;
  surface: string;
  budget: string;
  email: string;
  commune: string;
  status: "new" | "in_progress";
};

export default function ArtisanMenu() {
  const nav = useNavigate();
  const [items, setItems] = useState<Item[]>([]);
  const [pick, setPick] = useState<Item | null>(null);

  async function refresh() {
    const artisan_id = getArtisanId();
    const token = getArtisanToken();
    if (!artisan_id || !token) return nav("/artisan");

    const r = await api.get(`/artisan/requests/${artisan_id}`, { headers: artisanHeaders() });
    setItems(r.data.items || []);
  }

  async function setStatus(status: "new" | "in_progress") {
    if (!pick) return;
    const artisan_id = getArtisanId();
    await api.post(
      `/artisan/requests/${artisan_id}/${pick.kind}/${pick.id}/status`,
      { status },
      { headers: artisanHeaders() }
    );
    setPick(null);
    refresh();
  }

  async function logout() {
    const artisan_id = getArtisanId();
    try {
      await api.post(`/artisan/logout/${artisan_id}`, {}, { headers: artisanHeaders() });
    } catch {}
    setArtisanToken("");
    setArtisanId(0);
    nav("/artisan");
  }

  useEffect(() => { refresh(); }, []);

  return (
    <Paper sx={{ p: 3 }}>
      <Stack spacing={2}>
        <Stack direction="row" justifyContent="space-between" alignItems="center">
          <Typography variant="h5">Menu Travaux (Artisan)</Typography>
          <Stack direction="row" spacing={1}>
            <Button onClick={refresh}>Rafraîchir</Button>
            <Button color="error" onClick={logout}>Déconnexion</Button>
          </Stack>
        </Stack>

        {items.map((it) => (
          <Paper
            key={`${it.kind}-${it.id}`}
            variant="outlined"
            sx={{ p: 2, cursor: "pointer" }}
            onClick={() => setPick(it)}
          >
            <Stack direction="row" spacing={1} alignItems="center" justifyContent="space-between">
              <Stack>
                <Typography variant="subtitle1">{it.work_type}</Typography>
                <Typography variant="body2" color="text.secondary">
                  {new Date(it.date).toLocaleString()} — {it.commune || "—"} — {it.email}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  m²: {it.surface || "—"} | budget: {it.budget || "—"}
                </Typography>
              </Stack>

              <Chip
                label={it.status === "in_progress" ? "en traitement" : "nouvelle"}
                color={it.status === "in_progress" ? "warning" : "default"}
              />
            </Stack>
          </Paper>
        ))}

        <Dialog open={!!pick} onClose={() => setPick(null)}>
          <DialogTitle>Traiter cette demande ?</DialogTitle>
          <DialogContent>
            <Typography variant="body2">
              {pick?.work_type} — {pick?.email} — {pick?.commune || "—"}
            </Typography>
          </DialogContent>
          <DialogActions>
            <Button onClick={() => setStatus("new")}>Ne pas traiter pour le moment</Button>
            <Button variant="contained" onClick={() => setStatus("in_progress")}>Traiter ce chantier</Button>
          </DialogActions>
        </Dialog>
      </Stack>
    </Paper>
  );
}
