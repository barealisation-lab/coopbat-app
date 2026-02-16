import React from "react";
import { useRegisterSW } from "virtual:pwa-register/react";
import { Snackbar, Button } from "@mui/material";

export default function PwaUpdater() {
  const {
    needRefresh: [needRefresh],
    updateServiceWorker,
  } = useRegisterSW();

  return (
    <Snackbar
      open={needRefresh}
      message="Mise à jour disponible"
      action={
        <Button color="inherit" size="small" onClick={() => updateServiceWorker(true)}>
          Mettre à jour
        </Button>
      }
    />
  );
}
