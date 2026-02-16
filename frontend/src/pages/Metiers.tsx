import React from "react";
import { Grid, Card, CardContent, CardMedia, Typography, CardActionArea } from "@mui/material";
import { useNavigate } from "react-router-dom";

const cards = [
  { title: "Lot Charpente / Couverture / Zinguerie", desc: "Chiffrage complet (une seule demande)", img: "https://via.placeholder.com/900x500", to: "/chiffrage-lot" },
  { title: "Lot Charpente", desc: "Rénovation • Extension • Sur-élévation", img: "https://via.placeholder.com/900x500", to: "/chiffrage-lot" },
  { title: "Lot Couverture", desc: "Toiture • Isolation • Sarking", img: "https://via.placeholder.com/900x500", to: "/chiffrage-lot" },
  { title: "Lot Zinguerie", desc: "Gouttières • Habillages • Solins • Noues", img: "https://via.placeholder.com/900x500", to: "/chiffrage-lot" },
];

export default function Metiers() {
  const nav = useNavigate();
  return (
    <>
      <Typography variant="h5" sx={{ mb: 2 }}>Nos métiers</Typography>
      <Grid container spacing={2}>
        {cards.map((c, i) => (
          <Grid item xs={12} md={6} key={i}>
            <Card>
              <CardActionArea onClick={() => nav(c.to)}>
                <CardMedia component="img" height="200" image={c.img} />
                <CardContent>
                  <Typography variant="h6">{c.title}</Typography>
                  <Typography variant="body2" color="text.secondary">{c.desc}</Typography>
                </CardContent>
              </CardActionArea>
            </Card>
          </Grid>
        ))}
      </Grid>
    </>
  );
}
