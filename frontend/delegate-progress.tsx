"use client";

import { useEffect, useRef, useState } from "react";
import { fetch } from "@/core/api/fetcher";
import { getBackendBaseURL } from "@/core/config";
import { duration, jobHealth, secondsSince, terminalJob, type JobProgress } from "./delegate-progress-state";

const providers: Record<string, string> = { codex: "Codex", gemini: "Antigravity", deepseek: "DeepSeek" };
type Delivery = { id: string; title: string; agent: string; at: string; current: boolean; contribution?: boolean; technical_status: string; issues: string[]; purpose: string };
type Project = { deliveries?: Delivery[]; quality_status?: string; summary?: string; next_action?: string; status?: string; product_path?: string; results?: Result[]; attention?: { code: string; message: string; action: string } | null; id: string; brief: string; steps: { id: string; agent: string; goal: string;
  status: string; note?: string; error?: string; attempt_count?: number }[] };
type Result = { path: string; agent: string; label: string; validated: boolean; at: string; delivery_id?: string; role?: string; open_with?: string; editability?: string; limitations?: string[] };
const roles: Record<string, string> = { export: "Prodotto", editable_source: "Sorgente modificabile", source_archive: "Pacchetto sorgenti", preview: "Anteprima", report: "Rapporto", dependency: "Risorsa collegata", file: "File" };
const stepLabels: Record<string, string> = { pending: "Da fare", running: "In corso",
  completed: "Incarico concluso", needs_revision: "Da rivedere", review: "Da valutare", paused: "In pausa", skipped: "Non necessaria" };

function JobCard({ job, now }: { job: JobProgress; now: number }) {
  const terminal = terminalJob(job);
  const end = terminal ? (Date.parse(job.finished_at) || now) : now;
  const elapsed = secondsSince(job.started_at || job.created_at, end);
  const deadline = Date.parse(job.deadline_at);
  const remaining = Number.isFinite(deadline) ? Math.max(0, Math.floor((deadline - now) / 1000)) : null;
  const heartbeat = secondsSince(job.heartbeat_at, now);
  const health = jobHealth(job, now);
  const stamp = (value: string) => Number.isFinite(Date.parse(value))
    ? new Date(value).toLocaleTimeString("it-IT", { hour: "2-digit", minute: "2-digit", second: "2-digit" }) : "";
  return <article className="bg-background space-y-3 rounded-lg border p-4" data-testid="delegate-job">
    <div className="flex flex-wrap items-center justify-between gap-2">
      <strong>{job.agent.charAt(0).toUpperCase() + job.agent.slice(1)} · {providers[job.engine] ?? job.engine}</strong>
      <span className="text-muted-foreground text-xs">{duration(elapsed)} trascorsi</span>
    </div>
    {job.model && <p className="text-muted-foreground text-xs">Modello: {job.model}</p>}
    {job.work_summary && job.work_summary !== job.summary && <p className="text-sm">{job.work_summary}</p>}
    <p className="text-sm" data-testid="delegate-summary">{job.summary}</p>
    {!terminal && <div className="text-muted-foreground space-y-1 text-xs">
      <p>Ultima attività: {duration(secondsSince(job.last_activity_at, now))} fa</p>
      {remaining !== null && remaining > 0 && <p>Limite di esecuzione tra {duration(remaining)}. Non è una stima di consegna.</p>}
      {heartbeat !== null && heartbeat <= 15 && <p>Worker raggiungibile</p>}
    </div>}
    {health && <p className="rounded-md border border-amber-500/50 p-2 text-sm" role="status">{health}</p>}
    {job.files.length > 0 && <div className="text-xs">
      <p>{job.files_count} file {job.phase === "completed" ? "presenti alla consegna" : terminal ? "provvisori, non consegnati" : "in lavorazione, ancora da verificare"}</p>
      <ul className="text-muted-foreground list-inside list-disc">
        {job.files.slice(0, 5).map((file) => <li key={file.name} className="break-all">{file.name} ({file.size} byte)</li>)}
      </ul>
    </div>}
    <ol className="text-muted-foreground space-y-1 text-xs" aria-label="Ultimi avanzamenti">
      {job.events.slice(-3).map((event, i) => <li key={i}><time>{stamp(event.at)}</time> · {event.summary}</li>)}
    </ol>
    {job.events.length > 3 && <details className="text-xs">
      <summary className="cursor-pointer">Cronologia operativa ({job.events.length} eventi recenti)</summary>
      <ol className="mt-2 space-y-1">{job.events.map((event, i) => <li key={i}><time>{stamp(event.at)}</time> · {event.summary}</li>)}</ol>
    </details>}
  </article>;
}

type Props = { threadId: string; active: boolean; pending: boolean; coordinatorError?: boolean; onContinue?: () => void | Promise<void> };
const person = (agent: string) => agent.charAt(0).toUpperCase() + agent.slice(1);
const kind = (path: string) => /\.(mp4|webm|mov)$/i.test(path) ? "video" : /\.(wav|mp3|m4a|ogg)$/i.test(path) ? "audio" : /\.(png|jpe?g|gif|webp)$/i.test(path) ? "image" : "source";
function artifactURL(threadId: string, path: string, download = false) {
  if (!path.startsWith("/mnt/user-data/")) return "";
  const encoded = path.split("/").map(encodeURIComponent).join("/");
  return `${getBackendBaseURL()}/api/threads/${encodeURIComponent(threadId)}/artifacts${encoded}${download ? "?download=true" : ""}`;
}

export function DelegateProgress({ threadId, active, pending, coordinatorError = false, onContinue }: Props) {
  const [snapshot, setSnapshot] = useState<{ threadId: string; jobs: JobProgress[]; project: Project | null } | null>(null);
  const [unavailable, setUnavailable] = useState(false);
  const [panel, setPanel] = useState<{ threadId: string; tab: string } | null>(null);
  const [resumeRequested, setResumeRequested] = useState<string | null>(null);
  const [resumeError, setResumeError] = useState<string | null>(null);
  const [accepting, setAccepting] = useState(false);
  const [acceptError, setAcceptError] = useState<string | null>(null);
  const resumeOwner = useRef(threadId);
  const resumeSequence = useRef(0);
  resumeOwner.current = threadId;
  const [now, setNow] = useState(Date.now);
  const jobs = snapshot?.threadId === threadId ? snapshot.jobs : [];
  const project = snapshot?.threadId === threadId ? snapshot.project : null;
  const tab = panel?.threadId === threadId ? panel.tab : null;
  const current = jobs.find((job) => !terminalJob(job));
  const working = !!current;
  const results = (project?.results ?? []).filter((r) => artifactURL(threadId, r.path));
  const deliveries = project?.deliveries ?? [];
  const selectedDelivery = deliveries.find((d) => d.current);
  const currentResults = selectedDelivery ? results.filter((r) => r.delivery_id === selectedDelivery.id) : results;
  const media = [...results].sort((a, b) => b.at.localeCompare(a.at)).filter((r) => kind(r.path) !== "source");
  const preview = media.find((r) => r.path === project?.product_path) ?? media.find((r) => kind(r.path) === "video") ?? media[0];
  const audio = currentResults.find((r) => kind(r.path) === "audio");
  const attention = !working && !active ? project?.attention : null;
  const ready = project?.status === "ready" && !!project.product_path && selectedDelivery?.technical_status === "passed"
    && ["passed", "accepted_by_user"].includes(project.quality_status ?? "") && !coordinatorError && !working;
  const waitingForReview = project?.status === "review" && !!project.product_path && selectedDelivery?.technical_status === "passed"
    && project.quality_status !== "passed" && !attention && !coordinatorError;
  const title = working ? `${person(current.agent)} sta lavorando` : active ? "La squadra sta preparando il prossimo risultato"
    : coordinatorError || attention || project?.status === "blocked" ? "Il lavoro è in pausa" : ready ? "Il risultato è pronto" : results.length ? "Una versione è disponibile" : "La squadra è pronta";
  const specificAction = current && ["running_tool", "exporting", "checking", "finalizing"].includes(current.phase)
    && current.summary !== "Esecuzione di uno strumento";
  const summary = working ? (specificAction ? current.summary : current.work_summary || current.summary) : attention?.message
    ?? (coordinatorError ? "Il coordinatore si è fermato. I file già salvati restano disponibili." : project?.summary || project?.brief);
  const toggle = (value: string) => setPanel(tab === value ? null : { threadId, tab: value });
  useEffect(() => { setPanel(null); setResumeRequested(null); setResumeError(null); setAcceptError(null); setAccepting(false); }, [threadId]);
  useEffect(() => { if (active) { setResumeRequested(null); setResumeError(null); } }, [active]);
  useEffect(() => {
    if (resumeRequested !== threadId || active || working) return;
    const timer = setTimeout(() => { setResumeRequested(null); setResumeError("Avvio non confermato: verifica lo stato e riprova se il lavoro resta fermo."); }, 15000);
    return () => clearTimeout(timer);
  }, [resumeRequested, threadId, active, working]);
  async function resume() {
    const owner = threadId;
    const sequence = ++resumeSequence.current;
    setResumeRequested(threadId); setResumeError(null);
    try { await onContinue?.(); }
    catch {
      if (resumeOwner.current === owner && resumeSequence.current === sequence) {
        setResumeRequested(null); setResumeError("Non riesco a inviare la richiesta di ripresa. I risultati restano disponibili: riprova.");
      }
    }
  }
  async function acceptVersion() {
    if (!selectedDelivery || accepting) return;
    const owner = threadId;
    setAccepting(true); setAcceptError(null);
    try {
      const response = await fetch(`${getBackendBaseURL()}/api/threads/${encodeURIComponent(threadId)}/studio-delivery/accept`, {
        method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ delivery_id: selectedDelivery.id }),
      });
      if (!response.ok) throw new Error("Version unavailable");
      const data = await response.json() as { project: Project };
      if (resumeOwner.current === owner) setSnapshot((current) => current?.threadId === owner ? { ...current, project: data.project } : current);
    } catch {
      if (resumeOwner.current === owner) setAcceptError("Non posso accettare questa versione: potrebbe essere cambiata o avere sorgenti incompleti. Aggiorna e controlla la consegna.");
    } finally { if (resumeOwner.current === owner) setAccepting(false); }
  }
  useEffect(() => {
    const controller = new AbortController();
    let timer: ReturnType<typeof setTimeout> | undefined;
    async function refresh() {
      let running = false;
      try {
        const response = await fetch(`${getBackendBaseURL()}/api/threads/${encodeURIComponent(threadId)}/studio-jobs`,
          { signal: controller.signal, cache: "no-store" });
        if (!response.ok) throw new Error("Progress unavailable");
        const data = await response.json() as { jobs: JobProgress[]; project?: Project | null };
        if (!Array.isArray(data.jobs)) throw new Error("Invalid progress");
        if (controller.signal.aborted) return;
        setSnapshot({ threadId, jobs: data.jobs, project: data.project ?? null });
        setUnavailable(false);
        running = data.jobs.some((job) => !terminalJob(job));
      } catch {
        if (controller.signal.aborted) return;
        setUnavailable(true);
      }
      // Keep watching an open conversation even between delegate calls or after a
      // background reconnect. A missing SSE event must not leave a frozen board.
      if (!controller.signal.aborted) timer = setTimeout(() => void refresh(), active || running ? 2000 : 5000);
    }
    if (threadId) void refresh();
    return () => { controller.abort(); if (timer) clearTimeout(timer); };
  }, [threadId, active]);
  useEffect(() => {
    if (!working && !pending) return;
    setNow(Date.now());
    const timer = setInterval(() => setNow(Date.now()), 1000);
    return () => clearInterval(timer);
  }, [working, pending]);
  if (!jobs.length && !project && !pending && !coordinatorError) return null;
  const health = current ? jobHealth(current, now) : null;
  const recent = [...jobs.filter((job) => !terminalJob(job)), ...jobs.filter(terminalJob).slice(0, 4)];
  return <section className="bg-background relative mb-2 rounded-xl border shadow-sm" aria-label="Il tuo progetto" data-testid="delegate-progress">
    {tab && <div className="bg-background absolute right-0 bottom-full left-0 z-50 mb-2 max-h-[60dvh] overflow-y-auto rounded-xl border p-4 shadow-xl" data-testid="studio-drawer">
      <div className="mb-3 flex items-center justify-between gap-2">
        <h3 className="font-medium">{tab === "preview" ? "Risultato da vedere" : tab === "team" ? "La squadra al lavoro" : tab === "files" ? "File e sorgenti" : "Attività e verifiche"}</h3>
        <button type="button" className="rounded border px-3 py-1 text-sm" onClick={() => setPanel(null)} aria-label="Chiudi dettagli del progetto">Chiudi</button>
      </div>
      {tab === "preview" && <div className="space-y-3">
        <p className="text-sm">{ready ? "Prodotto finale" : "Bozza di lavoro: può essere incompleta e non sostituisce il prodotto finale."}</p>
        {selectedDelivery && <p className="text-sm">{selectedDelivery.title}</p>}
        {project?.quality_status && <p className="text-sm">{project.quality_status === "accepted_by_user" ? "Questa versione è stata accettata da te." : project.quality_status === "passed" ? "Revisione dello specialista registrata per questa versione." : "Qualità ancora da valutare: le misure tecniche non sostituiscono visione e ascolto."}</p>}
        {preview && <div>
          {kind(preview.path) === "video" && <video key={preview.path} className="max-h-[35dvh] w-full rounded" controls playsInline preload="metadata" aria-label="Anteprima video" src={artifactURL(threadId, preview.path)} />}
          {kind(preview.path) === "image" && <img className="max-h-[35dvh] w-full object-contain" alt="Anteprima del lavoro" src={artifactURL(threadId, preview.path)} />}
          {kind(preview.path) === "audio" && <audio controls aria-label="Anteprima audio" src={artifactURL(threadId, preview.path)} />}
          <a className="text-sm underline" href={artifactURL(threadId, preview.path, true)}>{preview.label}</a>
        </div>}
        {audio && preview && kind(preview.path) === "video" && audio.path !== preview.path && <div>
          {!ready && <p className="text-sm">Audio disponibile separatamente. Questa bozza video potrebbe non contenerlo ancora.</p>}
          <audio controls preload="metadata" aria-label="Traccia audio disponibile" src={artifactURL(threadId, audio.path)} />
        </div>}
        {!preview && <p className="text-sm">Nessuna anteprima disponibile. Puoi controllare attività e file salvati.</p>}
        {!ready && !working && !active && selectedDelivery?.technical_status === "passed" && <div className="space-y-2 border-t pt-3">
          <p className="text-sm">Se hai verificato il risultato e ti soddisfa, puoi accettare questa versione. I controlli dei sorgenti restano obbligatori.</p>
          <button type="button" className="rounded border px-3 py-2 text-sm disabled:opacity-50" disabled={accepting} onClick={() => void acceptVersion()}>{accepting ? "Registro la scelta…" : "Ho verificato: accetta questa versione"}</button>
        </div>}
        {acceptError && <p className="text-sm" role="alert">{acceptError}</p>}
      </div>}
      {tab === "team" && <div data-testid="team-plan" className="space-y-3">
        <p className="text-sm">La squadra si adatta al risultato: può riprendere, cambiare ordine e integrare i file già disponibili.</p>
        {(project?.steps ?? []).map((step) => <article className="rounded border p-3 text-sm" key={step.id}>
          <strong>{person(step.agent)}</strong> · {stepLabels[step.status] ?? step.status}
          <p>{step.goal}</p>{step.note && <p className="text-muted-foreground">{step.note}</p>}
        </article>)}
      </div>}
      {tab === "files" && <div className="space-y-3 text-sm" data-testid="delivery-list">
        <p>Ogni pacchetto appartiene alla consegna indicata. Estrai tutto lo ZIP e segui le istruzioni di apertura; conserva le risorse accanto al progetto.</p>
        {deliveries.map((d) => <details key={d.id} open={d.current} className="rounded border p-3" data-testid="delivery-group">
          <summary className="cursor-pointer"><strong>{d.current ? "Consegna selezionata" : d.contribution ? "Contributo usato nella consegna" : d.purpose === "preview" ? "Prova" : "Lavorazione precedente"}</strong> · {person(d.agent)} · {d.at ? new Date(d.at).toLocaleString("it-IT") : ""}<p>{d.title}</p></summary>
          <p className="mt-2">{d.technical_status === "passed" ? "Controlli tecnici superati" : d.technical_status === "needs_revision" ? "Consegna incompleta: da correggere" : "Consegna precedente: nuovo collaudo non eseguito"}</p>
          {d.issues.map((issue, i) => <p className="mt-1" key={i}>{issue}</p>)}
          <ul className="mt-3 space-y-3">{results.filter((r) => r.delivery_id === d.id && r.role !== "preview" && r.role !== "dependency").map((r) => <DeliveryFile key={r.path} file={r} threadId={threadId} />)}</ul>
          <details className="mt-3"><summary className="cursor-pointer">Anteprime e risorse di questa consegna</summary><ul className="space-y-3">{results.filter((r) => r.delivery_id === d.id && (r.role === "preview" || r.role === "dependency")).map((r) => <DeliveryFile key={r.path} file={r} threadId={threadId} />)}</ul></details>
        </details>)}
        {!deliveries.length && <ul className="space-y-3">{results.map((r) => <DeliveryFile key={r.path} file={r} threadId={threadId} />)}</ul>}
        {!results.length && <p>I file appariranno qui quando saranno disponibili.</p>}
      </div>}
      {tab === "activity" && <div className="space-y-3">{recent.map((job) => <JobCard key={job.job_id} job={job} now={now} />)}</div>}
    </div>}
    <div className="space-y-1 p-3" role="status" aria-live="polite" aria-atomic="true">
      <div className="flex items-center justify-between gap-2"><strong className="text-sm" data-testid="studio-status">{title}</strong>
        {current && <span className="text-muted-foreground shrink-0 text-xs">{duration(secondsSince(current.started_at || current.created_at, now))}</span>}
      </div>
      {summary && <p className="line-clamp-2 text-sm" data-testid="studio-summary">{summary}</p>}
      {health && <p className="text-xs" data-testid="studio-health">{health}</p>}
      {!working && project?.next_action && !attention && <p className="text-muted-foreground line-clamp-2 text-xs">Prossimo passo: {project.next_action}</p>}
      {waitingForReview && !active && <p className="text-xs">Guarda il risultato e indica nella chat cosa vuoi correggere. Una verifica non disponibile non richiede di rigenerare tutto.</p>}
      {(attention || coordinatorError) && !active && !working && <p className="text-xs">{attention?.action ?? "Verifica il servizio AI e riprendi il lavoro dai risultati disponibili."}
        {(!attention || attention.code.startsWith("provider_")) && <> <a className="underline" href="/workspace/studio">Apri La tua squadra</a></>}</p>}
      {unavailable && <p className="text-xs" role="alert">Aggiornamenti non disponibili: questo stato potrebbe non essere attuale. Riprovo automaticamente.</p>}
      {resumeError && <p className="text-xs" role="alert">{resumeError}</p>}
    </div>
    <nav className="flex flex-wrap gap-2 border-t px-3 py-2 text-xs" aria-label="Controlli del progetto">
      <button type="button" className="rounded border px-3 py-1.5 disabled:opacity-50" disabled={!preview} aria-expanded={tab === "preview"} onClick={() => toggle("preview")}>Vedi risultato</button>
      <button type="button" className="rounded border px-3 py-1.5" aria-expanded={tab === "team"} onClick={() => toggle("team")}>Squadra</button>
      <button type="button" className="rounded border px-3 py-1.5" aria-expanded={tab === "files"} onClick={() => toggle("files")}>File e sorgenti ({results.length})</button>
      <button type="button" className="rounded border px-3 py-1.5" aria-expanded={tab === "activity"} onClick={() => toggle("activity")}>Attività</button>
      {!active && !working && !ready && !waitingForReview && onContinue && <button type="button" className="rounded border px-3 py-1.5 font-medium disabled:opacity-50" disabled={resumeRequested === threadId} onClick={() => void resume()}>{resumeRequested === threadId ? "Ripresa richiesta…" : "Riprendi lavoro"}</button>}
    </nav>
  </section>;
}

function DeliveryFile({ file, threadId }: { file: Result; threadId: string }) {
  return <li><span className="font-medium">{roles[file.role ?? "file"] ?? "File"}: </span><a className="break-all underline" href={artifactURL(threadId, file.path, true)}>{file.label}</a>
    {file.open_with && <p className="mt-1">Come aprire: {file.open_with}</p>}
    {file.editability && <p className="text-muted-foreground">Modificabile: {file.editability}</p>}
    {file.limitations?.map((limit, i) => <p className="text-muted-foreground" key={i}>{limit}</p>)}
  </li>;
}
