"""DeerFlow tool: delegate one task using the specialist's configured CLI."""
from langchain.tools import tool
from deerflow.tools.types import Runtime
from deerflow.config.paths import get_paths
from deerflow.runtime.user_context import resolve_runtime_user_id
from .docker_runtime import delegate
from .projects import archive_plan, create_plan, execute_step, read_project, revise_step
import json


def workspace_for(runtime):
    thread = runtime.config.get('configurable', {}).get('thread_id')
    if not thread:
        raise ValueError('La delega richiede una conversazione DeerFlow')
    user = resolve_runtime_user_id(runtime)
    paths = get_paths()
    paths.ensure_thread_dirs(thread, user_id=user)
    return paths.sandbox_user_data_dir(thread, user_id=user)


@tool('studio_plan', parse_docstring=True)
def studio_plan(runtime: Runtime, brief: str = '', steps_json: str = '',
                project_type: str = 'custom', omissions_json: str = '{}', revise_step_id: str = '',
                archive: bool = False) -> str:
    """Create or read the persistent team plan before multidisciplinary production.

    Without steps_json, read the current plan and resume its unfinished steps.
    All 13 catalog specialists are available. Choose the useful disciplines.
    For an animated audiovisual product use animated_video: PhotoCraft assets,
    EffectCraft animation, SoundCraft audio, FilmCraft final assembly. Only explicit
    user requirements can omit one of these roles, recorded in omissions_json.
    Steps must be topologically ordered; the last one integrates every branch.
    Workers run sequentially on the 4 GB VPS, with separate 25-minute budgets.
    To fix an already completed phase, set revise_step_id and explain the failed
    requirement in brief. Its dependent phases will also require a new validation.
    Archive only when the user abandons the project or requests unrelated new work;
    explain why in brief. Never archive to bypass dependencies or the retry limit.

    Args:
        runtime: Injected DeerFlow runtime.
        brief: Requested result and acceptance criteria.
        steps_json: JSON list of objects with id, agent, goal and depends_on (step IDs).
        project_type: custom for any team from the 13 tools, animated_video for animation with sound.
        omissions_json: JSON object mapping omitted video roles to explicit user requirements.
        revise_step_id: Reopen this phase and invalidate downstream deliveries for a targeted revision.
        archive: Archive an inactive abandoned plan, preserving all files and attempts.
    """
    workspace = workspace_for(runtime)
    if archive:
        value = archive_plan(workspace, brief)
    elif revise_step_id:
        value = revise_step(workspace, revise_step_id, brief)
    else:
        value = create_plan(workspace, brief, json.loads(steps_json), project_type,
                            json.loads(omissions_json)) if steps_json else read_project(workspace)
    return json.dumps({'project': value}, ensure_ascii=False)


@tool('studio_delegate', parse_docstring=True)
def studio_delegate(agent: str, task: str, runtime: Runtime, step_id: str = '') -> str:
    """Delegate an ArtCraft task to a configured Codex, Antigravity or DeepSeek specialist in Docker.

    Use the exact specialist ID from the configured operational catalog in the
    lead instructions. Give input paths, required outputs and acceptance checks.
    Request editable sources and dependencies as downloadable outputs, not only exports.
    Require delivery metadata: format, actual opening app, editability, reopening evidence
    and limitations. A GLB/viewer is not evidence of CADCraft compatibility.
    Specialists share files in this conversation; pass result paths to the next one.
    The runtime assigns a separate output directory per task: request filenames,
    not fixed absolute output locations. Use the paths returned by the specialist.
    Only one specialist runs at a time on the 4 GB profile.
    Create studio_plan for multidisciplinary work and supply its step_id.
    Dependency files are injected automatically and must be used as actual inputs.
    After a partial failure, repeat the same step_id with a targeted continuation:
    the previous output directory is supplied automatically. Maximum three attempts.

    Args:
        agent: Exact specialist ID.
        task: Self-contained instructions, input paths and required deliverables.
        runtime: Injected DeerFlow runtime.
        step_id: Assigned phase in studio_plan; empty only for simple single-discipline work.
    """
    workspace = workspace_for(runtime)
    return execute_step(workspace, agent, task, step_id,
        lambda instructions, started=None: delegate(agent, instructions, workspace,
            tool_call_id=getattr(runtime, 'tool_call_id', None), on_started=started))
