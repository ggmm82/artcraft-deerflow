"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useEffect, useState } from "react";

export function TeamOnboarding() {
  const pathname = usePathname();
  const [failed, setFailed] = useState(false);

  useEffect(() => {
    if (pathname !== "/workspace/chats/new") return;
    const controller = new AbortController();
    void fetch("/studio/api/catalog", {
      signal: controller.signal,
      credentials: "same-origin",
    })
      .then(async (response) => {
        if (response.status === 403) return; // The administrator configures the shared team.
        if (!response.ok) throw new Error("Configurazione non disponibile");
        const data: { team?: { ready?: boolean } } = await response.json();
        if (typeof data.team?.ready !== "boolean") {
          throw new Error("Configurazione non disponibile");
        }
        if (!controller.signal.aborted && !data.team.ready) {
          window.location.replace("/workspace/studio");
        }
      })
      .catch(() => {
        if (!controller.signal.aborted) setFailed(true);
      });
    return () => controller.abort();
  }, [pathname]);

  if (!failed || pathname !== "/workspace/chats/new") return null;
  return (
    <Link
      className="mx-3 rounded-md border p-3 text-sm"
      href="/workspace/studio"
    >
      Non riesco a verificare la squadra. Apri la configurazione per riprovare.
    </Link>
  );
}
