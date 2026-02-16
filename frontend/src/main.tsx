import React from "react";
import ReactDOM from "react-dom/client";
import { BrowserRouter } from "react-router-dom";
import App from "./App";
import { CssBaseline } from "@mui/material";
import { registerSW } from "virtual:pwa-register";
ReactDOM.createRoot(document.getElementById("root")!).render(
  <React.StrictMode>
    <BrowserRouter>
      <CssBaseline />
      <App />
    </BrowserRouter>
  </React.StrictMode>
);

registerSW({
  onNeedRefresh() {
    // rien ici, ton PwaUpdater gère déjà l'UI
  },
  onOfflineReady() {
    // optionnel
  },
});
