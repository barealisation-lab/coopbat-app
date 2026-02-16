import React, { useMemo, useState } from "react";
import {
  Paper, Stack, Typography, TextField, MenuItem, Switch, FormControlLabel,
  Checkbox, Button, Divider
} from "@mui/material";
import { api } from "../api";
import { useNavigate } from "react-router-dom";

const TYPES = [
  "Tuile mécanique faible pente 25-35%",
  "Tuile mécanique forte pente 35-45%",
  "Ardoise",
  "Zinc",
  "Autre"
];

type ZLine = { key: string; label: string; unit: string; checked: boolean; qty: string };

export default function ChiffrageLot() {
  const nav = useNavigate();

  const [couvType, setCouvType] = useState(TYPES[0]);
  const [couvSurf, setCouvSurf] = useState("");
  const [isolation, setIsolation] = useState(false);
  const [sarking, setSarking] = useState(false);
  const [ecran, setEcran] = useState(true);

  const [zing, setZing] = useState<ZLine[]>([
    { key: "gouttieres_ml", label: "Gouttières", unit: "ml", checked: false, qty: "" },
    { key: "hab_rives_ml", label: "Habillage rives / frontons", unit: "ml", checked: false, qty: "" },
    { key: "hab_mur_m2", label: "Habillage mur", unit: "m²", checked: false, qty: "" },
    { key: "couv_zinc_m2", label: "Couverture zinc", unit: "m²", checked: false, qty: "" },
    { key: "tour_chem_u", label: "Tour de cheminée", unit: "u", checked: false, qty: "" },
    { key: "couloir_ml", label: "Couloir", unit: "ml", checked: false, qty: "" },
    { key: "solins_ml", label: "Solins", unit: "ml", checked: false, qty: "" },
    { key: "descentes_ml", label: "Descentes", unit: "ml", checked: false, qty: "" },
  ]);

  const [charp, setCharp] = useState({
    reno: false, ext: false, surel: false, newp: false, other: false
  });
  const [charpSurf, setCharpSurf] = useState("");

  const [name, setName] = useState("");
  const [commune, setCommune] = useState("");
  const [email, setEmail] = useState("");
  const [msg, setMsg] = useState("");

  const canSend = useMemo(() => {
    return !!couvSurf && !!name && !!commune && !!email && !!charpSurf;
  }, [couvSurf, name, commune, email, charpSurf]);

  async function send() {
    if (!canSend) return;

    const zinguerie = zing
      .filter(z => z.checked && z.qty.trim() !== "")
      .map(z => ({ key: z.key, label: z.label, unit: z.unit, qty: z.qty }));

    const charpente = Object.entries(charp)
      .filter(([, v]) => v)
      .map(([k]) => k);

    const payload = {
      couverture_type: couvType,
      couverture_surface_m2: couvSurf,
      couverture_isolation: isolation,
      couverture_sarking: sarking,
      couverture_ecran: ecran,
      zinguerie,
      charpente,
      contact_name: name,
      contact_commune: commune,
      contact_email: email,
      contact_message: msg
    };

    const r = await api.post("/lead", payload);
    if (r.data?.id) nav("/after-send");
  }

  return (
    <Paper sx={{ p: 3 }}>
      <Stack spacing={2}>
        <Typography variant="h5">Chiffrage lot complet</Typography>

        <Typography variant="h6">Couverture</Typography>
        <TextField select label="Type de couverture" value={couvType} onChange={e => setCouvType(e.target.value)}>
          {TYPES.map(t => <MenuItem key={t} value={t}>{t}</MenuItem>)}
        </TextField>
        <TextField label="Surface couverture (m²) *" value={couvSurf} onChange={e => setCouvSurf(e.target.value)} />
        <Stack direction="row" spacing={2}>
          <FormControlLabel control={<Switch checked={isolation} onChange={e => setIsolation(e.target.checked)} />} label="Isolation" />
          <FormControlLabel control={<Switch checked={sarking} onChange={e => setSarking(e.target.checked)} />} label="Sarking" />
          <FormControlLabel control={<Switch checked={ecran} onChange={e => setEcran(e.target.checked)} />} label="Écran sous-toiture" />
        </Stack>

        <Divider />

        <Typography variant="h6">Zinguerie</Typography>
        {zing.map((z, idx) => (
          <Stack key={z.key} direction="row" spacing={2} alignItems="center">
            <Checkbox
              checked={z.checked}
              onChange={e => {
                const next = [...zing];
                next[idx] = { ...z, checked: e.target.checked };
                setZing(next);
              }}
            />
            <Typography sx={{ width: 240 }}>{z.label} ({z.unit})</Typography>
            <TextField
              size="small"
              label={z.unit}
              value={z.qty}
              onChange={e => {
                const next = [...zing];
                next[idx] = { ...z, qty: e.target.value };
                setZing(next);
              }}
            />
          </Stack>
        ))}

        <Divider />

        <Typography variant="h6">Charpente</Typography>
        <TextField label="Surface charpente (m²) *" value={charpSurf} onChange={e => setCharpSurf(e.target.value)} />
        <Stack direction="row" spacing={2} flexWrap="wrap">
          <FormControlLabel control={<Checkbox checked={charp.reno} onChange={e => setCharp({ ...charp, reno: e.target.checked })} />} label="Rénovation" />
          <FormControlLabel control={<Checkbox checked={charp.ext} onChange={e => setCharp({ ...charp, ext: e.target.checked })} />} label="Extension" />
          <FormControlLabel control={<Checkbox checked={charp.surel} onChange={e => setCharp({ ...charp, surel: e.target.checked })} />} label="Sur-élévation" />
          <FormControlLabel control={<Checkbox checked={charp.newp} onChange={e => setCharp({ ...charp, newp: e.target.checked })} />} label="Nouveau projet" />
          <FormControlLabel control={<Checkbox checked={charp.other} onChange={e => setCharp({ ...charp, other: e.target.checked })} />} label="Autre" />
        </Stack>

        <Divider />

        <Typography variant="h6">Vos coordonnées</Typography>
        <TextField label="Nom *" value={name} onChange={e => setName(e.target.value)} />
        <TextField label="Commune *" value={commune} onChange={e => setCommune(e.target.value)} />
        <TextField label="Email *" value={email} onChange={e => setEmail(e.target.value)} />
        <TextField label="Message" value={msg} onChange={e => setMsg(e.target.value)} multiline minRows={3} />

        <Button variant="contained" disabled={!canSend} onClick={send}>
          Envoyer ma demande
        </Button>
      </Stack>
    </Paper>
  );
}
