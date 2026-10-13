import http.server
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import threading
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'labs'))
import collect_predictions as collector


class FixtureHandler(http.server.BaseHTTPRequestHandler):
    seen = []

    def log_message(self, *args):
        pass

    def do_POST(self):
        payload = json.loads(self.rfile.read(int(self.headers['Content-Length'])))
        self.seen.append(payload)
        prompt = payload['messages'][-1]['content']
        if prompt == 'http-error':
            self.send_response(503); self.end_headers(); self.wfile.write(b'Private provider error body'); return
        if prompt == 'redirect':
            self.send_response(307); self.send_header('Location', '/unexpected'); self.end_headers(); return
        self.send_response(200); self.send_header('Content-Type', 'application/json'); self.end_headers()
        if prompt == 'bad-json':
            self.wfile.write(b'not-json'); return
        result = {'choices': [{'message': {'content': '4'}, 'finish_reason': 'stop'}],
                  'model': 'test-fixture', 'usage': {'completion_tokens': 1}}
        if prompt == 'bad-schema': result = {'choices': []}
        self.wfile.write(json.dumps(result).encode())


class CollectorTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = http.server.ThreadingHTTPServer(('127.0.0.1', 0), FixtureHandler)
        cls.worker = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.worker.start()
        cls.base = f'http://127.0.0.1:{cls.server.server_port}/v1'

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown(); cls.server.server_close(); cls.worker.join()

    def case(self, name):
        return {'id': name, 'input': name, 'expected': 'HIDDEN-ANSWER', 'slice': 'PRIVATE-SLICE'}

    def test_labels_never_sent_and_tokens_declared(self):
        predictions, attempts = collector.collect([self.case('ok')], 'fixture', self.base, api_key='test-secret', max_tokens=16)
        self.assertEqual(predictions, {'ok': '4'})
        sent = FixtureHandler.seen[-1]
        self.assertNotIn('HIDDEN-ANSWER', json.dumps(sent))
        self.assertNotIn('PRIVATE-SLICE', json.dumps(sent))
        self.assertNotIn('test-secret', json.dumps(attempts))
        self.assertEqual(sent['max_tokens'], 16)
        self.assertFalse(sent['stream'])
        self.assertGreaterEqual(attempts[0]['request_seconds'], 0)

    def test_failures_preserved_and_collection_continues(self):
        names = ['http-error', 'bad-json', 'bad-schema', 'ok']
        predictions, attempts = collector.collect([self.case(n) for n in names], 'fixture', self.base)
        self.assertEqual(predictions, {'ok': '4'})
        self.assertEqual(len(attempts), 4)
        self.assertEqual(sum(a['status'] == 'failed' for a in attempts), 3)
        self.assertNotIn('Private provider error body', json.dumps(attempts))

    def test_redirect_is_not_followed(self):
        before = len(FixtureHandler.seen)
        predictions, attempts = collector.collect([self.case('redirect')], 'fixture', self.base)
        self.assertEqual(predictions, {})
        self.assertEqual(len(FixtureHandler.seen) - before, 1)
        self.assertEqual(attempts[0]['error'], 'HTTP 307')

    def test_rejects_credentials_in_url(self):
        for url in ['https://user:secret@example.org/v1', 'https://example.org/v1?key=secret', 'https://example.org/#secret']:
            with self.assertRaises(ValueError): collector.endpoint_url(url)

    def test_remote_cleartext_rejected(self):
        with self.assertRaises(ValueError): collector.endpoint_url('http://example.org/v1')

    def test_invalid_budget_rejected(self):
        with self.assertRaises(ValueError): collector.collect([], 'fixture', self.base, timeout=0)
        with self.assertRaises(ValueError): collector.collect([], 'fixture', self.base, timeout=float('nan'))

    def test_cli_writes_evidence_and_prevents_overwrite(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            cases = root / 'cases.jsonl'
            cases.write_text(json.dumps(self.case('ok')), encoding='utf-8')
            args = [sys.executable, str(ROOT/'labs/collect_predictions.py'), '--model', 'fixture',
                    '--base-url', self.base, '--cases', str(cases), '--output', str(root/'run')]
            result = subprocess.run(args, capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            manifest = json.loads((root/'run/manifest.json').read_text())
            self.assertEqual(manifest['successful_responses'], 1)
            self.assertEqual(manifest['case_count'], 1)
            self.assertNotIn('HIDDEN-ANSWER', json.dumps(manifest))
            repeat = subprocess.run(args, capture_output=True, text=True)
            self.assertNotEqual(repeat.returncode, 0)
            self.assertIn('already contains a run', repeat.stderr)


if __name__ == '__main__': unittest.main()
