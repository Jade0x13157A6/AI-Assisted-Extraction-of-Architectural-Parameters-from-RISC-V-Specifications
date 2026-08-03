# AI-Assisted Extraction of Architectural Parameters from RISC-V Specifications

## 1. Objective

This project uses a large language model (LLM) to convert natural-language
RISC-V specification excerpts into a structured YAML parameter catalogue. The
goal is information extraction, not RISC-V code generation and not model
training.

The extraction distinguishes between:

- `implementation_parameter`: a value that a compliant implementation may
  choose, such as cache capacity;
- `architectural_constant`: a width, value, bit field, or encoding fixed by the
  specification, such as the 12-bit CSR address;
- `non_parameter_requirement`: a normative statement that constrains behaviour
  but is not itself a configurable value.

This distinction is important because a number appearing in the specification
is not automatically an implementation choice.

## 2. LLM details

| Item | Value |
| --- | --- |
| Provider | OpenAI |
| Model | GPT-5.6 Sol |
| Model identifier | `gpt-5.6-sol` |
| Interface | ChatGPT Work Mode |
| Context window | 1,050,000 tokens |
| Maximum output | 128,000 tokens |
| Knowledge cutoff | 2026-02-16 |
| Date used | 2026-08-03 |
| Temperature / seed | Not exposed by the ChatGPT interface |
| Exact backend snapshot | Not exposed by the ChatGPT interface |

The context-window, output-limit, and knowledge-cutoff values are taken from
the [official OpenAI model page](https://developers.openai.com/api/docs/models/gpt-5.6-sol).
The unavailable interface settings are reported explicitly instead of being
guessed.

## 3. Prompt development

The prompt was refined in three stages. Full versions and the associated
failure analysis are in [`prompts/prompt_iterations.md`](prompts/prompt_iterations.md).

1. **Broad extraction:** requested names, descriptions, types, and constraints.
   This was too ambiguous because fixed constants and implementation choices
   could be mixed together.
2. **Evidence-grounded extraction:** required a quotation for every item and
   prohibited external RISC-V knowledge. This reduced invented defaults such as
   a 64-byte cache block.
3. **Typed extraction:** introduced explicit categories, treated modal keywords
   only as candidate signals, and added rules for encoding-space limits. This
   prevents “up to 4,096 CSR addresses” from becoming the false claim that every
   implementation contains 4,096 CSRs.

The final reusable prompt is in
[`prompts/final_prompt.md`](prompts/final_prompt.md).

## 4. Hallucination controls

- Every parameter must have direct textual evidence.
- No default, unit, range, enumeration, or implementation choice may be added
  from general hardware knowledge.
- `may`, `optional`, and `implementation-specific` are candidate signals, not
  automatic proof that the whole sentence is a parameter.
- Fixed ISA constants and implementation-selectable parameters have separate
  categories.
- A maximum encoding capacity must not be reported as an implemented count.
- Missing information is represented as `null` or stated as unspecified.
- Normative strength is preserved: for example, `shall` is recorded as a
  mandatory constraint.
- The YAML is checked both manually against the source and mechanically with a
  schema-oriented validation script.

## 5. Extraction decisions

### Privileged Specification 19.3.1

The cache capacity, cache organization, and cache-block size are explicitly
implementation-specific and are therefore implementation parameters. The
cache-block size also has explicit power-of-two, natural-alignment, and
system-wide uniformity constraints.

The requirement that the execution environment make cache information
discoverable is recorded as a non-parameter requirement. The excerpt does not
state the discovery mechanism, so none is invented.

### Privileged Specification 2.1

This excerpt does not explicitly identify an implementation-selectable
parameter. It instead fixes a 12-bit CSR address and defines two CSR address
bit fields. These items are retained as `architectural_constant` entries so the
structured output represents the information in the supplied excerpt without
misclassifying it as implementation-specific.

The maximum encoding capacity of 4,096 addresses is not interpreted as a
requirement to implement 4,096 CSRs.

## 6. Files

```text
riscv-parameter-extraction/
├── README.md
├── input/
│   └── snippets.txt
├── prompts/
│   ├── final_prompt.md
│   └── prompt_iterations.md
├── results/
│   └── results.yaml
├── scripts/
│   └── validate_yaml.py
├── .gitignore
└── requirements.txt
```

## 7. Reproduction and validation

To reproduce the extraction, copy the final prompt, replace
`{{SPECIFICATION_SNIPPET}}` with one excerpt from `input/snippets.txt`, and run
the prompt once per excerpt. The submitted output has then been manually
compared with the source text and normalized into `results/results.yaml`.

Validate the submitted YAML with:

```bash
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install -r requirements.txt
python3 scripts/validate_yaml.py results/results.yaml
```

Expected result:

```text
VALID: 2 snippets and 6 parameters checked.
```
