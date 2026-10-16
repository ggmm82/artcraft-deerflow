"use client";

import { useEffect, useState } from "react";
import { fetch } from "@/core/api/fetcher";
import { getBackendBaseURL } from "@/core/config";
import { duration, jobHealth, secondsSince, terminalJob, type JobProgress } from "./delegate-progress-state";

const providers: Record<string, string> = { codex: "Codex", gemini: "Antigravity", deepseek: "DeepSeek" };
type Project = { id: string; brief: string; steps: { id: string; agent: string; goal: string;
  status: string; depends_on: string[]; attempts: { output_files?: string[] }[] }[] };
const stepLabels: Record<string, string> = { pending: "Da fare", running: "In corso",
  completed: "Verificata", needs_revision: "Da riprendere o correggere" };

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

export function DelegateProgress({ threadId, active, pending }: { threadId: string; active: boolean; pending: boolean }) {
  const [snapshot, setSnapshot] = useState<{ threadId: string; jobs: JobProgress[]; project: Project | null } | null>(null);
  const [unavailable, setUnavailable] = useState(false);
  const [now, setNow] = useState(Date.now);
  const jobs = snapshot?.threadId === threadId ? snapshot.jobs : [];
  const project = snapshot?.threadId === threadId ? snapshot.project : null;
  const working = jobs.some((job) => !terminalJob(job));
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
        running = data.jobs.some((job) => !terminalJob(job)) || !!data.project?.steps.some((step) => step.status === "running");
      } catch {
        if (controller.signal.aborted) return;
        setUnavailable(true);
        running = true;
      }
      if (!controller.signal.aborted && (active || running)) timer = setTimeout(() => void refresh(), 2000);
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
  if (!jobs.length && !pending && !project) return null;
  const visible = [...jobs.filter((job) => !terminalJob(job)), ...jobs.filter(terminalJob).slice(0, 3)];
  return <section className="w-full space-y-3" aria-label="Avanzamento specialisti" data-testid="delegate-progress">
    <h3 className="text-sm font-medium">Lavoro della squadra</h3>
    {project && <article className="bg-background space-y-2 rounded-lg border p-4" data-testid="team-plan">
      <p className="text-sm font-medium">{project.brief}</p>
      <p className="text-muted-foreground text-xs">{project.steps.filter((step) => step.status === "completed").length} di {project.steps.length} fasi verificate · Gli specialisti lavorano in sequenza e si passano i file.</p>
      <ol className="space-y-2 text-sm">
        {project.steps.map((step) => <li key={step.id}>
          <div><strong>{step.agent.charAt(0).toUpperCase() + step.agent.slice(1)}</strong> · {stepLabels[step.status] ?? step.status}</div>
          <p>{step.goal}</p>
          {step.depends_on.length > 0 && <p className="text-muted-foreground text-xs">Riceve da: {step.depends_on.join(", ")}</p>}
        </li>)}
      </ol>
      <p className="text-muted-foreground text-xs">Il limite di 25 minuti vale per ogni incarico, non per tutto il progetto. Se una fase si interrompe, i file salvati restano disponibili per una continuazione; i risultati incompleti richiedono verifica.</p>
    </article>}
    {unavailable && <p className="text-sm" role="status">Aggiornamenti non disponibili: l’ultimo stato visibile potrebbe non essere attuale. Riprovo automaticamente.</p>}
    {!jobs.length && pending && <p className="text-muted-foreground text-sm">Delega avviata. In attesa dello stato del worker; le esecuzioni precedenti a questo aggiornamento non hanno una cronologia operativa.</p>}
    {visible.map((job) => <JobCard key={job.job_id} job={job} now={now} />)}
  </section>;
}
