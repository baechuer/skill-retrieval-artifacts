import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from replay import rank_metrics


class MetricsTests(unittest.TestCase):
    def test_multiple_acceptable_answers(self):
        ranking = list(map(str, range(20)))
        result = rank_metrics(ranking, ranking, {"2", "5"}, {"0", "2", "5"})
        self.assertEqual(result["acceptable_hit_at_1"], 0)
        self.assertEqual(result["candidate_hit_at_20"], 1)
        self.assertEqual(result["mrr_at_20"], 1 / 3)
        self.assertEqual(result["set_recall_at_20"], 1)
        self.assertEqual(result["unjudged_at_1"], 0)

    def test_candidate_presence_is_not_set_recall(self):
        ranking = list(map(str, range(20)))
        result = rank_metrics(ranking, ranking, {"0", "missing"}, {"0"})
        self.assertEqual(result["candidate_hit_at_20"], 1)
        self.assertEqual(result["set_recall_at_20"], .5)

    def test_invalid_permutation_fails(self):
        with self.assertRaises(ValueError):
            rank_metrics(["x"] * 20, ["x"] * 20, {"x"}, {"x"})


if __name__ == "__main__":
    unittest.main()
