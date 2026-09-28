# PSPEdit: Quality Assessment Agent

Four-dimensional evaluation of **edited images**, using a shared editing specification derived from the original image and user instruction.

This release replaces the earlier six-dimensional instruction-text prompt, which evaluated a different object.

## Code and Prompts

- [aies_metric.py](aies_metric.py): prompt builders, edit-spec validation, and JSON extraction helper.
- [Shared target extraction](prompts/edit_spec.txt).
- [Four-dimensional image assessment](prompts/image_judge.txt).
- [Optional pairwise tie-breaker](prompts/tie_breaker.txt).
- [Tests](tests/test_aies_metric.py): prompt and edit-spec contracts.

The prompt functions are extracted from the author's existing `zhibiao/aies_metric.py` implementation, with their wording preserved. This release includes prompt construction and JSON parsing, not a complete inference pipeline or overall-score implementation.

## Evaluation Flow

1. Call `build_edit_spec_prompt(instruction)` and pass the text **with the original image** to a multimodal evaluator. Parse its JSON into `edit_spec`, containing `target`, `location`, `replacement`, `keep`, and `ambiguity`.
2. Reuse that specification for every candidate for the sample. Call `build_image_judge_prompt(edit_spec, candidate_label)` and pass the text **with the original image first and the candidate image second** to the evaluator.
3. Parse its JSON response to obtain the four dimension scores and their visual-evidence explanations.

These image inputs follow the original `QwenImageJudge.extract_edit_spec` and `evaluate_candidate` call sites. The stages do not consume the editing agent's instruction or reasoning fields; scoring uses visible image evidence.

The original prompt includes the supplied candidate label, so this interface is not inherently blinded. The optional tie-breaker explicitly refers to baseline and agent images and provides a separate pairwise comparison.

## Four Dimensions

| Dimension | Field | Range |
|---|---|---|
| Editing correctness (RC) | `replacement_correctness` | 0-100 |
| Target localization (TL) | `target_localization` | 0-100 |
| Non-target preservation (P) | `preservation` | 0-100 |
| Visual quality (VQ) | `visual_quality` | 0-100 |

## Usage

The prompt module uses only the Python standard library. Supply a multimodal inference backend separately.

```python
from aies_metric import (
    build_edit_spec_prompt, build_image_judge_prompt,
    extract_json_object,
)

# Send with the original image to your multimodal evaluator.
spec_prompt = build_edit_spec_prompt("Change the left animal to a chicken.")

# After receiving the evaluator's response:
# edit_spec = extract_json_object(spec_response)
# judge_prompt = build_image_judge_prompt(edit_spec, "candidate")
# Send judge_prompt with [original_image, candidate_image].
# assessment = extract_json_object(judge_response)
# dimension_scores = assessment["scores"]
```

No measured result is implied by this example. Record the model identifier, decoding settings, image preprocessing and dataset selection separately for reproducibility.

Run the core tests from the repository root:

```sh
python -m unittest discover -s tests -v
```
