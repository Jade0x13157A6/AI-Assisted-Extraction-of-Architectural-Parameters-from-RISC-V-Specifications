# Prompt Development and Refinement

## Iteration 1: broad extraction

```text
Extract architectural parameters from the following RISC-V specification.
For each parameter, return its name, description, type, and constraints as
YAML.
```

### Problem identified

The word *parameter* was not defined. A model could therefore mix together:

- implementation-selectable values;
- fixed ISA constants;
- behavioural requirements; and
- facts that are not parameters.

It could also fill gaps using common hardware knowledge. For example, it might
invent a typical cache-block size even though the excerpt contains no number.

## Iteration 2: evidence-grounded extraction

```text
Extract only architectural parameters explicitly supported by the supplied
RISC-V text. Do not use external knowledge and do not invent defaults. Include
a short exact evidence quotation and all explicit constraints for every item.
Return valid YAML only. If a value is missing, use null.
```

### Improvement

Requiring evidence makes each output traceable to the supplied text. Using
`null` gives the model a safe representation for information that the
specification does not state.

### Remaining problem

The prompt still did not distinguish a configurable parameter from a fixed
architectural value. For example, a 12-bit CSR address is important structured
information, but the excerpt does not present its width as an
implementation-specific choice.

The phrase “up to 4,096 CSRs” also creates a specific hallucination risk: the
encoding-space maximum could be incorrectly converted into an exact implemented
CSR count.

## Iteration 3: final prompt

The final prompt adds:

- formal parameter categories;
- a separate place for non-parameter requirements;
- an explicit warning that modal keywords are only candidate signals;
- a rule against converting maximum encoding capacity into implemented count;
- a fixed YAML schema; and
- per-item evidence and confidence fields.

This version is stored in [`final_prompt.md`](final_prompt.md).

## Manual review checklist

After the model produces YAML, each item is reviewed with these questions:

1. Is the item explicitly present in the supplied excerpt?
2. Is its category correct?
3. Does every constraint preserve the original meaning and strength?
4. Has the model invented a value, unit, range, mapping, or default?
5. Has a fixed encoding limit been confused with implemented hardware?
6. Does the evidence directly support the item?
7. Is the YAML syntactically valid and schema-complete?
