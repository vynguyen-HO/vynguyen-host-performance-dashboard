import unittest
from slot_allocation import resolve_overlaps, clip_to_live, allocate, Slot

H = 3600


class Tests(unittest.TestCase):
    def test_override(self):
        # "9h-18h A" rồi B 13-15, C 15-17, D 17-19  ->  A chỉ còn 9-13
        segs = resolve_overlaps([("A", 9 * H, 18 * H), ("B", 13 * H, 15 * H), ("C", 15 * H, 17 * H), ("D", 17 * H, 19 * H)])
        self.assertEqual([(s.host, s.start / H, s.end / H) for s in segs],
                         [("A", 9, 13), ("B", 13, 15), ("C", 15, 17), ("D", 17, 19)])

    def test_split_middle(self):
        segs = resolve_overlaps([("A", 0, 10 * H), ("B", 4 * H, 6 * H)])
        self.assertEqual([(s.host, s.start / H, s.end / H) for s in segs], [("A", 0, 4), ("B", 4, 6), ("A", 6, 10)])

    def test_clip(self):
        segs = [Slot("A", 10 * H, 12 * H), Slot("B", 12 * H, 23 * H)]
        c = clip_to_live(segs, 9.9 * H, 23.1 * H)
        self.assertAlmostEqual(c[0].start, 9.9 * H)
        self.assertAlmostEqual(c[-1].end, 23.1 * H)

    def test_allocate_scales_to_official(self):
        slots = [Slot("A", 0, 2 * H), Slot("B", 2 * H, 4 * H)]
        series = [(0, H, 10.0), (H, 2 * H, 10.0), (2 * H, 3 * H, 30.0), (3 * H, 4 * H, 30.0)]
        lv = {"start": 0, "end": 4 * H, "official_gmv": 200.0, "series": series}
        r = allocate(slots, [lv])
        self.assertAlmostEqual(r[0]["gmv"], 50.0)
        self.assertAlmostEqual(r[1]["gmv"], 150.0)
        self.assertAlmostEqual(sum(x["gmv"] for x in r), 200.0)
        self.assertAlmostEqual(r[0]["hours"], 2.0)

    def test_partial_bucket(self):
        slots = [Slot("A", 0, 1.5 * H), Slot("B", 1.5 * H, 2 * H)]
        lv = {"start": 0, "end": 2 * H, "official_gmv": 100.0, "series": [(0, H, 50.0), (H, 2 * H, 50.0)]}
        r = allocate(slots, [lv])
        self.assertAlmostEqual(r[0]["gmv"], 75.0)
        self.assertAlmostEqual(r[1]["gmv"], 25.0)


if __name__ == "__main__":
    unittest.main()
