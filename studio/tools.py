"""DeerFlow tool: delegate one task using the specialist's configured CLI."""
from langchain.tools import tool
from deerflow.tools.types import Runtime
from deerflow.config.paths import get_paths
from deerflow.runtime.user_context import resolve_runtime_user_id
from .docker_runtime import delegate


@tool('studio_delegate', parse_docstring=True)
def studio_delegate(agent: str, task: str, runtime: Runtime) -> str:
    """Delegate an ArtCraft task to a configured Codex, Gemini or DeepSeek specialist in Docker.

    Use the exact specialist ID from the configured operational catalog in the
    lead instructions. Give input paths, required outputs and acceptance checks.
    Request editable sources and dependencies as downloadable outputs, not only exports.
    Require delivery metadata: format, actual opening app, editability, reopening evidence
    and limitations. A GLB/viewer is not evidence of CADCraft compatibility.
    Specialists share files in this conversation; pass result paths to the next one.
    The runtime assigns a separate output directory per task: request filenames,
    not fixed absolute output locations. Use the paths returned by the specialist.
    Only one specialist runs at a time on the 4 GB profile.

    Args:
        agent: Exact specialist ID.
        task: Self-contained instructions, input paths and required deliverables.
        runtime: Injected DeerFlow runtime.
    """
    thread = runtime.config.get('configurable', {}).get('thread_id')
    if not thread:
        raise ValueError('La delega richiede una conversazione DeerFlow')
    user = resolve_runtime_user_id(runtime)
    paths = get_paths()
    paths.ensure_thread_dirs(thread, user_id=user)
    return delegate(agent, task, paths.sandbox_user_data_dir(thread, user_id=user))
