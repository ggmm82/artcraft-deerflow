import copy
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from studio import experience, projects, lessons
from studio.project_skills import load_compiled
from studio.source_packages import digest
from test_project_skills import role


class ExperienceTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(); self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name); self.workspace = self.root / 'user-a/project'
        self.library = self.root / 'user-a/library'
        projects.create_plan(self.workspace, 'Un progetto qualsiasi', [
            {'id':'produce','agent':'workspace','goal':'Produrre'},
            {'id':'review','agent':'workspace','goal':'Verificare'}])
        projects.sync_acceptance(self.workspace, ['Richiesta reale'])
        spec = role(); spec['tools'] = ['vectorcraft']
        projects.sync_project_context(self.workspace, [spec])
        self.spec = spec
        out = self.workspace / 'outputs/workspace/artcraft-job-123456abcdef'; out.mkdir(parents=True)
        self.product = out / 'product.svg'; self.product.write_text('<svg/>')
        review = self.workspace / 'outputs/reviewer'; review.mkdir()
        self.report = review / 'quality-review.json'; self.report.write_text('{"fixture":"actual report"}')
        path = self.workspace / '.studio-project/project.json'
        data = json.loads(path.read_text()); self.contract = data['acceptance']['hash']
        data['steps'][0].update(status='completed', attempts=[{
            'status':'completed','validated':True,'role_id':'design','output_dir':str(out),
            'context':{'role':data['roles'][0]['version']},'role_scope':data['roles'][0]['scope'],'output_files':[str(self.product)]}])
        criteria = [{'requirement_id':'a','criterion':'Leggibilità delle etichette nella consegna','method':'structural','status':'passed','evidence':'Etichette lette nel prodotto'},
                    {'requirement_id':'b','criterion':'Risorse collegate portabili','method':'functional','status':'failed','evidence':'Risorsa collegata mancante'},
                    {'requirement_id':'c','criterion':'Qualità estetica','method':'visual','status':'not_run','evidence':'Visione assente'}]
        data['steps'][1].update(status='completed', attempts=[{'status':'completed','validated':True,'finished_at':'2026-10-20T01:00:00Z',
            'quality_review':{'product_path':str(self.product),'sha256':digest(self.product),'report_path':str(self.report),
             'contract_hash':self.contract,'criteria':criteria,'revision_actions':[{'requirement_id':'b','action':'Includere le risorse e riaprire il pacchetto estratto'}]}}])
        path.write_text(json.dumps(data));self.state = path

    def propose(self, sources=None):
        sources = sources or [r['id'] for r in experience.entries(self.library)]
        return lessons.learn(self.library, sources, {
            'title': 'Riaprire il pacchetto completo',
            'applies_when': 'Quando una consegna modificabile dipende da risorse collegate',
            'procedure': ['Includere le dipendenze nel pacchetto', 'Estrarre in una cartella nuova e riaprire il progetto'],
            'verification': ['Controllare che tutte le risorse siano risolte senza percorsi esterni'],
            'limits': 'Una verifica strutturale non prova la qualità estetica', 'tools': ['vectorcraft']})

    def test_capture_preserves_observed_failures_and_successes_but_not_missing_checks(self):
        self.assertEqual(experience.collect(self.workspace, self.library, 'thread-a'), 2)
        self.assertEqual(experience.collect(self.workspace, self.library, 'thread-a'), 0)
        records = experience.entries(self.library)
        self.assertEqual({r['observation']['status'] for r in records}, {'passed','failed'})
        self.assertTrue(any(r['observation']['corrections'] for r in records))
        self.assertEqual(records[0]['observation']['source_thread'],'thread-a')
        self.assertEqual(experience.entries(self.root/'user-b/library'), [])
        self.assertEqual((self.library/(records[0]['id']+'.json')).stat().st_mode & 0o777, 0o600)

    def test_next_project_compiles_relevant_experience_with_provenance_and_exclusions(self):
        experience.collect(self.workspace,self.library)
        proposal = self.propose()
        self.assertEqual(experience.select(self.library,[self.spec],projects.applications()), [])
        lessons.accept(self.library, proposal)
        other=self.root/'user-a/other'
        projects.create_plan(other,'Altro dominio',[]);projects.sync_acceptance(other,['Altro progetto'])
        projects.sync_project_context(other,[self.spec],experience_root=self.library)
        compiled=projects.read_project(other)['roles'][0]; text=load_compiled(other,compiled)
        self.assertIn('Riaprire il pacchetto completo',text)
        self.assertNotIn('Risorsa collegata mancante',text);self.assertNotIn('product_sha256',text)
        self.assertNotIn('Etichette lette nel prodotto',text)
        self.assertEqual(compiled['experience']['count'],1)
        first=compiled['version']
        for record in experience.entries(self.library):experience.exclude(self.library,record['id'])
        projects.sync_project_context(other,experience_root=self.library)
        compiled=projects.read_project(other)['roles'][0]
        self.assertEqual(compiled['experience']['count'],0);self.assertNotEqual(compiled['version'],first)
        self.assertEqual(len(experience.entries(self.library)),2)

    def test_explicit_preference_preserves_method_without_marking_checks_or_project_ready(self):
        before=json.loads(self.state.read_text())
        identifier=experience.prefer(self.workspace,self.library,'artcraft-job-123456abcdef',
            'Cambiare metodo dopo il campione e verificare due casi diversi','thread-a')
        self.assertEqual(json.loads(self.state.read_text()).get('status'),before.get('status'))
        record=experience.entries(self.library)[0]
        self.assertEqual(record['id'],identifier)
        self.assertEqual(record['observation']['status'],'preferred_by_user')
        self.assertEqual(record['observation']['files'][0]['sha256'],digest(self.product))
        self.assertEqual(experience.select(self.library,[self.spec],projects.applications()),[])
        proposal = self.propose([identifier])
        self.assertEqual(experience.select(self.library,[self.spec],projects.applications()),[])
        lessons.accept(self.library, proposal)
        selected = experience.select(self.library,[self.spec],projects.applications())[0]
        self.assertEqual(selected['source_statuses'], ['preferred_by_user'])
        self.assertEqual(selected['id'], proposal)
        self.assertEqual(experience.prefer(self.workspace,self.library,'artcraft-job-123456abcdef',
            'Cambiare metodo dopo il campione e verificare due casi diversi','thread-a'),identifier)
        self.assertEqual(len(experience.entries(self.library)),1)
        with self.assertRaises(ValueError):
            experience.prefer(self.workspace,self.library,'missing','Un metodo non verificato')

    def test_old_review_is_retained_after_the_user_changes_the_current_brief(self):
        projects.sync_acceptance(self.workspace,['Richiesta reale','Nuova modifica del brief'])
        self.assertEqual(experience.collect(self.workspace,self.library),2)
        self.assertTrue(all(r['observation']['contract_hash']==self.contract for r in experience.entries(self.library)))

    def test_version_relevance_tampering_and_changed_product(self):
        experience.collect(self.workspace,self.library)
        proposal = self.propose(); lessons.accept(self.library, proposal)
        apps=copy.deepcopy(projects.applications())
        next(a for a in apps if a['id']=='vectorcraft')['version']='future'
        self.assertEqual(experience.select(self.library,[self.spec],apps),[])
        unrelated=role();unrelated['tools']=['soundcraft']
        self.assertEqual(experience.select(self.library,[unrelated],projects.applications()),[])
        self.product.write_text('changed after review')
        self.assertEqual(experience.collect(self.workspace,self.root/'changed-library'),0)
        record=experience.entries(self.library)[0];path=self.library/(record['id']+'.json')
        record['observation']['status']='invented';path.write_text(json.dumps(record))
        self.assertEqual(len(experience.entries(self.library)),1)

    def test_report_changes_and_unknown_producer_scope_do_not_become_reusable_experience(self):
        data=json.loads(self.state.read_text())
        data['steps'][1]['attempts'][0]['quality_review']['report_sha256']=digest(self.report)
        self.state.write_text(json.dumps(data));self.report.write_text('modified report')
        self.assertEqual(experience.collect(self.workspace,self.library),0)
        data['steps'][1]['attempts'][0]['quality_review'].pop('report_sha256')
        data['steps'][0]['attempts'][0].pop('role_scope')
        data['steps'][0]['attempts'][0]['context']['role']='unknown-version'
        self.state.write_text(json.dumps(data))
        self.assertEqual(experience.collect(self.workspace,self.library),2)
        self.assertEqual(experience.select(self.library,[self.spec],projects.applications()),[])

    def test_no_experience_is_inferred_from_successful_command_or_unvalidated_review(self):
        data=json.loads(self.state.read_text());data['steps'][1]['attempts'][0]['validated']=False
        self.state.write_text(json.dumps(data))
        self.assertEqual(experience.collect(self.workspace,self.library),0)
        self.assertEqual(experience.summary(self.library)['total'],0)

    def test_actual_method_record_keeps_script_identity_but_remains_a_declared_recipe(self):
        out=self.product.parent; (out/'work').mkdir()
        script=out/'work/compose.py';script.write_text('print("fixture")')
        (out/'work/method.json').write_text(json.dumps({'approach':'Composizione con asset e lettering separato',
            'steps':['Preparare gli asset','Comporre e riaprire'],'scripts':[str(script)],'limits':['Creazione immagini non registrata']}))
        identifier=experience.prefer(self.workspace,self.library,out.name,'Conserva questo approccio')
        record=next(r for r in experience.entries(self.library) if r['id']==identifier)
        method=record['observation']['producer_method']
        self.assertEqual(method['status'],'reported');self.assertEqual(method['scripts'][0]['sha256'],digest(script))
        self.assertIn('non rieseguito',method['notice'])

    def test_a_pre_update_success_is_recovered_after_roles_have_been_recompiled(self):
        data=json.loads(self.state.read_text());data['steps'][0]['attempts'][0].pop('role_scope')
        self.state.write_text(json.dumps(data))
        projects.sync_project_context(self.workspace,memory={'later':'Subsequent project stage'})
        identifier=experience.prefer(self.workspace,self.library,'artcraft-job-123456abcdef','Metodo preferito della prima lavorazione')
        record=next(r for r in experience.entries(self.library) if r['id']==identifier)
        self.assertTrue(record['observation']['scope_known'])
        self.assertIn('vectorcraft',record['observation']['tools'])
        self.assertEqual(experience.select(self.library,[self.spec],projects.applications()), [])
        proposal = self.propose([identifier]); lessons.accept(self.library, proposal)
        self.assertTrue(experience.select(self.library,[self.spec],projects.applications()))

    def test_acceptance_is_individual_revocable_and_bound_to_the_exact_proposal(self):
        experience.collect(self.workspace, self.library)
        ids = [r['id'] for r in experience.entries(self.library)]
        first = self.propose([ids[0]])
        second = self.propose([ids[1]])
        self.assertEqual(experience.select(self.library, [self.spec], projects.applications()), [])
        lessons.accept(self.library, first)
        self.assertEqual([r['id'] for r in experience.select(self.library,[self.spec],projects.applications())], [first])
        self.assertFalse(next(r for r in experience.summary(self.library)['lessons'] if r['id']==second)['accepted'])
        lessons.accept(self.library, first, False)
        self.assertEqual(experience.select(self.library,[self.spec],projects.applications()), [])
        with self.assertRaises(ValueError): lessons.accept(self.library, ids[0])
        with self.assertRaises(ValueError): lessons.accept(self.root/'user-b/library', first)
        self.assertEqual(len(experience.entries(self.library)), 2)

    def test_structural_guards_and_dismissal_keep_unhelpful_sources_out_of_skills(self):
        experience.collect(self.workspace,self.library)
        proposal = self.propose()
        lesson = lessons.entries(self.library)[0]['basis']['lesson']
        source = experience.entries(self.library)[0]['id']
        for text in ['/mnt/user-data/outputs/project.svg', 'project '+source, 'token sk-'+'a'*35]:
            bad = {**lesson, 'title': text}
            with self.subTest(text=text[:20]), self.assertRaises(ValueError): lessons.learn(self.library,[source],bad)
        with self.assertRaises(ValueError): lessons.learn(self.library,['f'*64],lesson)
        self.assertEqual(lessons.pending(self.library), [])
        record = self.library/'lessons'/(proposal+'.json')
        data=json.loads(record.read_text());data['basis']['lesson']['title']='Altered';record.write_text(json.dumps(data))
        self.assertEqual(lessons.entries(self.library), [])
        lessons.dismiss(self.library,[source],'Osservazione specifica senza lezione trasferibile')
        self.assertNotIn(source, [r['id'] for r in lessons.pending(self.library)])
        self.assertEqual(len(experience.entries(self.library)),2)
        self.assertEqual(experience.select(self.library,[self.spec],projects.applications()), [])
