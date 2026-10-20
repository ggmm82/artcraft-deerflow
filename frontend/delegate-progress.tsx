"use client";

import { useEffect, useRef, useState, type ReactNode } from "react";
import { fetch } from "@/core/api/fetcher";
import { getBackendBaseURL } from "@/core/config";
import { duration, jobHealth, secondsSince, terminalJob, type JobProgress } from "./delegate-progress-state";

import { ExperiencePanel } from "./experience-panel";

const providers: Record<string, string> = { codex: "Codex", gemini: "Antigravity", deepseek: "DeepSeek", openai: "OpenAI compatibile" };
type Delivery = { id: string; title: string; agent: string; at: string; current: boolean; contribution?: boolean; technical_status: string; issues: string[]; purpose: string };
type MethodStrategy = { state: string; method: string; reason: string; user_action: string; stop_reason: string; alternatives: { method: string; reason: string; status: string; tools: string[]; evidence: { path: string; sha256: string }[] }[] };
type RevisionAction = { requirement_id: string; action: string; reason?: string; priority: number; strategy: string };
type Comparison = { baseline_path: string; criteria: { requirement_id: string; status: string; evidence: string }[] };
type Criterion = { requirement_id?: string; criterion: string; status: string; evidence: string; method: string };
type Outcome = { title: string; result: string; format: string; use: string; quality: string; constraints: string[]; assumptions: string[]; questions: string[] };
type ProjectRole = { experience?: { count: number; ids: string[] }; id: string; title: string; mission: string; version: string; expertise: string[]; procedure?: string[]; checks: string[]; tools: string[] };
type Orientation = { active_step_ids?: string[]; history_step_ids?: string[]; history_count?: number; total: number; counts: Record<string, number>; current: { id: string; goal: string; role_id: string; task: string }[]; remaining: { id: string; goal: string; status: string }[]; roles?: Record<string, { attempts: number; completed: number; running: number }>; needs_briefing: boolean };
type Project = { strategy?: MethodStrategy | null; method_recovery?: { message: string } | null; outcome?: Outcome | null; orientation?: Orientation; roles?: ProjectRole[]; acceptance?: { user_requests: string[]; request_manifest?: { path: string }; request_documents?: { path: string }[]; request_count?: number; criteria: { id: string; requirement: string; critical: boolean; origin?: string; source_quote?: string }[] } | null; review_criteria?: Criterion[]; revision_actions?: RevisionAction[]; comparison?: Comparison | null; deliveries?: Delivery[]; quality_status?: string; summary?: string; next_action?: string; status?: string; product_path?: string; results?: Result[]; attention?: { code: string; message: string; action: string } | null; id: string; brief: string; steps: { id: string; agent: string; goal: string;
  status: string; role_id?: string; role_title?: string; note?: string; error?: string; attempt_count?: number }[] };
type Result = { path: string; agent: string; label: string; validated: boolean; at: string; delivery_id?: string; role?: string; open_with?: string; editability?: string; limitations?: string[] };
const roles: Record<string, string> = { export: "Prodotto", editable_source: "Sorgente modificabile", source_archive: "Pacchetto sorgenti", preview: "Anteprima", report: "Rapporto", dependency: "Risorsa collegata", file: "File" };
const stepLabels: Record<string, string> = { pending: "Da fare", running: "In corso",
  completed: "Incarico concluso", needs_revision: "Da rivedere", review: "Da valutare", paused: "In pausa", skipped: "Non necessaria" };

type Tone = "active" | "done" | "attention" | "neutral";
function StatusBadge({ children, tone = "neutral" }: { children: ReactNode; tone?: Tone }) {
  const colors = { active: "border-blue-500/25 bg-blue-500/10 text-blue-700 dark:text-blue-300",
    done: "border-emerald-500/25 bg-emerald-500/10 text-emerald-700 dark:text-emerald-300",
    attention: "border-amber-500/25 bg-amber-500/10 text-amber-800 dark:text-amber-300",
    neutral: "border-border bg-muted/50 text-muted-foreground" };
  return <span className={`inline-flex items-center rounded-full border px-2 py-0.5 text-xs font-medium ${colors[tone]}`}>{children}</span>;
}
const stepTone = (state: string): Tone => state === "running" ? "active" : state === "completed" ? "done"
  : ["paused", "needs_revision", "review"].includes(state) ? "attention" : "neutral";
const tabStyle = "rounded-lg border border-transparent px-3 py-2 transition-colors hover:bg-muted focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-ring aria-expanded:border-border aria-expanded:bg-muted aria-expanded:font-semibold disabled:opacity-50";

function JobCard({ job, now }: { job: JobProgress; now: number }) {
  const operation = job.operations?.find(o => o.state === "running") ?? job.operations?.[0];
  const terminal = terminalJob(job);
  const end = terminal ? (Date.parse(job.finished_at) || now) : now;
  const elapsed = secondsSince(job.started_at || job.created_at, end);
  const deadline = Date.parse(job.deadline_at);
  const remaining = Number.isFinite(deadline) ? Math.max(0, Math.floor((deadline - now) / 1000)) : null;
  const heartbeat = secondsSince(job.heartbeat_at, now);
  const health = jobHealth(job, now);
  const stamp = (value: string) => Number.isFinite(Date.parse(value))
    ? new Date(value).toLocaleTimeString("it-IT", { hour: "2-digit", minute: "2-digit", second: "2-digit" }) : "";
  return <article className="bg-background space-y-3 rounded-2xl border p-4 shadow-sm" data-testid="delegate-job">
    <div className="flex flex-wrap items-center justify-between gap-2">
      <strong>{job.role_title || job.agent.charAt(0).toUpperCase() + job.agent.slice(1)} · {providers[job.engine] ?? job.engine}</strong>
      <span className="text-muted-foreground text-xs">{duration(elapsed)} trascorsi</span>
    </div>
    {operation && <div className="rounded-md border p-2 text-sm" data-testid="operation-progress">
      <p>{operation.label} · {operation.state === "running" && !terminal ? "in esecuzione" : operation.state === "completed" ? "conclusa" : operation.state === "out_of_memory" ? "memoria esaurita" : "interrotta"}</p>
      {operation.progress?.total && <p>{operation.progress.done ?? 0}/{operation.progress.total} campioni osservati</p>}
      {operation.estimate_seconds !== undefined && <p>Stima iniziale dal campione: circa {duration(Math.round(operation.estimate_seconds))}. Può variare.</p>}
      {operation.elapsed_seconds !== undefined && <p>{duration(Math.floor(operation.elapsed_seconds))} di elaborazione</p>}
    </div>}
    {job.resources?.memory_bytes !== undefined && <p className="text-muted-foreground text-xs">RAM worker: {Math.round(job.resources.memory_bytes / 1048576)} MiB{job.resources.memory_limit_bytes ? ` / ${Math.round(job.resources.memory_limit_bytes / 1048576)} MiB` : ""}{job.limits?.cpus ? ` · ${job.limits.cpus} CPU` : ""}</p>}
    {!!job.resources?.oom_kills && <p role="status" className="text-sm">Il sistema ha terminato un processo per memoria esaurita. Conserva i file e verifica il budget della squadra prima di riprovare.</p>}
    {job.model && <p className="text-muted-foreground text-xs">Modello: {job.model}</p>}
    {job.work_summary && job.work_summary !== job.summary && <p className="text-sm">{job.work_summary}</p>}
    <p className="text-sm" data-testid="delegate-summary">{job.summary}</p>
    {!terminal && <div className="text-muted-foreground space-y-1 text-xs">
      <p>Ultimo avanzamento osservato: {duration(secondsSince(job.last_activity_at, now))} fa</p>
      {job.execution_started_at && <p>{job.execution_state === "model" ? "Attesa del modello" : "Comando in esecuzione"}: {duration(secondsSince(job.execution_started_at, now))}</p>}
      {job.last_model_event_at && <p>Ultimo evento ricevuto dal modello: {duration(secondsSince(job.last_model_event_at, now))} fa</p>}
      {job.last_file_change_at && <p>Ultima modifica dei file: {duration(secondsSince(job.last_file_change_at, now))} fa</p>}
      {remaining !== null && remaining > 0 && <p>Limite di esecuzione tra {duration(remaining)}. Non è una stima di consegna.</p>}
      {(job.limits?.model_wait_seconds ?? 0) > 0 && ["codex", "gemini"].includes(job.engine) && <p>Budget senza eventi del modello: {duration(job.limits?.model_wait_seconds ?? 0)}; poi il coordinatore può ripianificare.</p>}
      {heartbeat !== null && heartbeat <= 15 && <p>Monitor della sandbox presente · non conferma l’avanzamento del modello</p>}
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
  const dock = useRef<HTMLElement>(null);
  const resumeSequence = useRef(0);
  resumeOwner.current = threadId;
  const [now, setNow] = useState(Date.now);
  const jobs = snapshot?.threadId === threadId ? snapshot.jobs : [];
  const project = snapshot?.threadId === threadId ? snapshot.project : null;
  const tab = panel?.threadId === threadId ? panel.tab : null;
  const current = jobs.find((job) => !terminalJob(job));
  const questions = project?.outcome?.questions ?? [];
  const clarifying = questions.length > 0 || project?.status === "clarifying";
  const allSteps = project?.steps ?? [];
  const activeStepIds = new Set(project?.orientation?.active_step_ids ?? allSteps.map(step => step.id));
  const currentSteps = allSteps.filter(step => activeStepIds.has(step.id));
  const otherSteps = allSteps.filter(step => !activeStepIds.has(step.id));
  const currentActivity = currentSteps.find(step => step.status === "running");
  const planned = currentSteps.filter(step => step.status !== "skipped");
  const completed = planned.filter(step => step.status === "completed").length;
  const working = !!current;
  const results = (project?.results ?? []).filter((r) => artifactURL(threadId, r.path));
  const deliveries = project?.deliveries ?? [];
  const selectedDelivery = deliveries.find((d) => d.current);
  const currentResults = selectedDelivery ? results.filter((r) => r.delivery_id === selectedDelivery.id) : results;
  const media = [...currentResults].filter(r => r.role !== "dependency" && r.role !== "report").sort((a, b) => b.at.localeCompare(a.at)).filter((r) => kind(r.path) !== "source");
  const selected: Result | undefined = project?.product_path
    ? results.find((r) => r.path === project.product_path) ?? { path: project.product_path, label: project.product_path.split("/").pop() ?? "Risultato", agent: "", validated: false, at: "" }
    : undefined;
  const preview = selected ?? currentResults.find(r => r.role === "export") ?? media.find((r) => kind(r.path) === "video") ?? media[0];
  const pairedSources = preview?.delivery_id ? results.filter(r => r.delivery_id === preview.delivery_id && ["editable_source", "source_archive"].includes(r.role ?? "")) : [];
  const audio = currentResults.find((r) => kind(r.path) === "audio");
  const attention = !working && !active ? project?.attention : null;
  const ready = project?.status === "ready" && !!project.product_path && selectedDelivery?.technical_status === "passed"
    && ["passed", "accepted_by_user"].includes(project.quality_status ?? "") && !coordinatorError && !working;
  const waitingForReview = project?.status === "review" && !!project.product_path && selectedDelivery?.technical_status === "passed"
    && project.quality_status !== "passed" && !attention && !coordinatorError;
  const title = working && jobHealth(current, now) ? "Avanzamento da verificare" : working ? `${current.role_title || person(current.agent)} sta lavorando` : clarifying ? "Definiamo il risultato insieme" : active ? "La squadra sta preparando il prossimo risultato"
    : coordinatorError || attention || project?.status === "blocked" ? "Il lavoro è in pausa" : ready ? "Il risultato è pronto" : results.length ? "Una versione è disponibile" : "La squadra è pronta";
  const specificAction = current && ["running_tool", "exporting", "checking", "finalizing"].includes(current.phase)
    && current.summary !== "Esecuzione di uno strumento";
  const nativeOperation = current?.operations?.find(o => o.state === "running");
  const nativeSummary = nativeOperation ? nativeOperation.label + (nativeOperation.progress?.total ? ` · ${nativeOperation.progress.done ?? 0}/${nativeOperation.progress.total} campioni` : "") : null;
  const summary = clarifying && !working ? (questions[0] || "Mancano risultato atteso e forma della consegna.") : working ? (nativeSummary ?? (specificAction ? current.summary : current.work_summary || current.summary)) : attention?.message
    ?? (coordinatorError ? "Il coordinatore si è fermato. I file già salvati restano disponibili." : project?.summary || project?.brief);
  const toggle = (value: string) => setPanel(tab === value ? null : { threadId, tab: value });
  useEffect(() => { setPanel(null); setResumeRequested(null); setResumeError(null); setAcceptError(null); setAccepting(false); }, [threadId]);
  useEffect(() => {
    const element = dock.current;
    if (!element) return;
    const measure = () => element.style.setProperty("--studio-panel-space", `${Math.max(0, element.getBoundingClientRect().top - 16)}px`);
    measure();
    const observer = new ResizeObserver(measure);
    observer.observe(element);
    if (element.parentElement) observer.observe(element.parentElement);
    window.addEventListener("resize", measure);
    window.visualViewport?.addEventListener("resize", measure);
    return () => { observer.disconnect(); window.removeEventListener("resize", measure); window.visualViewport?.removeEventListener("resize", measure); };
  }, [threadId, tab, project, jobs.length, pending, coordinatorError]);
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
  return <section ref={dock} className="bg-background relative mb-2 rounded-2xl border shadow-sm" aria-label="Il tuo progetto" data-testid="delegate-progress">
    {tab && <div className="bg-background absolute right-0 bottom-full left-0 z-50 mb-2 flex flex-col overflow-hidden rounded-2xl border shadow-xl" style={{ maxHeight: "min(60dvh, var(--studio-panel-space, 60dvh))" }} data-testid="studio-drawer">
      <div className="bg-background flex shrink-0 items-center justify-between gap-2 border-b px-4 py-3">
        <h3 className="text-sm font-semibold">{tab === "project" ? "Il progetto e il punto attuale" : tab === "preview" ? "Risultato da vedere" : tab === "team" ? "La squadra del progetto" : tab === "files" ? "File e sorgenti" : tab === "experience" ? "Esperienza conservata" : "Attività e verifiche"}</h3>
        <button type="button" className="hover:bg-muted rounded-lg border px-3 py-1.5 text-sm focus-visible:outline-2 focus-visible:outline-ring" onClick={() => setPanel(null)} aria-label="Chiudi dettagli del progetto">Chiudi</button>
      </div>
      <div className="min-h-0 overflow-y-auto p-4" data-testid="studio-drawer-content">
      {tab === "project" && project && <div className="space-y-4 text-sm" data-testid="project-overview">
        <section className="bg-muted/30 space-y-3 rounded-xl border p-4">
          <h4 className="text-muted-foreground text-xs font-semibold uppercase tracking-wide">Risultato da ottenere</h4>
          <p className="text-base font-medium leading-relaxed">{project.outcome?.result || project.brief}</p>
          <p><strong>Consegna:</strong> {project.outcome?.format || "Da definire con te prima di proseguire la produzione."}</p>
          {project.outcome?.use && <p><strong>Uso e destinatari:</strong> {project.outcome.use}</p>}
          {project.outcome?.quality && <p><strong>Qualità attesa:</strong> {project.outcome.quality}</p>}
        </section>
        {questions.length > 0 && <section className="space-y-2 rounded-xl border border-amber-500/30 bg-amber-500/5 p-4" data-testid="brief-questions">
          <h4 className="font-semibold">Le scelte che mancano</h4>
          <ul className="list-inside list-disc">{questions.map((q, i) => <li key={i}>{q}</li>)}</ul>
          <p>Rispondi alle domande nella chat. La produzione attende queste scelte.</p>
        </section>}
        <section className="space-y-2 rounded-xl border border-blue-500/25 bg-blue-500/5 p-4" data-testid="project-position">
          <h4 className="font-semibold">Dove siamo</h4>
          <p>{planned.length ? `${completed} di ${planned.length} incarichi conclusi nella squadra attuale` : "La squadra e le attività sono ancora da definire."}</p>
          {currentActivity && <p><strong>Traguardo in corso:</strong> {currentActivity.goal}</p>}
          {summary && <p><strong>Adesso:</strong> {summary}</p>}
          {!working && !clarifying && project.next_action && <p><strong>Prossima azione:</strong> {project.next_action}</p>}
          <p className="text-muted-foreground text-xs">Gli incarichi possono cambiare. Il conteggio non è una percentuale di completamento o una stima dei tempi.</p>
        </section>
        {planned.some(step => step.status !== "completed") && <section className="space-y-2">
          <h4 className="font-semibold">Attività ancora previste</h4>
          <ul className="space-y-2">{planned.filter(step => step.status !== "completed").map(step => <li key={step.id} className="flex items-start gap-3 rounded-lg border p-3">
            <span className="shrink-0"><StatusBadge tone={stepTone(step.status)}>{stepLabels[step.status] ?? step.status}</StatusBadge></span><span>{step.goal}</span>
          </li>)}</ul>
        </section>}
        {otherSteps.length > 0 && <details className="space-y-2 rounded-xl border p-3" data-testid="project-history">
          <summary className="cursor-pointer font-medium">Altre attività del progetto ({otherSteps.length})</summary>
          <p className="text-muted-foreground">Queste attività appartengono a ruoli fuori dalla squadra attuale. Tentativi e file restano conservati; possono essere ripresi senza ricominciare.</p>
          <ul className="space-y-2">{otherSteps.map(step => <li key={step.id}><StatusBadge tone={stepTone(step.status)}>{stepLabels[step.status] ?? step.status}</StatusBadge> {step.goal}</li>)}</ul>
        </details>}
        {(project.strategy || project.method_recovery) && <section className="space-y-2 rounded-xl border p-3" data-testid="project-method">
          <h4 className="font-semibold">Metodo e alternative</h4>
          {project.method_recovery && <p className="text-amber-700 dark:text-amber-300">{project.method_recovery.message}</p>}
          {project.strategy && <>
            <p><strong>{project.strategy.state === "selected" ? "Metodo scelto" : project.strategy.state === "needs_user" ? "Decisione necessaria" : "Metodo in valutazione"}:</strong> {project.strategy.method}</p>
            <p>{project.strategy.reason}</p>
            <ul className="space-y-2">{project.strategy.alternatives.map((item, index) => <li key={index} className="rounded-lg border p-2">
              <p><strong>{item.method}</strong> · {item.status === "candidate" ? "Da provare" : item.status === "tested" ? "Prova disponibile" : "Valutato non disponibile"}</p>
              <p>{item.reason}</p>
              {!!item.tools.length && <p className="text-muted-foreground text-xs">Strumenti: {item.tools.join(", ")}</p>}
              {item.evidence.map((proof, i) => { const href = artifactURL(threadId, proof.path); return href ? <a key={i} href={href} target="_blank" rel="noreferrer" className="mr-3 underline">Prova {i + 1}</a> : null; })}
            </li>)}</ul>
            {project.strategy.state === "needs_user" && <p><strong>Per proseguire:</strong> {project.strategy.user_action}</p>}
          </>}
          {!!project.outcome?.assumptions.length && <div><h5 className="font-medium">Scelte provvisorie della squadra</h5><ul className="list-inside list-disc">{project.outcome.assumptions.map((item, i) => <li key={i}>{item}</li>)}</ul><p className="text-muted-foreground text-xs">Si possono rivedere mantenendo il risultato e i vincoli richiesti.</p></div>}
        </section>}
        {!!project.revision_actions?.length && <section className="space-y-2 rounded-xl border border-amber-500/30 p-3" data-testid="revision-actions">
          <h4 className="font-semibold">Correzioni dal controllo qualità</h4>
          <ol className="list-inside list-decimal space-y-2">{project.revision_actions.map((action, i) => <li key={i}>{action.action}{action.strategy === "change_method" && <p className="text-muted-foreground text-xs">Serve provare un metodo diverso.</p>}</li>)}</ol>
        </section>}
        {project.comparison && <section className="space-y-2 rounded-xl border p-3" data-testid="quality-comparison">
          <h4 className="font-semibold">Confronto con la versione precedente</h4>
          <ul className="space-y-2">{project.comparison.criteria.map((item, i) => <li key={i}><strong>{item.status === "improved" ? "Migliorato" : item.status === "unchanged" ? "Invariato" : item.status === "regressed" ? "Peggiorato" : "Non verificato"}</strong> · {item.evidence}</li>)}</ul>
        </section>}
        {!!project.outcome?.constraints.length && <section><h4 className="font-semibold">Vincoli</h4><ul className="list-inside list-disc">{project.outcome.constraints.map((c, i) => <li key={i}>{c}</li>)}</ul></section>}
        {!!project.outcome?.assumptions.length && <section><h4 className="font-semibold">Ipotesi adottate</h4><ul className="list-inside list-disc">{project.outcome.assumptions.map((a, i) => <li key={i}>{a}</li>)}</ul></section>}
      </div>}
      {tab === "preview" && <div className="space-y-3">
        <p><StatusBadge tone={ready ? "done" : "attention"}>{ready ? "Prodotto finale" : "Bozza di lavoro: può essere incompleta e non sostituisce il prodotto finale."}</StatusBadge></p>
        {selectedDelivery && <p className="text-sm">{selectedDelivery.title}</p>}
        {preview && <div className="bg-muted/20 space-y-3 rounded-xl border p-3" data-testid="primary-result">
          {kind(preview.path) === "video" && <video key={preview.path} className="max-h-[35dvh] w-full rounded" controls playsInline preload="metadata" aria-label="Anteprima video" src={artifactURL(threadId, preview.path)} />}
          {kind(preview.path) === "image" && <img className="max-h-[35dvh] w-full object-contain" alt="Anteprima del lavoro" src={artifactURL(threadId, preview.path)} />}
          {kind(preview.path) === "audio" && <audio controls aria-label="Anteprima audio" src={artifactURL(threadId, preview.path)} />}
          {kind(preview.path) === "source" && <p className="text-sm">Risultato disponibile come documento o progetto: scaricalo e aprilo con l’app indicata nella consegna.</p>}
          <p className="text-muted-foreground text-xs">Scarica il risultato</p>
          <a className="bg-foreground text-background inline-flex max-w-full items-center rounded-lg px-4 py-2 text-sm font-medium break-all focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-ring" href={artifactURL(threadId, preview.path, true)}>{preview.label}</a>
          {preview.open_with && <p className="text-sm">Come aprire: {preview.open_with}</p>}
          {preview.limitations?.map((limit, i) => <p className="text-muted-foreground text-xs" key={i}>{limit}</p>)}
        </div>}
        {audio && preview && kind(preview.path) === "video" && audio.path !== preview.path && <div>
          {!ready && <p className="text-sm">Audio disponibile separatamente. Questa bozza video potrebbe non contenerlo ancora.</p>}
          <audio controls preload="metadata" aria-label="Traccia audio disponibile" src={artifactURL(threadId, audio.path)} />
        </div>}
        {!preview && <p className="text-sm">Nessuna anteprima disponibile. Puoi controllare attività e file salvati.</p>}
        {pairedSources.length > 0 && <section className="space-y-3 rounded-xl border p-3 text-sm" data-testid="paired-sources">
          <h4 className="font-semibold">Sorgenti della stessa consegna</h4>
          <ul className="space-y-3">{pairedSources.map(file => <DeliveryFile key={file.path} file={file} threadId={threadId} />)}</ul>
        </section>}
        {project?.quality_status && <p className="text-sm">{project.quality_status === "accepted_by_user" ? "Questa versione è stata accettata da te." : project.quality_status === "passed" ? "Revisione dello specialista registrata per questa versione." : "Qualità ancora da valutare: i controlli tecnici non verificano tutti i requisiti del progetto."}</p>}
        {project?.acceptance && <details className="rounded border p-3 text-sm" data-testid="acceptance-criteria">
          <summary className="cursor-pointer font-medium">Rispondenza alla tua richiesta</summary>
          <p className="my-2 whitespace-pre-wrap">{project.acceptance.user_requests[0]}</p>
          <ul className="space-y-2">{project.acceptance.criteria.map((rule) => {
            const observed = project.review_criteria?.find((c) => c.requirement_id === rule.id);
            return <li key={rule.id}><strong>{observed?.status === "passed" ? "Verificato" : observed?.status === "failed" ? "Da correggere" : "Da verificare"}</strong> · {rule.requirement}
              {rule.origin === "proposal" && <p className="text-muted-foreground text-xs">Criterio proposto dalla squadra, rivedibile nel rispetto della richiesta.</p>}
              {rule.origin === "user" && rule.source_quote && <p className="text-muted-foreground text-xs">Dalla tua richiesta: «{rule.source_quote}»</p>}
              {observed && <p className="text-muted-foreground">{observed.evidence}</p>}</li>;
          })}</ul>
          {project.acceptance.request_documents?.[0] && <p><a className="underline" href={artifactURL(threadId, project.acceptance.request_documents[0].path, true)}>Leggi la richiesta originale completa</a></p>}
          {project.acceptance.request_manifest && <p><a className="underline" href={artifactURL(threadId, project.acceptance.request_manifest.path, true)}>Indice dei messaggi conservati ({project.acceptance.request_count ?? 1})</a></p>}
        </details>}
        {!ready && !working && !active && selectedDelivery?.technical_status === "passed" && <div className="space-y-2 border-t pt-3">
          <p className="text-sm">Se hai verificato il risultato e ti soddisfa, puoi accettare questa versione. I controlli dei sorgenti restano obbligatori.</p>
          <button type="button" className="rounded border px-3 py-2 text-sm disabled:opacity-50" disabled={accepting} onClick={() => void acceptVersion()}>{accepting ? "Registro la scelta…" : "Ho verificato: accetta questa versione"}</button>
        </div>}
        {acceptError && <p className="text-sm" role="alert">{acceptError}</p>}
      </div>}
      {tab === "team" && <div data-testid="team-plan" className="space-y-3">
        <p className="text-sm">La squadra si adatta al risultato: può riprendere, cambiare ordine e integrare i file già disponibili.</p>
        {(project?.roles ?? []).map(role => {
          const activities = currentSteps.filter(step => step.role_id === role.id);
          const live = jobs.find(job => job.role_id === role.id && !terminalJob(job));
          const usage = project?.orientation?.roles?.[role.id];
          const used = (usage?.attempts ?? jobs.filter(job => job.role_id === role.id).length) > 0;
          const state = live || !!usage?.running ? "Al lavoro" : used && activities.some(step => step.status === "paused") ? "In pausa" : used ? "Ha lavorato al progetto" : "Previsto";
          return <article key={role.id} className="bg-muted/20 space-y-3 rounded-xl border p-4 text-sm" data-testid="compiled-role">
            <div className="flex flex-wrap items-center justify-between gap-2"><strong className="text-base">{role.title}</strong><StatusBadge tone={live || usage?.running ? "active" : state === "In pausa" ? "attention" : "neutral"}>{state}</StatusBadge></div>
            <p>{role.mission}</p>
            {role.experience && <p>{role.experience.count} osservazioni pertinenti incluse nella skill compilata.</p>}
            <h4 className="text-muted-foreground text-xs font-semibold uppercase tracking-wide">Competenze assegnate</h4>
            <ul className="list-inside list-disc">{role.expertise.map((skill, i) => <li key={i}>{skill}</li>)}</ul>
            <div className="space-y-2"><p className="text-muted-foreground text-xs font-semibold">Strumenti assegnati</p><div className="flex flex-wrap gap-1.5">{role.tools.length ? role.tools.map(tool => <StatusBadge key={tool}>{person(tool)}</StatusBadge>) : <span>Strumenti di base del progetto</span>}</div></div>
            {live && <p><strong>Adesso:</strong> {live.work_summary || live.summary}</p>}
            <ul className="space-y-1">{activities.map(step => <li key={step.id}><StatusBadge tone={stepTone(step.status)}>{stepLabels[step.status] ?? step.status}</StatusBadge> {step.goal}</li>)}</ul>
            {!activities.length && <p className="text-muted-foreground">{used ? "Contributi registrati nelle attività precedenti." : "Nessun incarico ancora assegnato."}</p>}
            <details><summary className="cursor-pointer">Metodo e verifiche previste</summary>
              {!!role.procedure?.length && <ol className="mt-2 list-inside list-decimal">{role.procedure.map((item, i) => <li key={i}>{item}</li>)}</ol>}
              <ul className="mt-2 list-inside list-disc">{role.checks.map((check, i) => <li key={i}>{check}</li>)}</ul>
              <p className="text-muted-foreground mt-2 text-xs">Versione {role.version.slice(0, 12)} · questi sono controlli da eseguire, non verifiche già superate. Gli strumenti effettivamente invocati sono nell’attività dell’incarico.</p>
            </details>
          </article>;
        })}
        {currentSteps.filter(step => !(project?.roles ?? []).some(role => role.id === step.role_id)).map(step => <article className="rounded border p-3 text-sm" key={step.id}>
          <strong>{step.role_title || person(step.agent)}</strong> · {stepLabels[step.status] ?? step.status}
          <p>{step.goal}</p>{step.note && <p className="text-muted-foreground">{step.note}</p>}
        </article>)}
      </div>}
      {tab === "files" && <div className="space-y-3 text-sm" data-testid="delivery-list">
        <p>Ogni pacchetto appartiene alla consegna indicata. Estrai tutto lo ZIP e segui le istruzioni di apertura; conserva le risorse accanto al progetto.</p>
        {deliveries.map((d) => <details key={d.id} open={d.current} className={`rounded-xl border p-4 ${d.current ? "border-blue-500/30 bg-blue-500/5" : "bg-muted/20"}`} data-testid="delivery-group">
          <summary className="cursor-pointer"><strong>{d.current ? "Consegna selezionata" : d.contribution ? "Contributo usato nella consegna" : d.purpose === "preview" ? "Prova" : "Lavorazione precedente"}</strong> · {person(d.agent)} · {d.at ? new Date(d.at).toLocaleString("it-IT") : ""}<p>{d.title}</p></summary>
          <p className="mt-2"><StatusBadge tone={d.technical_status === "passed" ? "done" : d.technical_status === "needs_revision" ? "attention" : "neutral"}>{d.technical_status === "passed" ? "Controlli tecnici superati" : d.technical_status === "needs_revision" ? "Consegna incompleta: da correggere" : "Consegna precedente: nuovo collaudo non eseguito"}</StatusBadge></p>
          {d.issues.map((issue, i) => <p className="mt-1" key={i}>{issue}</p>)}
          <ul className="mt-3 space-y-3">{results.filter((r) => r.delivery_id === d.id && r.role !== "preview" && r.role !== "dependency").map((r) => <DeliveryFile key={r.path} file={r} threadId={threadId} />)}</ul>
          <details className="mt-3"><summary className="cursor-pointer">Anteprime e risorse di questa consegna</summary><ul className="space-y-3">{results.filter((r) => r.delivery_id === d.id && (r.role === "preview" || r.role === "dependency")).map((r) => <DeliveryFile key={r.path} file={r} threadId={threadId} />)}</ul></details>
        </details>)}
        {!deliveries.length && <ul className="space-y-3">{results.map((r) => <DeliveryFile key={r.path} file={r} threadId={threadId} />)}</ul>}
        {!results.length && <p>I file appariranno qui quando saranno disponibili.</p>}
      </div>}
      {tab === "experience" && <ExperiencePanel key={threadId} threadId={threadId} deliveries={deliveries} />}
      {tab === "activity" && <div className="space-y-3">{recent.map((job) => <JobCard key={job.job_id} job={job} now={now} />)}</div>}
      </div>
    </div>}
    <div className="space-y-1 p-3" role="status" aria-live="polite" aria-atomic="true">
      {project && <div className="mb-2 space-y-1 border-b pb-2" data-testid="project-identity">
        <p className="line-clamp-1 text-sm font-semibold tracking-tight">{project.outcome?.title || project.outcome?.result || "Il tuo progetto"}</p>
        <p className="text-muted-foreground line-clamp-1 text-xs">Consegna: {project.outcome?.format || "da definire"}</p>
        {planned.length > 0 && <p className="text-muted-foreground line-clamp-2 text-xs">{completed} di {planned.length} incarichi conclusi{currentActivity ? ` · ${stepLabels[currentActivity.status]}: ${currentActivity.goal}` : ""}</p>}
      </div>}
      <div className="flex items-center justify-between gap-2"><strong className="text-sm" data-testid="studio-status"><span aria-hidden="true" className={`mr-2 inline-block h-2 w-2 rounded-full ${working ? "bg-blue-500" : ready ? "bg-emerald-500" : attention || clarifying || coordinatorError ? "bg-amber-500" : "bg-muted-foreground"}`} />{title}</strong>
        {current && <span className="text-muted-foreground shrink-0 text-xs">{duration(secondsSince(current.started_at || current.created_at, now))}</span>}
      </div>
      {summary && <p className="line-clamp-2 text-sm" data-testid="studio-summary">{summary}</p>}
      {health && <p className="text-xs" data-testid="studio-health">{health}</p>}
      {!working && !clarifying && project?.next_action && !attention && <p className="text-muted-foreground line-clamp-2 text-xs">Prossimo passo: {project.next_action}</p>}
      {waitingForReview && !active && <p className="text-xs">Guarda il risultato e indica nella chat cosa vuoi correggere. Una verifica non disponibile non richiede di rigenerare tutto.</p>}
      {(attention || coordinatorError) && !active && !working && <p className="text-xs">{attention?.action ?? "Verifica il servizio AI e riprendi il lavoro dai risultati disponibili."}
        {(!attention || attention.code.startsWith("provider_")) && <> <a className="underline" href="/workspace/studio">Apri La tua squadra</a></>}</p>}
      {clarifying && !working && <p className="text-xs">Rispondi nella chat: la produzione attende le scelte sul risultato.</p>}
      {unavailable && <p className="text-xs" role="alert">Aggiornamenti non disponibili: questo stato potrebbe non essere attuale. Riprovo automaticamente.</p>}
      {resumeError && <p className="text-xs" role="alert">{resumeError}</p>}
    </div>
    <nav className="flex flex-wrap gap-1 border-t px-2 py-1.5 text-xs" aria-label="Controlli del progetto">
      <button type="button" className={tabStyle} aria-expanded={tab === "project"} onClick={() => toggle("project")}>Progetto</button>
      <button type="button" className={tabStyle} disabled={!preview} aria-expanded={tab === "preview"} onClick={() => toggle("preview")}>Vedi risultato</button>
      <button type="button" className={tabStyle} aria-expanded={tab === "team"} onClick={() => toggle("team")}>Squadra</button>
      <button type="button" className={tabStyle} aria-expanded={tab === "files"} onClick={() => toggle("files")}>File e sorgenti ({results.length})</button>
      <button type="button" className={tabStyle} aria-expanded={tab === "activity"} onClick={() => toggle("activity")}>Attività</button>
      <button type="button" className={tabStyle} aria-expanded={tab === "experience"} onClick={() => toggle("experience")}>Esperienza</button>
      {!active && !working && !ready && !waitingForReview && !questions.length && onContinue && <button type="button" className="rounded border px-3 py-1.5 font-medium disabled:opacity-50" disabled={resumeRequested === threadId} onClick={() => void resume()}>{resumeRequested === threadId ? "Ripresa richiesta…" : clarifying ? "Definisci risultato" : "Riprendi lavoro"}</button>}
    </nav>
  </section>;
}

function DeliveryFile({ file, threadId }: { file: Result; threadId: string }) {
  return <li className="border-l-2 border-border pl-3"><span className="text-muted-foreground text-xs font-medium">{roles[file.role ?? "file"] ?? "File"}: </span><a className="break-all underline" href={artifactURL(threadId, file.path, true)}>{file.label}</a>
    {file.open_with && <p className="mt-1">Come aprire: {file.open_with}</p>}
    {file.editability && <p className="text-muted-foreground">Modificabile: {file.editability}</p>}
    {file.limitations?.map((limit, i) => <p className="text-muted-foreground" key={i}>{limit}</p>)}
  </li>;
}
