"""Bounded completion feedback through DeerFlow's native agent middleware."""
from typing import NotRequired
from langchain.agents import AgentState
from langchain.agents.middleware import AgentMiddleware
from langchain.agents.middleware.types import hook_config
from langchain_core.messages import AIMessage, SystemMessage
from .audit_middleware import workspace_for
from .audit_log import append
from .completion_policy import needs_continuation
from .projects import read_project, mark_incomplete_turn


def learning_sources(runtime):
    from .tools import experience_root
    from .lessons import pending
    thread = (getattr(runtime, 'config', None) or {}).get('configurable', {}).get('thread_id')
    return pending(experience_root(runtime), limit=3, source_thread=thread, meaningful_only=True) if thread else []


class CompletionState(AgentState):
    studio_production_started: NotRequired[bool]
    studio_completion_nudges: NotRequired[int]
    studio_completion_reminder: NotRequired[str]
    studio_work_generation: NotRequired[int]
    studio_reminded_generation: NotRequired[int]
    studio_learning_nudged: NotRequired[bool]


class ProjectCompletionMiddleware(AgentMiddleware):
    state_schema = CompletionState
    MAX_NUDGES = 2

    def before_agent(self, state, runtime):
        return {'studio_production_started': False, 'studio_completion_nudges': 0, 'studio_completion_reminder': '',
                'studio_work_generation':0, 'studio_reminded_generation':-1, 'studio_learning_nudged':False}

    async def abefore_agent(self, state, runtime):
        return self.before_agent(state, runtime)

    @hook_config(can_jump_to=['model'])
    def after_model(self, state, runtime):
        last = next((m for m in reversed(state.get('messages', [])) if isinstance(m, AIMessage)), None)
        if not last:
            return None
        update = {'studio_completion_reminder': ''}
        if isinstance(getattr(runtime, 'context', None), dict) and runtime.context.get('stop_reason'):
            return update  # Native loop/token/time budgets retain authority.
        if last.tool_calls:
            if any(c['name'] == 'studio_lessons' and (c.get('args',{}).get('lesson_json') or c.get('args',{}).get('dismiss_reason')) for c in last.tool_calls):
                update['studio_learning_nudged'] = True
            if any(c['name'] == 'studio_delegate' and c.get('args', {}).get('purpose', 'work') != 'review'
                   for c in last.tool_calls):
                update['studio_production_started'] = True
                update['studio_work_generation'] = state.get('studio_work_generation',0) + 1
            return update
        # Respect native provider/safety/loop terminalization and parsing errors.
        if last.invalid_tool_calls or any(k in last.additional_kwargs for k in
                ('deerflow_error_fallback', 'model_length_termination', 'safety_termination', 'loop_detection')):
            return update
        if not state.get('studio_production_started'):
            return update  # An explanation or a review-only turn is not new production.
        try:
            root = workspace_for(runtime)
            project = read_project(root)
            continuing = needs_continuation(project)
            count = state.get('studio_completion_nudges', 0)
            unchanged = count > 0 and state.get('studio_work_generation',0) == state.get('studio_reminded_generation',-1)
            # One bounded learning pass at a genuine stopping point, never a
            # render loop or mandatory approval of every observation.
            if (project and (not continuing or count >= self.MAX_NUDGES or unchanged)
                    and not state.get('studio_learning_nudged')
                    and project.get('status') != 'clarifying'
                    and not (project.get('user_control') or {}).get('paused')
                    and (project.get('attention') or {}).get('code') not in ('provider_auth','provider_quota','resource_memory','work_cancelled')):
                sources = learning_sources(runtime)
                if sources:
                    append(root, 'Memoria', 'Valutazione delle lezioni richiesta', 'progress',
                           detail='Una sola valutazione di massimo tre fonti della conversazione; nessuna approvazione automatica di metodi.')
                    return {**update, 'jump_to':'model', 'studio_learning_nudged':True,
                        'studio_completion_reminder':'Prima di chiudere valuta brevemente le osservazioni già conservate con '
                        'studio_lessons(current_project_only=true). Seleziona al massimo tre fonti significative: '
                        + ', '.join(s['id'] for s in sources) + '. Leggi prove e limiti, generalizza solo singole lezioni utili '
                        'o motiva perché non sono trasferibili. Le note tecniche richiedono il test verificabile per attivarsi; '
                        'i metodi di realizzazione richiedono accettazione dell’utente. Non approvare metodi, non inventare prove, '
                        'non rigenerare prodotti né bloccare la consegna per esaurire il backlog. Poi presenta risultato, limiti e prossimo passo reale.'}
            if not continuing:
                return update
            if count >= self.MAX_NUDGES or unchanged:
                mark_incomplete_turn(root)
                append(root, 'Coordinatore', 'Obiettivo non completato', 'failed',
                       detail='Nessuna nuova lavorazione dopo il richiamo; evitate risposte ripetute.' if unchanged else 'Terminati due richiami di completamento; file conservati, nessuna approvazione.')
                return update
            reminder = ('Il turno di produzione sta terminando ma il progetto non è completo. '
                'Prossimo obiettivo registrato: ' + str(project.get('next_action', ''))[:500] + '. '
                'Procedi con la correzione mirata o il completamento già autorizzati, riusando i sorgenti. '
                'Non ripetere campioni equivalenti né rigenerare per un controllo sensoriale indisponibile. '
                'Se serve davvero una decisione/input/budget dell’utente, registra strategy state=needs_user, '
                'stop_reason e user_action concreti e poni la domanda necessaria. Non dichiarare finito il prodotto incompleto.')
            append(root, 'Coordinatore', 'Ripresa del lavoro incompleto', 'progress',
                   detail='Richiamo di completamento ' + str(count + 1) + '/2')
            return {**update, 'jump_to': 'model', 'studio_completion_nudges': count + 1,
                    'studio_reminded_generation':state.get('studio_work_generation',0),
                    'studio_completion_reminder': reminder}
        except (AttributeError, ValueError, OSError):
            return update

    @hook_config(can_jump_to=['model'])
    async def aafter_model(self, state, runtime):
        return self.after_model(state, runtime)

    def augmented(self, request):
        reminder = request.state.get('studio_completion_reminder')
        # Control feedback is request-only: never persist a synthetic user turn
        # or change the immutable user acceptance contract.
        return request.override(messages=[*request.messages, SystemMessage(content=reminder)]) if reminder else request

    def wrap_model_call(self, request, handler):
        return handler(self.augmented(request))

    async def awrap_model_call(self, request, handler):
        return await handler(self.augmented(request))
