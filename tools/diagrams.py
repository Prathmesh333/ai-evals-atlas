"""Original, editable SVG teaching diagrams. No external renderer required."""
from html import escape

# Each node: x, y, primary label, secondary label. Each edge: source, target, label.
DIAGRAMS = {
    'foundations': ('The evaluation contract', 'A task reaches the system. The grader compares the result with a predefined success rule.',
        [('Task input','A representative case'),('AI system','Model + instructions'),('Observed result','Output or final state'),('Grader','Apply the success rule'),('Decision','Accept, revise, or test')]),
    'ml-basics': ('Training is a feedback loop', 'The loss compares a prediction with a target. Gradients guide parameter updates; new examples test generalization.',
        [('Training example','Input + target'),('Model','Current parameters'),('Prediction','Compare with target'),('Loss + gradients','Compute the update'),('Optimizer','Change parameters')]),
    'language-models': ('A causal transformer', 'Tokens pass through masked attention and a feed-forward block. Residual paths preserve information. The output predicts the next token.',
        [('Text → tokens','Token identifiers'),('Embeddings','Token + position'),('Attention block','Causal mask + residual'),('Feed-forward block','MLP + residual'),('Logits → softmax','Next-token distribution')]),
    'small-model': ('A small model, a complete experiment', 'Training fits counts. Validation selects smoothing. The frozen choice is evaluated once on test data.',
        [('Training text','Count transitions'),('Candidate models','Smoothing values'),('Validation text','Select lowest loss'),('Frozen model','No more selection'),('Test report','Loss + unknown rate')]),
    'tiny-transformer': ('Inside the neural training step', 'Inputs and shifted targets come from the same sequence. Backpropagation changes weights only on the training path.',
        [('Byte sequence','Input: A B C'),('Causal transformer','Predict B C D'),('Cross-entropy','Target: B C D'),('Backpropagation','Parameter gradients'),('AdamW step','Update the weights')]),
    'post-training': ('Where adaptation enters', 'Pretraining learns a base distribution. Supervised and preference stages modify behavior. Evaluate after each stage.',
        [('Base checkpoint','Pretrained weights'),('Supervised tuning','Desired responses'),('Preference training','Compared responses'),('System assembly','Prompts + retrieval'),('Independent eval','Held-out tasks')]),
    'dataset-design': ('Build splits before optimizing', 'Deduplicate and group related records before splitting. Each split has a different role.',
        [('Raw documents','Provenance + rights'),('Clean + group','Remove leakage paths'),('Training split','Fit parameters'),('Validation split','Choose settings'),('Test split','Final measurement')]),
    'metrics': ('A score needs several views', 'Evaluate correctness, coverage, and operating cost. The release decision uses all three views.',
        [('Task outcomes','Per-case evidence'),('Correctness','Precision / recall'),('Coverage','Answers / requests'),('Operating cost','Latency + resources'),('Decision','Declared tradeoffs')]),
    'statistics': ('A paired comparison', 'Both systems receive the same tasks. Resample matched cases to estimate uncertainty in their difference.',
        [('Same task set','Stable case IDs'),('Baseline A','Score every case'),('Candidate B','Score every case'),('Paired differences','B score − A score'),('Bootstrap interval','Resample task IDs')]),
    'graders': ('Grade, then audit the grader', 'Use deterministic checks where possible. Calibrate subjective scores against independent human labels.',
        [('Candidate output','Untrusted content'),('Code checks','Schema + exact rules'),('Model judge','Narrow rubric'),('Human calibration','Audit disagreements'),('Versioned score','Grader + evidence')]),
    'benchmark-practice': ('A reproducible benchmark run', 'The run manifest fixes model and task conditions. Raw outputs let another evaluator audit the score.',
        [('Run manifest','Versions + budgets'),('Pinned tasks','Dataset revision'),('Model adapter','Exact prompt format'),('Outputs + grader','Keep raw evidence'),('Result bundle','Scores + configuration')]),
    'rag-agents': ('Retrieval and the agent loop', 'The agent selects a tool, reads its observation, and can repeat. A final-state grader checks the outcome.',
        [('User task','Goal + permissions'),('Agent controller','Model + context'),('Tool / retrieval','Search or act'),('Observation','Evidence + new state'),('Outcome grader','Inspect final state')]),
    'safety-robustness': ('Test the full safeguard boundary', 'A request passes through controls before and after the model. Evaluate allowed requests and disallowed requests separately.',
        [('Test requests','Allowed + disallowed'),('Input controls','Identity + permissions'),('Model + tools','Restricted environment'),('Output controls','Policy + monitoring'),('Audit outcomes','Failures + overrefusal')]),
    'frontier-labs': ('Layers of evaluation evidence', 'This is a teaching synthesis of public methods, not a diagram of any lab’s private process.',
        [('Development checks','Frequent regressions'),('Capability suites','Broad task coverage'),('Targeted risk tests','Elicitation + safeguards'),('Release review','Evidence + limitations'),('Deployment signals','Monitor + investigate')]),
    'scaling-training': ('Distributed training in context', 'Data feeds workers. Workers coordinate updates. Checkpoints support recovery and separate evaluation.',
        [('Versioned corpus','Tokenized shards'),('Worker group','Parallel computation'),('Synchronization','Gradients / parameters'),('Checkpoint store','Weights + run state'),('Evaluation workers','Held-out measurements')]),
    'eval-platform': ('An evaluation platform', 'The runner joins a dataset and run configuration. It preserves trial artifacts before graders produce a report.',
        [('Registry + manifest','Data + configuration'),('Task runner','Queue + budgets'),('Model / tools','Isolated execution'),('Artifact store','Outputs + traces'),('Graders + report','Metrics + release gate')]),
    'production': ('The production feedback loop', 'Online signals produce reviewed cases. A candidate must pass evaluation before a controlled rollout.',
        [('Production signals','Failures + feedback'),('Reviewed cases','Redacted + labeled'),('Regression suite','Versioned examples'),('Candidate change','Paired evaluation'),('Controlled rollout','Monitor + rollback')]),
    'capstone': ('Your evidence package', 'A final decision must be traceable to the task, experiment, scoring rules, and observed results.',
        [('Task contract','Decision + population'),('Dataset + baseline','Versioned inputs'),('Frozen experiment','System + graders'),('Results + limits','Uncertainty + failures'),('Decision report','Conditions + next test')]),
}


def svg(slug):
    title, description, labels = DIAGRAMS[slug]
    # Two rows keep labels legible on phones without shrinking five boxes into one row.
    positions = [(20,35),(250,35),(480,35),(480,170),(250,170)]
    edges = [(0,1),(1,2),(2,3),(3,4)]
    if slug == 'dataset-design':
        positions = [(20,100),(250,100),(480,15),(480,105),(480,195)]
        edges = [(0,1),(1,2),(1,3),(1,4)]
    if slug == 'statistics':
        positions = [(20,100),(250,25),(250,175),(480,100),(480,255)]
        edges = [(0,1),(0,2),(1,3),(2,3),(3,4)]
    if slug == 'metrics':
        positions = [(20,100),(250,15),(250,105),(250,195),(480,100)]
        edges = [(0,1),(0,2),(0,3),(1,4),(2,4),(3,4)]
    height = 350 if slug == 'statistics' else 300
    result = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 710 {height}" role="img" aria-labelledby="title-{slug} desc-{slug}">',
              f'<title id="title-{slug}">{escape(title)}</title><desc id="desc-{slug}">{escape(description)}</desc>',
              f'<defs><marker id="arrow-{slug}" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse"><path d="M0 0L10 5L0 10" fill="#717b86"/></marker></defs>']
    for a,b in edges:
        x,y = positions[a]; xx,yy = positions[b]
        if x == xx:
            d=f'M{x+95},{y+65} V{yy-8}'
        elif xx > x:
            d=f'M{x+190},{y+32} C{x+210},{y+32} {xx-20},{yy+32} {xx-8},{yy+32}'
        else:
            d=f'M{x},{y+32} H{xx+198}'
        result.append(f'<path d="{d}" fill="none" stroke="#717b86" stroke-width="1.5" marker-end="url(#arrow-{slug})"/>')
    for i,((x,y),(primary,secondary)) in enumerate(zip(positions,labels)):
        result.append(f'<rect x="{x}" y="{y}" width="190" height="65" rx="5" fill="{("#eff5ff" if i==0 else "#fff")}" stroke="#b9c4d0"/>')
        result.append(f'<text x="{x+14}" y="{y+26}" font-family="Arial,sans-serif" font-size="14" font-weight="600" fill="#17212f">{escape(primary)}</text>')
        result.append(f'<text x="{x+14}" y="{y+47}" font-family="Arial,sans-serif" font-size="11.5" fill="#536170">{escape(secondary)}</text>')
    if slug in ('ml-basics','tiny-transformer'):
        result.append(f'<path d="M250 202 H115 V108" stroke="#3564a5" stroke-dasharray="5 4" fill="none" marker-end="url(#arrow-{slug})"/><text x="120" y="190" font-size="12" font-family="Arial" fill="#3564a5">Next training step</text>')
    if slug == 'rag-agents':
        result.append(f'<path d="M480 235 V266 H345 V108" stroke="#3564a5" stroke-dasharray="5 4" fill="none" marker-end="url(#arrow-{slug})"/><text x="350" y="285" font-size="12" font-family="Arial" fill="#3564a5">Repeat within the budget</text>')
    result.append('</svg>')
    return ''.join(result)


def figure(slug, number=None):
    title, description, _ = DIAGRAMS[slug]
    prefix = f'Figure {number:02d}. ' if number else ''
    return f'<figure class="diagram">{svg(slug)}<figcaption><strong>{prefix}{escape(title)}.</strong> {escape(description)} <a href="assets/diagrams/{slug}.svg" download>Download SVG</a></figcaption></figure>'
