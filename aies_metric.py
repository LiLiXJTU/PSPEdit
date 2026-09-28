import json


REQUIRED_EDIT_SPEC_KEYS = ("target", "location", "replacement", "keep", "ambiguity")


def validate_edit_spec(edit_spec):
    missing_keys = [
        key for key in REQUIRED_EDIT_SPEC_KEYS if key not in edit_spec
    ]
    if missing_keys:
        raise ValueError(f"Missing edit_spec keys: {', '.join(missing_keys)}")
    return edit_spec


def build_edit_spec_prompt(instruction):
    return f"""You are extracting a shared image-editing target.

Use only the original image and the user instruction. Ignore all other metadata.

Return only valid JSON with this schema:
{{
  "target": "object or region to edit",
  "location": "where the target appears in the original image",
  "replacement": "requested final object, attribute, or state",
  "keep": "regions and content that should remain unchanged",
  "ambiguity": "any uncertainty that affects scoring"
}}

INSTRUCTION:
{instruction}
"""


def build_image_judge_prompt(edit_spec, candidate_label):
    validate_edit_spec(edit_spec)
    return f"""You are judging the {candidate_label} candidate against the original image.

Use the shared edit spec below. Do not use any agent-only prompt fields.

SHARED_EDIT_SPEC:
{json.dumps(edit_spec, ensure_ascii=False, indent=2)}

Compare the original image and candidate image using visible evidence only.

Score each dimension from 0 to 100:
- replacement_correctness: whether the requested replacement or edit result is present.
- target_localization: whether the edit was applied to the intended object or region.
- preservation: whether non-target content remains visually consistent with the original image.
- visual_quality: whether the edit is natural, coherent, and free of obvious artifacts.

Return only valid JSON with this schema:
{{
  "description": {{
    "target_before": "visible target in the original image",
    "target_after": "visible result in the candidate image",
    "location_match": "whether the edit is in the intended place",
    "preserved_regions": "what appears unchanged",
    "unexpected_changes": "visible unintended changes",
    "uncertainties": "scoring caveats"
  }},
  "scores": {{
    "replacement_correctness": 0,
    "target_localization": 0,
    "preservation": 0,
    "visual_quality": 0
  }},
  "rationale": "brief explanation grounded in visible evidence"
}}
"""


def build_tie_breaker_prompt(edit_spec):
    validate_edit_spec(edit_spec)
    return f"""You are resolving a score tie between two edited images.

Use the shared edit spec below. Compare the original image, baseline image, and agent image using visible evidence only.

SHARED_EDIT_SPEC:
{json.dumps(edit_spec, ensure_ascii=False, indent=2)}

Choose the better edited image. If there is no visible meaningful difference, choose tie.

Return only valid JSON with this schema:
{{
  "winner": "agent|baseline|tie",
  "reason": "brief visual reason",
  "agent_advantage": "visible advantage or none",
  "baseline_advantage": "visible advantage or none"
}}
"""


def extract_json_object(raw_output):
    decoder = json.JSONDecoder()
    for index, character in enumerate(raw_output):
        if character != "{":
            continue
        try:
            parsed, _ = decoder.raw_decode(raw_output[index:])
        except json.JSONDecodeError:
            continue
        if isinstance(parsed, dict):
            return parsed
    raise ValueError("No valid JSON object found in model output")
