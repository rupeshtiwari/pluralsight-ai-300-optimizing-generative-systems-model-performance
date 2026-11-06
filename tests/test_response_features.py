"""Offline regression for response-only tokenization without model dependencies."""
import importlib.util
import sys
import unittest
from types import SimpleNamespace
from unittest.mock import patch

from ai300.core import ROOT


class TokenizerDouble:
    eos_token = '<eos>'

    def apply_chat_template(self, prompt, *, tokenize, add_generation_prompt,
                            enable_thinking, return_dict=True):
        ids = [11, 12]
        return {'input_ids': ids} if return_dict else ids

    def encode(self, text, *, add_special_tokens):
        return [21, 22, 23]


class ResponseFeaturesTests(unittest.TestCase):
    def test_chat_template_ids_build_response_only_features(self):
        torch = SimpleNamespace(
            tensor=lambda values: values,
            ones=lambda shape, dtype: [[1] * shape[1]],
            long=int,
        )
        transformers = SimpleNamespace(AutoTokenizer=object, AutoModelForCausalLM=object)
        spec = importlib.util.spec_from_file_location('offline_jobs_common', ROOT / 'jobs/common.py')
        module = importlib.util.module_from_spec(spec)
        with patch.dict(sys.modules, {'torch': torch, 'transformers': transformers}):
            spec.loader.exec_module(module)

        tokenizer = TokenizerDouble()
        prompt = [{'role': 'user', 'content': 'Fixture question'}]
        answer = {'answer': 'Fixture answer', 'source_ids': []}
        features = module.response_features(tokenizer, prompt, answer, max_length=5)
        self.assertEqual(features, {
            'input_ids': [[11, 12, 21, 22, 23]],
            'attention_mask': [[1, 1, 1, 1, 1]],
            'labels': [[-100, -100, 21, 22, 23]],
        })
        with self.assertRaisesRegex(ValueError, 'exceeds the fixed token budget'):
            module.response_features(tokenizer, prompt, answer, max_length=4)


if __name__ == '__main__':
    unittest.main()
