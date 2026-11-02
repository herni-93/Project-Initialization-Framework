import unittest

from pif.uncertainty import FIELDS, READY_THRESHOLD, assess, field_score


class UncertaintyTests(unittest.TestCase):
    def test_weights_sum_to_100(self):
        self.assertEqual(sum(f.weight for f in FIELDS), 100)

    def test_empty_project_is_high_uncertainty(self):
        result = assess({})
        self.assertEqual(result.clarity, 0)
        self.assertEqual(result.level, "high")
        self.assertFalse(result.ready)

    def test_success_criteria_must_be_measurable(self):
        self.assertEqual(field_score("success_criteria", "users are happy with it"), 0.5)
        self.assertEqual(field_score("success_criteria", "100 users within 60 days"), 1.0)
        self.assertEqual(field_score("success_criteria", "al menos cien usuarios activos"), 1.0)

    def test_none_counts_only_for_optional_fields(self):
        self.assertEqual(field_score("constraints", "none"), 1.0)
        self.assertEqual(field_score("objective", "none"), 0.0)

    def test_short_answers_need_detail(self):
        self.assertEqual(field_score("problem", "money"), 0.5)

    def test_ready_needs_threshold_and_critical_fields(self):
        fields = {
            "objective": "Build an invoicing tool",
            "problem": "Designers lose time with invoices",
            "deliverables": "Web MVP with invoicing",
            "success_criteria": "50 paying users in 3 months",
            "expected_result": "Deployed app for beta users",
        }
        result = assess(fields)
        self.assertGreaterEqual(result.clarity, READY_THRESHOLD)
        self.assertTrue(result.ready)
        fields["success_criteria"] = "users like it a lot"
        self.assertFalse(assess(fields).ready)

    def test_gaps_are_ordered_critical_first(self):
        result = assess({"objective": "Build an invoicing tool"})
        self.assertEqual(result.ordered_gaps[:2], ["success_criteria", "deliverables"])


if __name__ == "__main__":
    unittest.main()
