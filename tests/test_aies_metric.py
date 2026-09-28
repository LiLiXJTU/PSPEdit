import json
import unittest

from aies_metric import (
    build_edit_spec_prompt,
    build_image_judge_prompt,
    build_tie_breaker_prompt,
    extract_json_object,
)


class ImageAssessmentTests(unittest.TestCase):
    def test_shared_spec_and_four_dimension_response_contract(self):
        instruction = 'Change the left animal to a chicken.'
        prompt = build_edit_spec_prompt(instruction)
        self.assertIn(instruction, prompt)
        spec = extract_json_object(prompt)
        self.assertEqual(set(spec), {'target', 'location', 'replacement', 'keep', 'ambiguity'})
        spec['replacement'] = 'chicken'
        judge_prompt = build_image_judge_prompt(spec, 'candidate')
        self.assertIn(json.dumps(spec, ensure_ascii=False, indent=2), judge_prompt)
        schema = extract_json_object(judge_prompt.split('Return only valid JSON with this schema:', 1)[1])
        self.assertEqual(set(schema['scores']), {
            'replacement_correctness', 'target_localization',
            'preservation', 'visual_quality',
        })
        self.assertIn('Score each dimension from 0 to 100', judge_prompt)
        self.assertIn('visible evidence only', judge_prompt)

    def test_incomplete_spec_rejected(self):
        with self.assertRaises(ValueError):
            build_image_judge_prompt({'target': 'dog'}, 'candidate')

    def test_optional_tie_breaker(self):
        spec = extract_json_object(build_edit_spec_prompt('Remove the bag.'))
        prompt = build_tie_breaker_prompt(spec)
        self.assertIn('baseline image, and agent image', prompt)
        self.assertIn('agent|baseline|tie', prompt)


if __name__ == '__main__':
    unittest.main()
