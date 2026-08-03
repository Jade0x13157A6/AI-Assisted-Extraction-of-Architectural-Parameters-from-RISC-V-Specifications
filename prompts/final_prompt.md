# Final Extraction Prompt

```text
You are a requirements engineer extracting architectural information from a
RISC-V specification excerpt.

Definitions:
- implementation_parameter: a property whose value is explicitly allowed to
  vary between compliant implementations.
- architectural_constant: a width, value, bit field, or encoding explicitly
  fixed by the specification.
- non_parameter_requirement: a mandatory or descriptive rule that is not
  itself a configurable value.

Extraction rules:
1. Use only the supplied excerpt. Do not use outside RISC-V or hardware
   knowledge.
2. Treat words such as may, might, should, optional, implementation-defined,
   and implementation-specific as candidate signals, not automatic proof.
3. Do not invent defaults, examples, units, ranges, enum values, mappings, or
   implementation choices.
4. Distinguish implementation parameters from fixed architectural constants.
5. Do not convert a maximum encoding capacity into the number of items that an
   implementation must contain.
6. Record every explicit constraint and preserve normative strength. In
   particular, a statement using “shall” is mandatory.
7. Give a short exact evidence quotation for each extracted parameter.
8. If a value is not stated, write value: null. Explain the missing detail in
   constraints only when useful.
9. Use concise snake_case names.
10. If the excerpt has no entries in one category, return an empty list for
    that category. Do not create an item merely to avoid an empty list.
11. Return valid YAML only, with no Markdown fences or commentary.

Required schema:
source:
  document: string
  section: string
parameters:
  - name: string
    description: string
    category: implementation_parameter | architectural_constant
    type: integer | string | enum | bit_field | implementation_defined_structure
    value: any | null
    implementation_specific: boolean
    constraints:
      - string
    evidence:
      - string
    confidence: high | medium | low
non_parameter_requirements:
  - description: string
    evidence: string
excluded_candidates:
  - name: string
    reason: string

Specification excerpt:
{{SPECIFICATION_SNIPPET}}
```
