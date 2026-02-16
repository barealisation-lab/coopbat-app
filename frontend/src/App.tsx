import React from "react";
import { Routes, Route, Link, useNavigate } from "react-router-dom";
import {
  AppBar, Toolbar, Typography, Button, Container
} from "@mui/material";

import Home from "./pages/Home";
import Discover from "./pages/Discover";
import ProLogin from "./pages/ProLogin";
import ProRegister from "./pages/ProRegister";
import Metiers from "./pages/Metiers";
import ChiffrageLot from "./pages/ChiffrageLot";
import AfterSend from "./pages/AfterSend";
import Advanced from "./pages/Advanced";

import ArtisanLogin from "./pages/ArtisanLogin";
import ArtisanRegister from "./pages/ArtisanRegister";
import ArtisanMenu from "./pages/ArtisanMenu";
import PwaUpdater from "./PwaUpdater";
export default function App() {
  const nav = useNavigate();

  return (
    <>
      <AppBar position="sticky">
        <Toolbar>
          <Typography variant="h6" sx={{ flexGrow: 1 }}>
            Coop'Bat
          </Typography>
          <Button color="inherit" onClick={() => nav("/")}>Accueil</Button>
          <Button color="inherit" onClick={() => nav("/metiers")}>Nos métiers</Button>
          <Button color="inherit" onClick={() => nav("/artisan")}>Compte artisan</Button>
		  <Button color="inherit" onClick={() => nav("/login")}>Accès PRO</Button>

        </Toolbar>
      </AppBar>

      <Container sx={{ py: 3 }}>
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/decouvrir" element={<Discover />} />

          <Route path="/login" element={<ProLogin />} />
          <Route path="/register" element={<ProRegister />} />

          <Route path="/metiers" element={<Metiers />} />
          <Route path="/chiffrage-lot" element={<ChiffrageLot />} />
          <Route path="/after-send" element={<AfterSend />} />
          <Route path="/advanced" element={<Advanced />} />

          <Route path="/artisan" element={<ArtisanLogin />} />
          <Route path="/artisan/register" element={<ArtisanRegister />} />
          <Route path="/artisan/menu" element={<ArtisanMenu />} />

          <Route path="*" element={<div>Page introuvable</div>} />
        </Routes>
      </Container>
	  <PwaUpdater />
    </>
  );
}
