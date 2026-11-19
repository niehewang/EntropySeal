import json,sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'))
from entropyseal.claims import profile_distance, owner_decision
from entropyseal.query_budget import ordered_indices

class CoreTests(unittest.TestCase):
    def setUp(self): self.cfg=json.loads((ROOT/'configs/reproduction.json').read_text())
    def test_frozen_carrier_contract(self):
        c=self.cfg['carrier'];self.assertEqual(c['target_indices'],[45,46,47,48,49]);self.assertEqual(c['alpha'],0.03);self.assertEqual(set(c['vectors']),{'K0','K1','K2','K3'})
        self.assertTrue(all(len(v)==5 for v in c['vectors'].values()))
    def test_claim_rule_exact_match(self):
        thresholds=self.cfg['verifier']['thresholds']['K0']; suspect=[1,2,3,4]; profiles={'FP32':[1,2,3,4],'FP16':[2,2,3,4]}
        self.assertTrue(owner_decision(suspect,profiles,thresholds['tau_count'],thresholds['tau_mad'])['accepted'])
        self.assertEqual(profile_distance(suspect,profiles['FP32'],thresholds['tau_count'],thresholds['tau_mad']).mismatch_count,0)
    def test_query_order_deterministic(self):
        h=['0'*64,'1'*64,'2'*64];self.assertEqual(ordered_indices('G0',3,h),ordered_indices('G0',3,h))

if __name__=='__main__':unittest.main()
