export type JobProgress = {
  resources?: { memory_bytes?: number; memory_limit_bytes?: number; oom_kills?: number };
  limits?: { cpus?: number; memory_mib?: number; model_wait_seconds?: number };
  operations?: { id: string; label: string; state: string; elapsed_seconds?: number; estimate_seconds?: number; oom_kills?: number; progress?: { done?: number; total?: number } }[];
  job_id: string; agent: string; role_id?: string; role_title?: string; role_version?: string; engine: string; model: string; phase: string; summary: string; work_summary: string;
  created_at: string; started_at: string; finished_at: string; deadline_at: string;
  last_activity_at: string; heartbeat_at: string;
  execution_state?: string; execution_started_at?: string; last_model_event_at?: string; last_file_change_at?: string;
  files: { name: string; size: number }[]; files_count: number;
  events: { at: string; phase: string; summary: string }[];
};

export const terminalJob = (job: JobProgress) =>
  ["completed", "failed", "timed_out"].includes(job.phase);

export function secondsSince(value: string, now: number): number | null {
  const time = Date.parse(value);
  return Number.isFinite(time) ? Math.max(0, Math.floor((now - time) / 1000)) : null;
}

export function duration(seconds: number | null): string {
  if (seconds === null) return "non disponibile";
  const minutes = Math.floor(seconds / 60);
  return minutes > 0 ? `${minutes} min ${seconds % 60} s` : `${seconds} s`;
}

export function jobHealth(job: JobProgress, now: number): string | null {
  if (terminalJob(job)) return null;
  if (job.phase === "queued") return "In coda: attesa massima della squadra 2 minuti";
  if (job.phase === "starting" && (secondsSince(job.created_at, now) ?? 0) < 30) return null;
  if (job.deadline_at && Date.parse(job.deadline_at) <= now)
    return "Tempo limite superato: l’esito non è ancora stato ricevuto";
  const heartbeat = secondsSince(job.heartbeat_at, now);
  if (heartbeat === null || heartbeat > 15)
    return "Segnale del worker assente: stato da verificare";
  const activity = secondsSince(job.last_activity_at, now);
  if (activity !== null && activity >= 90)
    return job.execution_state === 'model' || job.phase === 'waiting_model'
      ? `Nessun nuovo avanzamento da ${duration(activity)}: sandbox presente, attesa del modello prolungata. La risposta non è confermata; non è una stima di consegna.`
      : `Nessun nuovo avanzamento da ${duration(activity)}: comando ancora senza esito. La presenza della sandbox non dimostra che il comando avanzi.`;
  return null;
}

export function hasPendingDelegate(messages: readonly {
  type?: string; tool_call_id?: string; tool_calls?: { id?: string; name: string }[];
}[]): boolean {
  const answered = new Set(messages.filter((m) => m.type === "tool").map((m) => m.tool_call_id));
  return messages.some((message) => message.type === "ai" && message.tool_calls?.some(
    (call) => call.name === "studio_delegate" && (!call.id || !answered.has(call.id)),
  ));
}
