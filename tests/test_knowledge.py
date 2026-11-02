import json
import tempfile
import unittest
from pathlib import Path

from pif.errors import GuardError
from pif.knowledge import KnowledgeConnector, MarkdownSource

SAMPLE = Path(__file__).resolve().parent.parent / "examples" / "sample-knowledge-base"


class KnowledgeConnectorTests(unittest.TestCase):
    def test_disabled_by_env(self):
        connector, disabled = KnowledgeConnector.discover(env={"PIF_KNOWLEDGE": "off"})
        self.assertTrue(disabled)
        self.assertEqual(connector.sources, [])

    def test_nothing_found_means_no_sources(self):
        with tempfile.TemporaryDirectory() as home:
            connector, disabled = KnowledgeConnector.discover(home=home, cwd=home, env={})
            self.assertFalse(disabled)
            self.assertEqual(connector.sources, [])

    def test_auto_detection_requires_consent(self):
        with tempfile.TemporaryDirectory() as home:
            brain = Path(home) / "brain"
            (brain / "skills" / "demo").mkdir(parents=True)
            (brain / "skills" / "demo" / "SKILL.md").write_text("---\ndescription: demo skill\n---\n")
            connector, _ = KnowledgeConnector.discover(home=home, cwd=home, env={})
            self.assertEqual([s.location for s in connector.sources], [str(brain)])
            self.assertTrue(connector.needs_consent)

    def test_explicit_path_is_trusted(self):
        connector, _ = KnowledgeConnector.discover(explicit_paths=[SAMPLE], auto_detect=False, env={})
        self.assertFalse(connector.needs_consent)
        kinds = {s.kind for s in connector.sources}
        self.assertEqual(kinds, {"markdown", "json-graph"})

    def test_explicit_missing_path_is_an_error(self):
        with self.assertRaises(GuardError):
            KnowledgeConnector.discover(explicit_paths=["/does/not/exist"], env={})

    def test_config_file(self):
        with tempfile.TemporaryDirectory() as tmp:
            config = Path(tmp) / "pif.knowledge.json"
            config.write_text(json.dumps({"sources": [{"type": "markdown", "location": str(SAMPLE)}]}))
            connector, _ = KnowledgeConnector.discover(cwd=tmp, home=tmp, env={})
            self.assertEqual(connector.sources[0].origin, "config")

    def test_inventory_and_query(self):
        source = MarkdownSource(SAMPLE, "explicit")
        kinds = {r.kind for r in source.inventory()}
        self.assertTrue({"system_prompt", "skill", "workflow", "knowledge"} <= kinds)
        connector = KnowledgeConnector([source])
        hits = connector.query(["invoicing", "designers"], limit=3)
        self.assertTrue(hits)
        self.assertIn("interviews", hits[0].path)

    def test_select_resources_always_includes_global_instructions(self):
        connector, _ = KnowledgeConnector.discover(explicit_paths=[SAMPLE], auto_detect=False, env={})
        selected = connector.select_resources(["saas", "freelancers", "invoicing"])
        names = [r["resource"] for r in selected]
        self.assertIn("SYSTEM.md", names)
        self.assertIn("saas-mvp-scoping", names)
        for row in selected:
            self.assertTrue(row["reason"])
            self.assertEqual(row["status"], "proposed")


if __name__ == "__main__":
    unittest.main()
