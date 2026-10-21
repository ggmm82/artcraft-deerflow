"""Read immutable project references without opening the host filesystem."""
import re
from pathlib import Path
from .project_skills import read_document


def read_context(workspace, path, sha256, offset=0):
    relative = Path(path).relative_to('/mnt/user-data/.studio-project')
    if (not relative.parts or relative.parts[0] not in ('control-results', 'learning-results', 'roles', 'requests')
            or '..' in relative.parts or not re.fullmatch('[0-9a-f]{64}', sha256)
            or type(offset) is not int or offset < 0):
        raise ValueError('Riferimento di contesto non valido')
    local = Path(workspace) / '.studio-project' / relative
    if local.is_symlink() or not local.is_file() or local.stat().st_size > 1000000:
        raise ValueError('Documento di contesto mancante o troppo grande')
    text = read_document(workspace, {'path':path, 'sha256':sha256})
    if offset > len(text):
        raise ValueError('Offset oltre la fine del documento')
    end = min(offset + 6000, len(text))
    return {'path':path, 'sha256':sha256, 'offset':offset, 'content':text[offset:end],
            'next_offset':end if end < len(text) else None, 'total_characters':len(text)}
