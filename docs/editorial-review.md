# Editorial and technical review

## Project profile

- Document type: educational descriptions, procedures, reference notes, and exercises.
- Reader: a beginner who progresses toward model training and evaluation engineering.
- Spelling: US English. Official names, code identifiers, and source titles retain their original form.
- Terminology: the notebook glossary and primary-source terminology.
- Writing guide: [Controlled Technical English](https://github.com/Prathmesh333/controlled-technical-english-writing-skill/blob/e6cb28449d07ffe8f20b8055ff6cf027705d41cd/SKILL.md).
- House rules: short sentences, direct steps, explicit conditions, and consistent terms. Sentence targets are review triggers rather than claims of compliance.

## Scope and evidence

The curriculum covers classical prediction models, language models, multimodal systems, and agents. The expanded edition has 30 chapters and explicit learning outcomes. It does not claim to cover every AI subfield, every benchmark, or undisclosed lab processes.

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

## Completeness audit and expansion

The original 18-chapter edition introduced the lifecycle but lacked depth in several areas. The expansion adds dedicated treatments rather than only renaming the guide:

| Gap | Added coverage |
| --- | --- |
| AI beyond language models | Prediction metrics, cross-validation, forecasting, ranking, clustering, policy evaluation |
| Experimental rigor | Estimands, dependence, power, ablations, rare failures, stopping rules |
| Human evaluation | Rubrics, annotation operations, agreement, ties, preference-model interpretation |
| Reasoning and code | Outcome versus explanation, inference budgets, selection, executable tests, instruction constraints |
| Context and memory | Position and length tests, oracle context, persistence, updates, deletion |
| Multimodal evaluation | Vision, documents, speech error, video sampling, generated media |
| Fairness and access | Group metrics, intersections, languages, accessibility outcomes |
| Measurement science | Validity, reliability, saturation, contamination, item response theory |
| Performance benchmarking | Timing boundaries, workload, load generation, quality constraints, cost and energy |
| Tooling and real outputs | Public-harness walkthrough and a tested chat-completions collector |
| Release operations | Acceptance rules, evidence ownership, artifact access, reevaluation triggers |

The coverage page maps every chapter to an exercise and provides five reading routes. Templates cover dataset documentation, grading, and final reporting. The expanded directory includes 22 benchmark families and suites.

The public-harness command is based on checked documentation. No full external benchmark or hosted-model quality run was performed. The endpoint collector passed local HTTP-fixture tests for label exclusion, malformed responses, failed requests, redirects, output preservation, and metadata. Software test results are not model capability results.
