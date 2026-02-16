import axios from "axios";
import { API_BASE } from "./config";

export const api = axios.create({
  baseURL: API_BASE,
  timeout: 15000
});

// Artisan token
export function setArtisanToken(token: string) {
  localStorage.setItem("artisan_token", token);
}

export function getArtisanToken(): string {
  return localStorage.getItem("artisan_token") || "";
}

export function setArtisanId(id: number) {
  localStorage.setItem("artisan_id", String(id));
}
export function getArtisanId(): number {
  const v = localStorage.getItem("artisan_id");
  return v ? Number(v) : 0;
}

// Simple helper to add headers per-request
export function artisanHeaders() {
  const t = getArtisanToken();
  return t ? { "X-ARTISAN-TOKEN": t } : {};
}
