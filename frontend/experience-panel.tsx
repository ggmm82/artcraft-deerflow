"use client";
import { useEffect, useRef, useState } from "react";
import { fetch } from "@/core/api/fetcher";
import { getBackendBaseURL } from "@/core/config";

type Observation = { id: string; at: string; excluded: boolean; observation: {
  criterion: string; status: string; method: string; evidence: string; corrections: string[];
  tools: Record<string, string>; product_sha256: string; report_sha256: string; source_thread?: string; producer_method?: { status: string; notice: string; declared_method?: { approach: string; steps: string[]; limits: string[] } }; limitations?: string[];
} };
type Lesson = { id: string; accepted: boolean; excluded: boolean; basis: { source_ids: string[]; source_statuses?: string[]; lesson: { title: string; applies_when: string; procedure: string[]; verification: string[]; limits: string; tools: string[] } } };
type Library = { total: number; excluded: number; pending?: number; lessons?: Lesson[]; observations: Observation[] };
export function ExperiencePanel({ threadId, deliveries = [] }: { threadId: string; deliveries?: { id: string; title: string; purpose: string }[] }) {
  const [library, setLibrary] = useState<Library | null>(null);
  const [error, setError] = useState("");
  const [delivery, setDelivery] = useState(deliveries.find(d => d.purpose !== "review")?.id ?? "");
  const [note, setNote] = useState("");
  const [busy, setBusy] = useState(false);
  const alive = useRef(false);
  const base = `${getBackendBaseURL()}/api/threads/${encodeURIComponent(threadId)}/studio-experience`;
  useEffect(() => {
    alive.current = true;
    const controller = new AbortController();
    void fetch(base, { signal: controller.signal, cache: "no-store" }).then(async response => {
      if (!response.ok) throw new Error();
      const data = await response.json() as Library;
      if (!controller.signal.aborted) setLibrary(data);
    }).catch(() => { if (!controller.signal.aborted) setError("Archivio non disponibile: nessuna esperienza è stata cancellata."); });
    return () => { alive.current = false; controller.abort(); };
  }, [base]);
  async function change(path: string, body?: object) {
    setBusy(true); setError("");
    try {
      const response = await fetch(base + path, { method: path === "/prefer" || !body ? "POST" : "PUT", headers: { "Content-Type": "application/json" }, ...(body ? { body: JSON.stringify(body) } : {}) });
      if (!response.ok) throw new Error();
      const data = await response.json() as Library;
      if (alive.current) setLibrary(data);
    } catch { if (alive.current) setError("Modifica non confermata. Riapri la scheda per verificare."); }
    finally { if (alive.current) setBusy(false); }
  }
  async function download() {
    setError("");
    try {
      const response = await fetch(base + "?export=true", { cache: "no-store" });
      if (!response.ok) throw new Error();
      const url = URL.createObjectURL(new Blob([JSON.stringify(await response.json(), null, 2)], { type: "application/json" }));
      const link = document.createElement("a"); link.href = url; link.download = "artcraft-esperienza.json"; link.click();
      setTimeout(() => URL.revokeObjectURL(url), 1000);
    } catch { if (alive.current) setError("Esportazione non riuscita. Le esperienze restano nell’archivio."); }
  }
  return <div className="space-y-3 text-sm" data-testid="experience-panel">
    <p>Solo le lezioni che accetti singolarmente entrano nelle skills. Le altre restano proposte. Le evidenze del singolo progetto restano separate.</p>
    {library && <p>{library.lessons?.filter(lesson => !lesson.accepted).length ?? 0} proposte da valutare · {library.lessons?.filter(lesson => lesson.accepted).length ?? 0} lezioni accettate</p>}
    {library?.lessons?.map(record => <article key={record.id} className="space-y-3 rounded-xl border p-4" data-testid="general-lesson">
      <h4 className="font-semibold">{record.basis.lesson.title}</h4>
      <p className="text-xs">{record.accepted ? "Accettata per il riutilizzo" : "Proposta: non ancora usata nelle skills"}</p>
      <p><strong>Quando usarla:</strong> {record.basis.lesson.applies_when}</p>
      <details><summary className="cursor-pointer">Procedura e verifiche</summary>
        <ol className="my-2 list-inside list-decimal">{record.basis.lesson.procedure.map((step, i) => <li key={i}>{step}</li>)}</ol>
        <ul className="list-inside list-disc">{record.basis.lesson.verification.map((step, i) => <li key={i}>{step}</li>)}</ul>
      </details>
      <p className="text-muted-foreground"><strong>Limiti:</strong> {record.basis.lesson.limits}</p>
      <p className="text-xs">{record.basis.source_ids.length} fonti · {record.basis.source_statuses?.includes("preferred_by_user") ? "Include una preferenza dell’utente, non un collaudo tecnico." : "Generalizzazione delle osservazioni conservate, da verificare nel nuovo progetto."}</p>
      <button className="rounded border px-3 py-2 disabled:opacity-50" disabled={busy} onClick={() => void change("/lesson", { id: record.id, accepted: !record.accepted })}>{record.accepted ? "Rimuovi dalle skills" : "Accetta questa lezione"}</button>
    </article>)}
    {library && !library.lessons?.length && <p>Nessuna lezione generale ancora compilata. Le fonti già conservate non vengono copiate nelle nuove skills.</p>}
    <details className="space-y-3 rounded-xl border p-3"><summary className="cursor-pointer font-medium">Fonti, preferenze e archivio ({library?.total ?? 0})</summary>
    <div className="flex flex-wrap gap-2">
      <button className="rounded border px-3 py-2 disabled:opacity-50" disabled={busy} onClick={() => void change("/collect")}>Recupera esperienza di questa chat</button>
      <button className="rounded border px-3 py-2" disabled={!library} onClick={() => void download()}>Esporta esperienza</button>
    </div>
    <div className="space-y-2 rounded border p-3">
      <p className="font-medium">Conserva un metodo che ti ha soddisfatto</p>
      <label className="block">Lavorazione<select className="w-full rounded border p-2" value={delivery} onChange={event => setDelivery(event.target.value)}>{deliveries.filter(d => d.purpose !== "review").map(d => <option key={d.id} value={d.id}>{d.title || d.id}</option>)}</select></label>
      <label className="block">Cosa vuoi riutilizzare?<textarea className="w-full rounded border p-2" maxLength={2000} value={note} onChange={event => setNote(event.target.value)} placeholder="Ad esempio: cambiare metodo dopo il campione, conservare la struttura valida, verificare due casi diversi." /></label>
      <button className="rounded border px-3 py-2 disabled:opacity-50" disabled={busy || !delivery || note.trim().length < 5} onClick={() => void change("/prefer", { delivery_id: delivery, note })}>Conserva questo metodo</button>
      <p className="text-xs text-muted-foreground">Conserva una fonte per la successiva generalizzazione del coordinatore. Non entra direttamente nelle skills.</p>
    </div>
    {error && <p role="alert">{error}</p>}
    {library?.total === 0 && <p>Nessuna revisione utilizzabile ancora registrata. I soli comandi riusciti non diventano buone pratiche.</p>}
    {library?.observations.map(record => <article className="space-y-2 rounded border p-3" key={record.id}>
      <p className="font-medium">{record.observation.criterion}</p>
      <p>{record.observation.status === "preferred_by_user" ? "Metodo preferito dall’utente" : record.observation.status === "passed" ? "Esito positivo osservato" : "Difetto osservato"} · {record.observation.method} · {record.excluded ? "Esclusa" : "Fonte conservata, separata dalle skills"}</p>
      <p>{record.observation.evidence}</p>
      {record.observation.producer_method && <details><summary>Procedimento conservato</summary><p>{record.observation.producer_method.notice}</p><p>{record.observation.producer_method.declared_method?.approach}</p><ol className="list-inside list-decimal">{record.observation.producer_method.declared_method?.steps.map((step, i) => <li key={i}>{step}</li>)}</ol></details>}
      {record.observation.limitations?.map((limit, i) => <p key={i}>Limite conservato: {limit}</p>)}
      {record.observation.corrections.map((action, i) => <p key={i}>Correzione proposta: {action}</p>)}
      <p>Strumenti: {Object.entries(record.observation.tools).map(([tool, version]) => `${tool} ${version}`).join(", ") || "Workspace generale"}</p>
      {record.observation.source_thread && <a className="underline" href={`/workspace/chats/${encodeURIComponent(record.observation.source_thread)}`}>Apri il progetto di origine</a>}
      <details><summary>Provenienza e versioni</summary><p className="break-all">Prodotto SHA256: {record.observation.product_sha256}</p><p className="break-all">Rapporto SHA256: {record.observation.report_sha256}</p></details>

    </article>)}
    </details>
  </div>;
}
