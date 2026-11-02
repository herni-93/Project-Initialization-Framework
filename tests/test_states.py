import unittest

from pif.errors import InvalidTransition
from pif.states import State, can_transition, ensure_transition


class StateMachineTests(unittest.TestCase):
    def test_happy_path_is_allowed(self):
        path = ["waiting", "bootstrap", "discovery", "validation", "prd_generation", "prd_review", "completed"]
        for src, dst in zip(path, path[1:]):
            self.assertTrue(can_transition(src, dst), f"{src} -> {dst}")

    def test_discovery_can_be_skipped_but_validation_cannot(self):
        self.assertTrue(can_transition("bootstrap", "validation"))
        self.assertFalse(can_transition("bootstrap", "prd_generation"))
        self.assertFalse(can_transition("discovery", "prd_generation"))

    def test_rejections_go_back_to_discovery(self):
        self.assertTrue(can_transition("validation", "discovery"))
        self.assertTrue(can_transition("prd_review", "discovery"))

    def test_terminal_states_are_final(self):
        for terminal in ("completed", "cancelled"):
            for dst in State:
                self.assertFalse(can_transition(terminal, dst))

    def test_error_and_cancel(self):
        self.assertTrue(can_transition("discovery", "error"))
        self.assertTrue(can_transition("error", "cancelled"))
        self.assertFalse(can_transition("error", "discovery"))  # only via resume

    def test_invalid_transition_raises(self):
        with self.assertRaises(InvalidTransition):
            ensure_transition("waiting", "completed")


if __name__ == "__main__":
    unittest.main()
