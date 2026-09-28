# PSPEdit: Instruction Quality Assessment Prompt

This repository contains the author-provided prompt for assessing agent-generated image editing instructions in the PSPEdit project.

## Prompt

See [instruction_quality_assessment.txt](prompts/instruction_quality_assessment.txt).

The prompt evaluates instruction text along six dimensions, each scored from 0 to 5:

1. Implicit intent reasoning
2. Functional edit correctness
3. Executable specificity
4. Target grounding
5. Preservation awareness
6. Hallucination control

It requests a JSON response containing these six scores, an overall score, an error type, and a brief explanation. The template is preserved as supplied by the author, with chat-specific escaping removed.

## Inputs and Scope

The supplied template includes `SIMPLE_INSTRUCTION`, `AGENT_INSTRUCTION`, and `AGENT_REASONING` placeholders. It assesses generated editing instructions, not whether an edited image actually fulfills the instruction. It should therefore be distinguished from an image-output evaluator reporting editing correctness, target localization, preservation, and visual quality on a 0-100 scale.

## Details to Specify Before Reproduction

- The functional-correctness rubric references `REFERENCE_PROMPT`, but the supplied template has no corresponding input block. The reference source and how it is supplied need to be specified.
- The aggregation rule and scale for `overall_score` are not defined in the supplied prompt.
- `AGENT_REASONING` is included as input, but its permitted role in judging the final instruction is not specified.
- No image input is specified in this text template. Image-conditioned evaluation requires documenting any image attached separately by the evaluation code.
- The evaluator model, decoding settings, and sampling procedure must be documented separately to reproduce a particular evaluation.

This prompt release does not include generation code, evaluation results, model weights, or datasets. It does not establish agreement with human judgments.
