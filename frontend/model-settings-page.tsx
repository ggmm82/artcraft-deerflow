"use client";

import Link from "next/link";

import { setSettingsDialogOpen } from "./settings-dialog-store";

export function ModelSettingsPage() {
  return (
    <section className="space-y-4 p-4">
      <h2 className="text-lg font-semibold">Un solo modello per la squadra</h2>
      <p>
        Servizio, account e modello si configurano in ArtCraft Studio. Le
        impostazioni valgono per il coordinatore e tutti gli specialisti.
      </p>
      <Link
        onClick={() => setSettingsDialogOpen(false)}
        className="inline-block rounded-md bg-primary px-4 py-2 text-primary-foreground"
        href="/workspace/studio"
      >
        Configura la squadra →
      </Link>
    </section>
  );
}
