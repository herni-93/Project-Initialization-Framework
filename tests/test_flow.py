import json
import tempfile
import unittest
from pathlib import Path

from pif.documents import check_prd
from pif.cli import main
from pif.errors import GuardError
from pif.metrics import build_report
from pif.orchestrator import Orchestrator
from pif.workspace import Workspace

SAMPLE = Path(__file__).resolve().parent.parent / "examples" / "sample-knowledge-base"
REQUEST = "I want to build a SaaS platform for freelance designers"


class FlowTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.home = self.tmp.name
        self.orch = Orchestrator(Workspace(Path(self.tmp.name) / ".pif"))

    def tearDown(self):
        self.tmp.cleanup()

    def _discover(self):
        answers = {
            "success_criteria": "100 paying users within 6 months",
            "deliverables": "Web MVP with portfolio, invoicing and client portal",
            "problem": "Freelance designers juggle many tools to manage clients and invoices",
            "expected_result": "A deployed web app used by beta designers",
        }
        status = None
        while True:
            status = self.orch.status()
            question = status["next_question"]
            if status["state"] != "discovery" or question is None:
                return status
            status = self.orch.answer(question["field"], answers[question["field"]])

    def test_full_flow_without_knowledge(self):
        status = self.orch.start(REQUEST, auto_detect=False, home=self.home)
        self.assertEqual(status["state"], "bootstrap")
        self.assertEqual(status["next_question"]["field"], "knowledge_source")
        status = self.orch.answer("knowledge_source", "no")
        self.assertEqual(status["state"], "discovery")
        status = self._discover()
        self.assertEqual(status["state"], "validation")
        self.assertTrue(status["ready"])
        status = self.orch.approve()
        self.assertEqual(status["state"], "prd_review")
        prd = self.orch.ws.read("PRD.md")
        self.assertEqual(check_prd(prd), [])
        self.assertIn("No external knowledge base was used.", prd)
        status = self.orch.approve()
        self.assertEqual(status["state"], "completed")
        self.assertIn("status: approved", self.orch.ws.read("PRD.md"))
        handoff = json.loads(self.orch.ws.read("handoff.json"))
        self.assertEqual(handoff["state"], "completed")
        report = build_report(self.orch.ws.load(), self.orch.ws.events())
        self.assertTrue(all(c["ok"] for c in report["checks"]))

    def test_knowledge_is_used_when_given(self):
        self.orch.start(REQUEST, knowledge_paths=[SAMPLE], auto_detect=False, home=self.home)
        self._discover()
        summary = self.orch.ws.read("executive-summary.md")
        self.assertIn("Connected sources", summary)
        self.assertIn("saas-mvp-scoping", summary)
        self.orch.approve()
        self.assertIn("saas-mvp-scoping", self.orch.ws.read("PRD.md"))

    def test_auto_detected_knowledge_asks_consent(self):
        brain = Path(self.home) / "brain"
        brain.mkdir()
        (brain / "INDEX.md").write_text("# Index\n")
        status = self.orch.start(REQUEST, home=self.home)
        self.assertEqual(status["next_question"]["field"], "knowledge_consent")
        status = self.orch.answer("knowledge_consent", "no")
        self.assertEqual(status["knowledge"]["status"], "declined")
        self.assertEqual(status["knowledge"]["sources"], [])

    def test_clear_request_skips_discovery_but_not_validation(self):
        fields = {
            "deliverables": "Web MVP with invoicing and client portal",
            "success_criteria": "50 paying users in 3 months",
            "problem": "Designers lose hours every week on invoices",
            "expected_result": "Deployed app used by beta designers",
        }
        self.orch.start(REQUEST, auto_detect=False, home=self.home, fields=fields)
        status = self.orch.answer("knowledge_source", "no")
        self.assertEqual(status["state"], "validation")
        states = [h["to"] for h in self.orch.ws.load().history]
        self.assertNotIn("discovery", states)
        self.assertIn("validation", states)

    def test_unknown_prefilled_field_is_rejected(self):
        with self.assertRaises(GuardError):
            self.orch.start(REQUEST, auto_detect=False, home=self.home, fields={"budget": "10k"})

    def test_guards(self):
        self.orch.start(REQUEST, auto_detect=False, home=self.home)
        with self.assertRaises(GuardError):
            self.orch.answer("problem", "something")  # knowledge question pending
        self.orch.answer("knowledge_source", "no")
        with self.assertRaises(GuardError):
            self.orch.approve()  # nothing to approve in discovery
        self.orch.summary()  # close discovery early
        with self.assertRaises(GuardError):
            self.orch.approve()  # critical fields missing
        with self.assertRaises(GuardError):
            self.orch.start("another project")  # one initialization at a time

    def test_rejection_and_change(self):
        self.orch.start(REQUEST, auto_detect=False, home=self.home)
        self.orch.answer("knowledge_source", "no")
        self._discover()
        status = self.orch.reject("deliverables are wrong")
        self.assertEqual(status["state"], "discovery")
        status = self.orch.answer("deliverables", "Mobile app with invoicing only")
        self.assertEqual(status["state"], "validation")
        self.assertIn("Mobile app", self.orch.ws.read("executive-summary.md"))
        self.assertEqual(self.orch.ws.load().counters["summary_rejections"], 1)

    def test_error_and_resume(self):
        self.orch.start(REQUEST, auto_detect=False, home=self.home)
        self.orch.answer("knowledge_source", "no")
        self._discover()
        self.orch.bootstrapper.templates_dir = "/missing-templates"
        with self.assertRaises(FileNotFoundError):
            self.orch.approve()
        self.assertEqual(self.orch.status()["state"], "error")
        self.orch.bootstrapper.templates_dir = None
        status = self.orch.resume()
        self.assertEqual(status["state"], "prd_generation")
        status = self.orch.approve()
        self.assertEqual(status["state"], "prd_review")

    def test_new_start_archives_finished_run(self):
        self.orch.start(REQUEST, auto_detect=False, home=self.home)
        self.orch.cancel()
        self.orch.start("Second project about research", auto_detect=False, home=self.home)
        archive = Path(self.tmp.name) / ".pif" / "archive"
        self.assertTrue(any(archive.iterdir()))


class CliTests(unittest.TestCase):
    def test_cli_round_trip(self):
        with tempfile.TemporaryDirectory() as tmp:
            d = str(Path(tmp) / ".pif")
            self.assertEqual(main(["--dir", d, "start", REQUEST, "--no-auto-detect",
                                   "--field", "deliverables=Web MVP with invoicing"]), 0)
            self.assertEqual(main(["--dir", d, "answer", "knowledge_source", "no"]), 0)
            self.assertEqual(main(["--dir", d, "approve"]), 2)  # guard: still in discovery
            self.assertEqual(main(["--dir", d, "metrics", "--format", "md"]), 0)


if __name__ == "__main__":
    unittest.main()
