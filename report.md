# AI-Assisted Extraction of Architectural Parameters from RISC-V Specifications

**Author:** Ruijue Luo  
**Date:** 3 August 2026 

---

# Abstract

This report presents an LLM-assisted method for extracting architectural
parameters from RISC-V specification text. The objective is information
extraction rather than RISC-V code generation or model training. The method
distinguishes implementation-selectable parameters from fixed architectural
constants and non-parameter requirements. Hallucination is limited by requiring
source-only reasoning, exact evidence fragments, explicit `null` values for
missing information, and a constrained YAML schema. Applied to the two supplied
excerpts, the final method identifies three implementation-specific cache
parameters and three fixed CSR architectural constants.

# 1. Task and Scope

RISC-V specifications contain both mandatory architectural rules and choices
left to an implementation. Such choices are often indicated by words such as
*may*, *might*, *should*, *optional*, *implementation-defined*, and
*implementation-specific*. Manually finding these choices in a long
specification is slow and may produce inconsistent results.

The purpose of this challenge is therefore to develop prompts that allow a
large language model (LLM) to:

1. read a RISC-V specification excerpt;
2. identify architectural parameters and their constraints;
3. avoid adding information that is not stated in the excerpt; and
4. return the result in a machine-readable YAML format.

The supplied excerpts are:

- RISC-V Privileged Specification Section 19.3.1, concerning cache blocks;
- RISC-V Privileged Specification Section 2.1, concerning conventional CSR
  read/write accessibility encoding.

The workflow used in this project is summarized below.

| Step | Input | Output |
| --- | --- | --- |
| 1. Source preparation | RISC-V excerpts | Clean specification text |
| 2. Prompting | Specification text and extraction rules | LLM response |
| 3. Structuring | LLM response | YAML parameter catalogue |
| 4. Validation | YAML and original excerpts | Checked final result |

# 2. LLM Details

| Item | Value |
| --- | --- |
| Provider | OpenAI |
| Model | GPT-5.6 Sol |
| Model identifier | `gpt-5.6-sol` |
| Interface | ChatGPT Work Mode |
| Context window | 1,050,000 tokens |
| Maximum output | 128,000 tokens |
| Knowledge cutoff | 16 February 2026 |
| Date used | 3 August 2026 |
| Temperature and seed | Not exposed by the ChatGPT interface |
| Exact backend snapshot | Not exposed by the ChatGPT interface |

The context-window, maximum-output, and knowledge-cutoff values are taken from
the [official OpenAI model page](https://developers.openai.com/api/docs/models/gpt-5.6-sol).
Settings that were not exposed by the interface are reported as unavailable
rather than guessed.

# 3. Extraction Ontology

A major difficulty is that not every number or technical property in a
specification is an implementation-selectable parameter. The final prompt uses
three categories.

| Category | Meaning | Example |
| --- | --- | --- |
| `implementation_parameter` | A property whose value is explicitly allowed to vary between compliant implementations. | `cache_block_size` |
| `architectural_constant` | A width, value, bit field, or encoding fixed by the specification. | `csr_address_width: 12` |
| `non_parameter_requirement` | A mandatory or descriptive rule that is not itself a configurable value. | Cache information must be discoverable by software. |

Each extracted parameter contains the following fields:

- `name`: concise snake_case identifier;
- `description`: meaning of the parameter;
- `category`: implementation parameter or architectural constant;
- `type`: integer, string, enum, bit field, or implementation-defined
  structure;
- `value`: explicit value, or `null` if it is not stated;
- `implementation_specific`: whether the implementation selects the value;
- `constraints`: restrictions explicitly given by the text;
- `evidence`: exact supporting fragments from the source;
- `confidence`: extraction confidence.

# 4. Prompt Development

The prompt was developed in three analytical iterations. The changes were based
on ambiguities and hallucination risks found while manually comparing the task
text with a human-created reference annotation. This report does not claim a
large multi-run benchmark; validation is limited to the two supplied excerpts.

## 4.1 Version 1: Broad Extraction

The first prompt was intentionally simple:

```text
Extract architectural parameters from the following RISC-V specification.
For each parameter, return its name, description, type, and constraints as
YAML.
```

This version did not define the word *parameter*. Consequently, it could mix
together implementation choices, fixed ISA constants, behavioural requirements,
and general facts. It also did not explicitly prevent the model from filling
missing values with common hardware knowledge.

## 4.2 Version 2: Evidence-Grounded Extraction

The second version added source grounding:

```text
Extract only architectural parameters explicitly supported by the supplied
RISC-V text. Do not use external knowledge and do not invent defaults. Include
a short exact evidence quotation and all explicit constraints for every item.
Return valid YAML only. If a value is missing, use null.
```

Requiring evidence makes every result traceable to the supplied excerpt. Using
`null` gives the model a safe representation for missing information and avoids
inventing typical values, such as a 64-byte cache block.

However, this version still did not clearly distinguish a fixed architectural
constant from a value that an implementation may select.

## 4.3 Version 3: Typed and Constrained Extraction

The final version introduced:

- explicit semantic categories;
- a separate list for non-parameter requirements;
- a fixed YAML schema;
- exact evidence for every parameter;
- a warning that modal keywords are only candidate signals;
- a rule against converting encoding capacity into implemented hardware count;
- preservation of normative words such as *shall*.

These changes specifically address two risks in the supplied text:

1. the cache-block size must not be replaced by an invented numerical default;
2. “up to 4,096 CSRs” must not be interpreted as requiring every implementation
   to contain 4,096 CSRs.

# 5. Final Prompt

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

# 6. Hallucination-Control Strategy

The following controls were used.

| Risk | Control | Final treatment |
| --- | --- | --- |
| Invented cache-block size | Missing values must be `null`; no external defaults are allowed. | No numerical cache-block size is reported. |
| 4,096 treated as implemented CSR count | Encoding capacity and implementation count are explicitly separated. | 4,096 is recorded only as the upper bound of the encoding space. |
| Invented `csr[9:8]` mapping | Enum mappings absent from the excerpt are prohibited. | The mapping is recorded as `null`. |
| Mandatory rule weakened | Normative strength must be preserved. | System-wide cache-block uniformity remains mandatory. |
| Fixed CSR fields labelled configurable | Fixed constants and implementation parameters use different categories. | CSR fields are classified as architectural constants. |

# 7. Validation Method

Validation combines manual semantic review with deterministic software checks.

## 7.1 Human Reference Annotation

The manually identified reference items are:

| Section | Expected item | Category |
| --- | --- | --- |
| 19.3.1 | `cache_capacity` | Implementation parameter |
| 19.3.1 | `cache_organization` | Implementation parameter |
| 19.3.1 | `cache_block_size` | Implementation parameter |
| 2.1 | `csr_address_width` | Architectural constant |
| 2.1 | `csr_read_write_access_field` | Architectural constant |
| 2.1 | `csr_lowest_privilege_field` | Architectural constant |

The second excerpt does not explicitly state an implementation-selectable
parameter. Its information is retained because the project ontology separately
labels fixed architectural constants.

## 7.2 Software Validation

The YAML file was parsed with Python 3 and PyYAML. The validation script checks:

- valid YAML syntax;
- presence of all required fields;
- allowed parameter categories and types;
- Boolean type of `implementation_specific`;
- consistency between category and implementation-specific status;
- non-empty constraint and evidence lists;
- duplicate parameter names.

In addition, every evidence string was checked against the supplied source text
after whitespace normalization.

The validation result was:

```text
VALID: 2 snippets and 6 parameters checked.
```

## 7.3 Validation Limit

These checks establish that the submitted YAML is structurally valid and
grounded in the two supplied excerpts. They do not demonstrate generalisation
to the complete RISC-V specification or statistical robustness across many
independent LLM runs.

# 8. Results

## 8.1 Cache Parameters: Privileged Specification 19.3.1

| Parameter | Type | Value | Main constraints |
| --- | --- | --- | --- |
| `cache_capacity` | Integer | Not stated | Selected by the implementation; no numerical value, unit, or range is stated. |
| `cache_organization` | Implementation-defined structure | Not stated | Selected by the implementation; no permitted organizations are listed. |
| `cache_block_size` | Integer | Not stated | Power-of-two size; naturally aligned; uniform throughout the system for the initial CMO extensions. |

The cache capacity, cache organization, and cache-block size are explicitly
implementation-specific. The cache-block size also has explicit power-of-two,
natural-alignment, and system-wide uniformity constraints. No numerical cache
size is invented.

## 8.2 CSR Constants: Privileged Specification 2.1

| Parameter | Type | Value | Main constraints |
| --- | --- | --- | --- |
| `csr_address_width` | Integer | 12 | Address field is `csr[11:0]`; encoding space supports up to 4,096 addresses. |
| `csr_read_write_access_field` | Bit field | `csr[11:10]` | `00`, `01`, and `10` mean read/write; `11` means read-only. |
| `csr_lowest_privilege_field` | Bit field | `csr[9:8]` | Encodes the lowest access privilege; individual values are not given in the excerpt. |

The CSR excerpt defines fixed architectural information rather than an
implementation-selectable choice. The 12-bit address and the two bit fields are
therefore marked as `architectural_constant`. The omitted privilege-value
mapping remains `null`.

# 9. Complete YAML Result

```yaml
schema_version: "1.0"
extraction_policy:
  description: >-
    Extract implementation-selectable parameters and explicitly fixed
    architectural constants, while keeping non-parameter requirements separate.
  evidence_required: true
  external_knowledge_allowed: false

snippets:
  - source:
      document: "RISC-V Privileged Specification"
      section: "19.3.1"
      topic: "Cache blocks"
    parameters:
      - name: cache_capacity
        description: "Capacity of a cache."
        category: implementation_parameter
        type: integer
        value: null
        implementation_specific: true
        constraints:
          - "The implementation selects the capacity."
          - "No numeric value, unit, or range is stated in the excerpt."
        evidence:
          - >-
            The capacity and organization of a cache and the size of a cache
            block are both implementation-specific
        confidence: high

      - name: cache_organization
        description: "Organization of a cache."
        category: implementation_parameter
        type: implementation_defined_structure
        value: null
        implementation_specific: true
        constraints:
          - "The implementation selects the organization."
          - "No permitted organizations are enumerated in the excerpt."
        evidence:
          - >-
            The capacity and organization of a cache and the size of a cache
            block are both implementation-specific
        confidence: high

      - name: cache_block_size
        description: "Size of the memory range represented by one cache block."
        category: implementation_parameter
        type: integer
        value: null
        implementation_specific: true
        constraints:
          - "The represented range must have a power-of-two size."
          - "Each represented range must be naturally aligned."
          - >-
            For the initial set of CMO extensions, the size shall be uniform
            throughout the system.
          - "No numeric size or unit is stated in the excerpt."
        evidence:
          - >-
            The capacity and organization of a cache and the size of a cache
            block are both implementation-specific
          - >-
            a contiguous, naturally aligned power-of-two (or NAPOT) range of
            memory locations
          - "the size of a cache block shall be uniform throughout the system"
        confidence: high

    non_parameter_requirements:
      - description: >-
          The execution environment must give software a way to discover cache
          and cache-block information.
        evidence: >-
          the execution environment provides software a means to discover
          information about the caches and cache blocks
      - description: >-
          Any physical address corresponding to the underlying locations can
          identify a cache block.
        evidence: >-
          A cache block is identifed by any of the physical addresses
          corresponding to the underlying memory locations.
    excluded_candidates:
      - name: cache_discovery_mechanism
        reason: >-
          A discovery mechanism must exist, but its form is not described as a
          selectable parameter in the excerpt.

  - source:
      document: "RISC-V Privileged Specification"
      section: "2.1"
      topic: "Conventional CSR read/write accessibility encoding"
    parameters:
      - name: csr_address_width
        description: "Width of the CSR address encoding space."
        category: architectural_constant
        type: integer
        value: 12
        implementation_specific: false
        constraints:
          - "The address field is csr[11:0]."
          - "The encoding space contains at most 4,096 distinct addresses."
          - "The excerpt does not require all 4,096 CSR addresses to be implemented."
        evidence:
          - "a 12-bit encoding space (csr[11:0]) for up to 4,096 CSRs"
        confidence: high

      - name: csr_read_write_access_field
        description: "CSR address field encoding whether a CSR is read/write or read-only."
        category: architectural_constant
        type: bit_field
        value:
          bits: "csr[11:10]"
          width: 2
          encoding:
            "00": read_write
            "01": read_write
            "10": read_write
            "11": read_only
        implementation_specific: false
        constraints:
          - "The field occupies the top two bits of the 12-bit CSR address."
        evidence:
          - >-
            The top two bits (csr[11:10]) indicate whether the register is
            read/write (00,01, or 10) or read-only (11).
        confidence: high

      - name: csr_lowest_privilege_field
        description: "CSR address field encoding the lowest privilege level allowed to access the CSR."
        category: architectural_constant
        type: bit_field
        value:
          bits: "csr[9:8]"
          width: 2
          encoding: null
        implementation_specific: false
        constraints:
          - "The field occupies the next two bits after csr[11:10]."
          - "The individual privilege-level encodings are not given in this excerpt."
        evidence:
          - >-
            The next two bits (csr[9:8]) encode the lowest privilege level that
            can access the CSR.
        confidence: high

    non_parameter_requirements:
      - description: >-
          By convention, csr[11:8] encode CSR read/write accessibility according
          to privilege level.
        evidence: >-
          the upper 4 bits of the CSR address (csr[11:8]) are used to encode the
          read and write accessibility of the CSRs according to privilege level
    excluded_candidates:
      - name: implemented_csr_count
        reason: >-
          The excerpt states the maximum size of the encoding space but does not
          state how many CSRs a particular implementation contains.
```

# 10. Limitations

- Only two supplied excerpts were evaluated; this is not a complete RISC-V
  parameter catalogue.
- The reference annotation was produced by one reviewer, so inter-annotator
  agreement was not measured.
- ChatGPT did not expose temperature, seed, or an exact backend snapshot.
- The current validation does not include repeated independent runs or held-out
  specification excerpts.
- The distinction between fixed constants and implementation parameters is an
  explicit project ontology; downstream users can filter by category.

# References

1. RISC-V International, *The RISC-V Instruction Set Manual, Volume II:
   Privileged Architecture*, supplied excerpts from Sections 19.3.1 and 2.1.
2. OpenAI, *GPT-5.6 Sol Model*,
   <https://developers.openai.com/api/docs/models/gpt-5.6-sol>, accessed
   3 August 2026.
3. PyYAML documentation, <https://pyyaml.org/>.
