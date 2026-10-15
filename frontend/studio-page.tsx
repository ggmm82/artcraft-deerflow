"use client";

import Link from "next/link";
import { useEffect, useState } from "react";

export default function StudioPage() {
  const [access, setAccess] = useState("loading");
  useEffect(() => {
    const controller = new AbortController();
    void fetch("/studio/api/catalog", { signal: controller.signal, credentials: "same-origin" })
      .then((response) => {
        if (!controller.signal.aborted) setAccess(response.ok ? "admin" : response.status === 403 ? "user" : "error");
      })
      .catch(() => { if (!controller.signal.aborted) setAccess("error"); });
    return () => controller.abort();
  }, []);
  if (access === "admin") return <iframe title="ArtCraft Studio" src="/studio/" style={{ width: "100%", height: "calc(100vh - 64px)", border: 0 }} />;
  return <section className="space-y-4 p-6">
    <h1 className="text-xl font-semibold">La tua squadra</h1>
    <p>{access === "loading" ? "Verifica dell’accesso…" : access === "user"
      ? "L’amministratore configura servizio, account e modello per tutti. Puoi usare la squadra dalla chat."
      : "Configurazione non raggiungibile. Ricarica la pagina per riprovare."}</p>
    {access !== "loading" && <Link className="underline" href="/workspace/chats/new">Apri una nuova chat →</Link>}
  </section>;
}
