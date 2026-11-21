from pathlib import Path
import importlib
import json
import os
import socket
import sys
import tempfile
import unittest
from unittest.mock import patch

PROJECT=Path(os.environ.get('DRESSUP_SOURCE',Path(__file__).resolve().parents[1]))
sys.path.insert(0,str(PROJECT))

class ColorHTTPErrorTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp=tempfile.TemporaryDirectory(prefix='dressup-color-');cls.old=os.getcwd();os.chdir(cls.temp.name)
        cls.api=importlib.import_module('api')
        from fastapi.testclient import TestClient
        cls.Client=TestClient

    @classmethod
    def tearDownClass(cls):
        os.chdir(cls.old);cls.temp.cleanup()

    def request(self, body, failure=None):
        with patch.object(socket.socket,'connect',side_effect=AssertionError('No external connection'))as network,self.Client(self.api.app)as client:
            if failure is None:
                result=client.post('/api/ai/color-analysis',json=body)
            else:
                with patch.object(self.api,'analyze_color_harmony',side_effect=failure):
                    result=client.post('/api/ai/color-analysis',json=body)
            self.assertEqual(network.call_count,0)
            self.assertEqual(result.headers['X-Content-Type-Options'],'nosniff')
            return result

    def test_empty_and_missing_colors_keep_existing_bad_request(self):
        for body in [{'colors':[]},{}]:
            with self.subTest(body=body):
                result=self.request(body)
                self.assertEqual(result.status_code,400)
                self.assertEqual(result.json(),{'detail':'Colors list cannot be empty'})

    def test_normal_color_response_matches_original_golden(self):
        result=self.request({'colors':['blue'],'style_context':'casual'})
        self.assertEqual(result.status_code,200)
        expected=json.loads((Path(__file__).parent/'fixtures/color_blue.json').read_text())
        self.assertEqual(result.json(),expected)

    def test_unexpected_internal_failure_still_maps_to_server_error(self):
        result=self.request({'colors':['blue']},RuntimeError('synthetic internal failure'))
        self.assertEqual(result.status_code,500)
        self.assertEqual(result.json(),{'detail':'synthetic internal failure'})

if __name__=='__main__':
    unittest.main()
