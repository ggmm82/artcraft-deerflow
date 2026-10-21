"""Gateway acceptance against the pinned, real DeerFlow storage and Agent loader."""
import os
from pathlib import Path
import tempfile


def main():
    with tempfile.TemporaryDirectory(prefix='native-capabilities-') as folder:
        root = Path(folder)
        os.environ['STUDIO_STATE'] = str(root / 'studio')
        os.environ['DEER_FLOW_HOME'] = str(root / 'home')
        config = root / 'config.yaml'
        config.write_text(Path('/app/backend/studio/deerflow.yaml').read_text())
        os.environ['DEER_FLOW_CONFIG_PATH'] = str(config)
        os.environ['DEER_FLOW_EXTENSIONS_CONFIG_PATH'] = str(root / 'extensions.json')
        from deerflow.config import get_app_config
        from deerflow.config.paths import get_paths
        from deerflow.skills.storage import get_or_new_user_skill_storage
        from deerflow.persistence.agents import get_agent_store
        from studio.capability_policy import native_policy, stage_skills, install_managed_skills, migrate_existing_users
        from studio.state import update_agent
        assert get_app_config().agents_api.enabled is True
        install_managed_skills()
        update_agent('blender', {'engine': 'inherit', 'enabled': False})
        one, two = 'native-policy-a', 'native-policy-b'
        for user in (one, two):
            get_paths().user_dir(user).mkdir(parents=True, exist_ok=True)
        migrate_existing_users()
        assert (get_paths().user_dir(one) / 'artcraft-native-skills-migrated.json').is_file()
        assert 'blender' in native_policy(one)['blocked']
        store = get_or_new_user_skill_storage(one)
        # An unrelated user-authored skill must not hide the managed CLI skills.
        custom = store.get_custom_skill_dir('custom-method'); custom.mkdir(parents=True)
        (custom / 'SKILL.md').write_text('---\nname: custom-method\ndescription: A native custom method\n---\nUse a representative sample.\n')
        assert 'freecad' in native_policy(one)['allowed']
        store.set_skill_enabled_state('artcraft-blender', True)
        assert 'blender' in native_policy(one)['allowed']
        assert 'blender' in native_policy(two)['blocked']
        agents = get_agent_store()
        agents.create('cad-profile', {'name': 'cad-profile', 'skills': ['artcraft-workspace', 'artcraft-freecad']},
                      'Use native parametric CAD when pertinent.', user_id=one)
        selected = native_policy(one, 'cad-profile')
        assert selected['allowed'] == ['freecad']
        agents.create('no-skills', {'name': 'no-skills', 'skills': []}, '', user_id=one)
        assert native_policy(one, 'no-skills')['allowed'] == []
        # The projection is real package content + references, not just names.
        target = stage_skills(selected, ['artcraft-freecad'], root / 'projection')
        assert (target / 'artcraft-freecad/SKILL.md').read_bytes() == Path(selected['skill_sources']['artcraft-freecad']).joinpath('SKILL.md').read_bytes()
        assert (target / 'artcraft-freecad/references/CLI-RECIPE.md').is_file()
        assert not (target / 'artcraft-blender').exists()
        assert get_paths().user_dir(one) != get_paths().user_dir(two)
        print('Native capability policy OK: legacy migration, user isolation, Agent None/[]/selection and real package projection')


if __name__ == '__main__': main()
