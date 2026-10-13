# Editorial and technical review

## Project profile

- Document type: educational descriptions, procedures, reference notes, and exercises.
- Reader: a beginner who progresses toward model training and evaluation engineering.
- Spelling: US English. Official names, code identifiers, and source titles retain their original form.
- Terminology: the notebook glossary and primary-source terminology.
- Writing guide: [Controlled Technical English](https://github.com/Prathmesh333/controlled-technical-english-writing-skill/blob/e6cb28449d07ffe8f20b8055ff6cf027705d41cd/SKILL.md).
- House rules: short sentences, direct steps, explicit conditions, and consistent terms. Sentence targets are review triggers rather than claims of compliance.

## Scope and evidence

The curriculum focuses on language models and their surrounding systems. It introduces wider concerns such as multimodal preprocessing and distribution shift. It does not claim to cover every AI subfield, every benchmark, or undisclosed lab processes.

Public lab practices are attributed to dated sources. The suggested multi-stage evaluation program is labeled as a teaching synthesis. Dataset fixtures and stored model predictions are explicitly synthetic. Token prices in the calculator are illustrative inputs.

## Technical checks

- Confirmed metric formulas and the Wilson interval against the linked statistical reference.
- Distinguished pass@k estimation from the independent-attempt probability model in the calculator.
- Preserved the roles of training, validation, and test data.
- Kept missing predictions in the evaluation denominator.
- Distinguished the character-model unit from the transformer's byte-level unit.
- Verified causal masking by changing future input bytes and checking that earlier logits did not change.
- Executed the character-model lab and the stored-prediction evaluation lab.
- Executed 50 transformer steps with PyTorch 2.6.0+cpu. This checks the path, not useful language capability.
- Reviewed SVG data-flow directions, labels, and captions.

## Limits of this review

The notebooks use small examples to teach experimental design. No new frontier-model benchmark scores were measured. Statistical intervals rely on the stated sampling assumptions. Source pages and software interfaces can change after the review date.

The writing guide improves clarity. It does not certify this project against ASD-STE100 or another external writing standard.
