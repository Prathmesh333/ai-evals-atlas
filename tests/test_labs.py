import importlib.util
import json
import math
from pathlib import Path
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]


def module(name):
    spec=importlib.util.spec_from_file_location(name,ROOT/'labs'/f'{name}.py')
    mod=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


evaluation=module('evaluate')
lm=module('tiny_lm')


class MetricTests(unittest.TestCase):
    def test_wilson_reference(self):
        lo,hi=evaluation.wilson(80,100)
        self.assertAlmostEqual(lo,.7111708344,places=8)
        self.assertAlmostEqual(hi,.8666330667,places=8)

    def test_wilson_extremes(self):
        self.assertAlmostEqual(evaluation.wilson(0,10)[0],0)
        self.assertAlmostEqual(evaluation.wilson(10,10)[1],1)

    def test_wilson_rejects_invalid_counts(self):
        for successes,total in [(1,0),(11,10),(-1,10),(1.5,10)]:
            with self.assertRaises(ValueError):evaluation.wilson(successes,total)

    def test_missing_prediction_is_failure(self):
        cases=[{'id':'x','input':'x','expected':'4','slice':'math'}]
        row=evaluation.score(cases,{})[0]
        self.assertFalse(row['pass'])
        self.assertEqual(row['status'],'missing')

    def test_normalization_does_not_extract_embedded_answer(self):
        cases=[{'id':'x','expected':'4'}]
        self.assertFalse(evaluation.score(cases,{'x':'The answer is 4'})[0]['pass'])
        self.assertTrue(evaluation.score(cases,{'x':' 4 '})[0]['pass'])

    def test_unknown_ids_rejected(self):
        with self.assertRaises(ValueError):evaluation.score([{'id':'x','expected':'4'}],{'y':'4'})

    def test_nonstring_answer_rejected(self):
        with self.assertRaises(ValueError):evaluation.score([{'id':'x','expected':'4'}],{'x':4})

    def test_duplicate_ids_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            file=Path(directory)/'cases.jsonl'
            row=json.dumps({'id':'a','input':'Question','expected':'1','slice':'math'})
            file.write_text(row+'\n'+row,encoding='utf-8')
            with self.assertRaises(ValueError):evaluation.load_cases(file)

    def test_identical_paired_results_have_zero_difference(self):
        result=evaluation.paired_bootstrap([True,False],[True,False],100)
        self.assertEqual(result['candidate_minus_baseline'],0)
        self.assertEqual(result['percentile_bootstrap_95'],[0,0])

    def test_teaching_fixture(self):
        cases=evaluation.load_cases(ROOT/'labs/data/cases.jsonl')
        baseline=evaluation.score(cases,json.loads((ROOT/'labs/data/baseline.json').read_text()))
        candidate=evaluation.score(cases,json.loads((ROOT/'labs/data/candidate.json').read_text()))
        self.assertEqual(evaluation.aggregate(baseline)['passed'],7)
        self.assertEqual(evaluation.aggregate(candidate)['passed'],10)
        self.assertEqual(evaluation.aggregate(candidate)['missing'],1)


class LanguageModelTests(unittest.TestCase):
    def test_probability_loss(self):
        vocab,counts,unigram=lm.fit('abab')
        result=lm.evaluate('ab',vocab,counts,unigram,1)
        self.assertAlmostEqual(result['nll_nats_per_character'],-math.log(3/5))

    def test_unknowns_are_reported(self):
        vocab,counts,unigram=lm.fit('abab')
        result=lm.evaluate('az',vocab,counts,unigram,1)
        self.assertEqual(result['unknown_rate'],.5)
        self.assertTrue(math.isfinite(result['perplexity']))


if __name__=='__main__':unittest.main()
