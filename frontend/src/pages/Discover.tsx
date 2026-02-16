import React from "react";
import { Grid, Card, CardContent, CardMedia, Typography, CardActions, Button } from "@mui/material";

type ArtisanCard = {
  name: string;
  job: string;
  phone: string;
  email: string;
  zone: string;
  img: string; // URL image
};

const demo: ArtisanCard[] = [
  { name: "Artisan 1", job: "Couverture", phone: "06 00 00 00 00", email: "artisan1@mail.fr", zone: "30 km autour de ...", img: "https://via.placeholder.com/800x450" },
  { name: "Artisan 2", job: "Zinguerie", phone: "06 00 00 00 00", email: "artisan2@mail.fr", zone: "40 km autour de ...", img: "https://via.placeholder.com/800x450" },
  { name: "Artisan 3", job: "Charpente", phone: "06 00 00 00 00", email: "artisan3@mail.fr", zone: "25 km autour de ...", img: "https://via.placeholder.com/800x450" },
  { name: "Artisan 4", job: "Lot complet", phone: "06 00 00 00 00", email: "artisan4@mail.fr", zone: "50 km autour de ...", img: "https://via.placeholder.com/800x450" },
];

export default function Discover() {
  return (
    <>
      <Typography variant="h5" sx={{ mb: 2 }}>Nous les artisans</Typography>
      <Grid container spacing={2}>
        {demo.map((a, i) => (
          <Grid item xs={12} sm={6} md={3} key={i}>
            <Card>
              <CardMedia component="img" height="160" image={a.img} />
              <CardContent>
                <Typography variant="h6">{a.name} — {a.job}</Typography>
                <Typography variant="body2" color="text.secondary">
                  Tel: {a.phone}<br />
                  Mail: {a.email}<br />
                  Zone: {a.zone}
                </Typography>
              </CardContent>
              <CardActions>
                <Button size="small" href={`mailto:${a.email}`}>Email</Button>
                <Button size="small" href={`tel:${a.phone.replaceAll(" ", "")}`}>Appeler</Button>
              </CardActions>
            </Card>
          </Grid>
        ))}
      </Grid>
    </>
  );
}
