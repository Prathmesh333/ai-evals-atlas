"""Generate the static notebook. Run from any directory with Python 3.10+."""
from pathlib import Path
from html import escape as e
import json
import re
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
from diagrams import DIAGRAMS, figure, svg
from detail_diagrams import DETAILS, detailed_svg, detailed_figure

ROOT = Path(__file__).resolve().parents[1]
CHAPTERS = json.loads((ROOT / 'content.json').read_text(encoding='utf-8'))
EXTENDED = json.loads((ROOT / 'content-advanced.json').read_text(encoding='utf-8'))
for chapter in EXTENDED:
    index = next(i for i, item in enumerate(CHAPTERS) if item['slug'] == chapter['after'])
    CHAPTERS.insert(index + 1, chapter)
EXTRA_CATALOG = json.loads((ROOT / 'catalog-extra.json').read_text(encoding='utf-8'))
from advanced_diagrams import DIAGRAMS as EXTRA_DIAGRAMS
DIAGRAMS.update(EXTRA_DIAGRAMS)
REPO = 'https://github.com/Prathmesh333/ai-evals-atlas'
SOURCES = {
    'helm': ('Holistic Evaluation of Language Models', 'https://crfm.stanford.edu/2022/11/17/helm.html', 'Stanford CRFM · 2022', 'A public approach to evaluating several dimensions across scenarios.'),
    'hf': ('Training a causal language model from scratch', 'https://huggingface.co/learn/llm-course/chapter7/6', 'Hugging Face · course', 'A practical reference for tokenization, causal targets, and training.'),
    'nano': ('nanoGPT', 'https://github.com/karpathy/nanoGPT', 'Andrej Karpathy · repository', 'A compact implementation for studying GPT training and configuration.'),
    'lora': ('LoRA: Low-Rank Adaptation of Large Language Models', 'https://arxiv.org/abs/2106.09685', 'Hu et al. · 2021', 'The original low-rank adaptation paper.'),
    'dpo': ('Direct Preference Optimization', 'https://arxiv.org/abs/2305.18290', 'Rafailov et al. · 2023', 'The original preference-optimization objective and experiments.'),
    'chinchilla': ('Training Compute-Optimal Large Language Models', 'https://arxiv.org/abs/2203.15556', 'Hoffmann et al. · 2022', 'An empirical study of model size, data, and training compute.'),
    'harness': ('Language Model Evaluation Harness', 'https://github.com/EleutherAI/lm-evaluation-harness', 'EleutherAI · repository', 'Reusable task implementations and reproducibility documentation. Match commands to your installed version.'),
    'mmlu': ('Measuring Massive Multitask Language Understanding', 'https://github.com/hendrycks/test', 'Hendrycks et al. · benchmark', 'The source repository for MMLU.'),
    'human-eval': ('HumanEval', 'https://github.com/openai/human-eval', 'OpenAI · benchmark', 'Executable code evaluation and pass@k estimation.'),
    'swe': ('SWE-bench', 'https://www.swebench.com/', 'SWE-bench authors · benchmark', 'Software issue resolution benchmarks. Compare the same variant and environment.'),
    'bigbench': ('BIG-bench', 'https://github.com/google/BIG-bench', 'BIG-bench collaboration · benchmark', 'A collection of tasks for language-model evaluation.'),
    'gsm8k': ('GSM8K', 'https://github.com/openai/grade-school-math', 'OpenAI · benchmark', 'Grade-school mathematical word problems. The repository is archived; the task remains a reference.'),
    'gpqa': ('GPQA', 'https://github.com/idavidrein/gpqa', 'Rein et al. · benchmark', 'Expert-written graduate-level question answering.'),
    'truthfulqa': ('TruthfulQA', 'https://github.com/sylinrl/TruthfulQA', 'Lin et al. · benchmark', 'Questions designed to expose imitated misconceptions.'),
    'tau': ('τ-bench', 'https://github.com/sierra-research/tau-bench', 'Sierra Research · benchmark', 'Tool use and policy-following in simulated user interactions.'),
    'anthropic-evals': ('Demystifying evals for AI agents', 'https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents', 'Anthropic · 9 January 2026', 'Public engineering guidance on tasks, trials, graders, and outcomes.'),
    'preparedness': ('Our updated Preparedness Framework', 'https://openai.com/index/updating-our-preparedness-framework/', 'OpenAI · 15 April 2025', 'A dated account of capability assessment, safeguard evaluation, and review. It is not a claim about every later release.'),
    'deepmind': ('Frontier safety at Google DeepMind', 'https://deepmind.google/frontier-safety/', 'Google DeepMind · living overview', 'Public safety-framework material. Follow the dated documents for release-specific interpretation.'),
    'wilson': ('Confidence intervals for proportions', 'https://www.itl.nist.gov/div898/handbook/prc/section2/prc241.htm', 'NIST · statistical handbook', 'Background for binomial-proportion estimation. The playground uses the Wilson score interval.'),
    'pages': ('Creating a GitHub Pages site', 'https://docs.github.com/en/pages/getting-started-with-github-pages/creating-a-github-pages-site', 'GitHub · documentation', 'Official publishing instructions for a static site.'),
}

BENCHMARKS = [
 ('MMLU','Knowledge','mmlu','Multiple-choice questions across academic subjects.','Accuracy under a specified prompting and scoring protocol.','Knowledge recall does not establish practical task reliability.'),
 ('GPQA','Reasoning','gpqa','Graduate-level questions written by domain experts.','Accuracy; identify the exact subset and answer protocol.','Expert questions cover a specific distribution, not all scientific work.'),
 ('GSM8K','Reasoning','gsm8k','Grade-school mathematical word problems.','Correctness of the extracted final answer.','Answer extraction, calculator use, and exposure to public solutions affect comparisons.'),
 ('HumanEval','Code','human-eval','Generate functions that satisfy executable tests.','Pass@k with a declared sampling budget.','Passing tests does not prove general correctness. Generated code requires isolation.'),
 ('SWE-bench','Code','swe','Resolve real repository issues in controlled environments.','Resolved-task rate for a named variant.','Agent scaffolding, tools, dependencies, and budgets can dominate differences.'),
 ('BIG-bench','Reasoning','bigbench','A broad collection of language-model tasks.','Task-specific metrics; name the selected tasks.','An aggregate depends on task selection and weighting.'),
 ('TruthfulQA','Truthfulness','truthfulqa','Answer questions that elicit common misconceptions.','Use the metric and format defined by the chosen protocol.','Truthfulness on this set does not establish factual reliability in every domain.'),
 ('τ-bench','Agents','tau','Tool-using agents interact with simulated users and domain policies.','Task success and repeated-trial reliability.','The user simulator, tools, and task version are part of the evaluated system.'),
 ('HELM','Evaluation suite','helm','Evaluate models across scenarios and multiple measurement dimensions.','Scenario-specific metrics and transparent run configurations.','A suite is not one universal score. Inspect individual scenarios and tradeoffs.'),
]

GLOSSARY = {
 'Ablation':'An experiment that removes or changes one component to study its contribution.',
 'Accuracy':'The fraction of scored cases with a correct prediction under the declared rule.',
 'Agent':'A system that selects actions and uses observations across multiple steps.',
 'Attention':'A learned operation that combines information from accessible sequence positions.',
 'Baseline':'A reference system used to judge whether a proposed change adds value.',
 'Benchmark':'A shared set of tasks and a protocol for scoring results.',
 'Calibration':'Agreement between stated confidence and observed correctness across comparable predictions.',
 'Checkpoint':'Saved model parameters and, when included, training state.',
 'Confidence interval':'An interval produced by a procedure with a stated long-run coverage under its assumptions.',
 'Contamination':'Evaluation information influencing training or selection in a way that undermines the intended measurement.',
 'Context window':'The token capacity available to a model request under its implementation.',
 'Cross-entropy':'A loss that penalizes low predicted probability on the target outcome.',
 'Dataset shift':'A difference between the distribution used for development and the distribution encountered later.',
 'Elicitation':'Choosing prompts, tools, or other conditions to reveal a model capability.',
 'Evaluation harness':'Software that runs tasks, obtains model outputs, applies graders, and records results.',
 'Fine-tuning':'Updating a pretrained model using additional training examples.',
 'Grader':'A rule, program, model, or human process that assigns a score.',
 'Holdout':'Data reserved from a specified training or selection process.',
 'Inference':'Using a trained model to produce outputs.',
 'Logit':'An unnormalized model score before a probability transformation such as softmax.',
 'LoRA':'Low-rank adaptation, which trains additional low-rank matrices while freezing most base weights.',
 'Negative log-likelihood':'The negative logarithm of the probability assigned to an observed target.',
 'Overfitting':'Learning patterns that improve fit on development data but do not generalize to the target population.',
 'Pass@k':'The probability or estimated rate of at least one success within k attempts under a specified protocol.',
 'Perplexity':'The exponential of average negative log-likelihood when natural logarithms are used.',
 'Precision':'The fraction of positive predictions that are correct.',
 'Prompt injection':'Instructions in untrusted content that attempt to change the system’s intended behavior.',
 'RAG':'Retrieval-augmented generation: retrieving evidence for use during response generation.',
 'Recall':'The fraction of actual positive cases that a system identifies.',
 'Regression':'A deterioration in a measured behavior after a change.',
 'RLHF':'Reinforcement learning from human feedback, a family of methods that use human feedback to guide optimization.',
 'Slice':'A defined subset of evaluation cases, such as a language or document type.',
 'Temperature':'A sampling setting that changes the concentration of the token distribution.',
 'Token':'A unit of input or output represented by a tokenizer.',
 'Trace':'A record of an execution, including available outputs, tool calls, observations, and state changes.',
 'Validation set':'Data used to choose model settings, checkpoints, or other development decisions.',
}


SOURCES.update(EXTRA_CATALOG['sources'])
BENCHMARKS.extend(EXTRA_CATALOG['benchmarks'])
GLOSSARY.update(EXTRA_CATALOG['glossary'])


def nav(current):
    links = [('index','Overview'),('coverage','Guide map & outcomes'),('benchmarks','Benchmark directory'),('diagrams','Diagram notebook'),('playground','Metric playground'),('labs','Practical labs'),('glossary','Glossary'),('sources','Sources & reading')]
    def link(slug,label,num=''):
        active = ' aria-current="page"' if slug == current else ''
        return f'<a href="{slug}.html"{active}>{("<span class=nav-number>"+num+"</span>") if num else ""}<span>{e(label)}</span></a>'
    out = ''.join(link(*item) for item in links)
    stage = None
    for i,c in enumerate(CHAPTERS,1):
        if c['stage'] != stage:
            stage = c['stage']; out += f'<div class="nav-label">{e(stage)}</div>'
        out += link(c['slug'],c['title'],f'{i:02d}')
    return out


def shell(slug,title,body,description='',section='The notebook'):
    return f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">{'<base href="/ai-evals-atlas/">' if slug=='404' else ''}
<title>{e(title)} · AI Evals Atlas</title><meta name="description" content="{e(description or title)}">
<meta name="theme-color" content="#ffffff"><meta property="og:title" content="{e(title)} · AI Evals Atlas"><meta property="og:description" content="{e(description or title)}"><meta property="og:type" content="website">
<link rel="icon" href="assets/favicon.svg" type="image/svg+xml"><link rel="stylesheet" href="assets/style.css">
<script defer src="assets/search-index.js?v=2"></script><script defer src="assets/app.js?v=2"></script></head>
<body data-page="{slug}"><a class="skip" href="#main">Skip to content</a>
<aside class="sidebar" id="sidebar" aria-label="Notebook navigation"><a class="brand" href="index.html"><span class="brand-mark" aria-hidden="true"></span>AI Evals Atlas</a><div class="edition">An open learning notebook</div>
<button class="search-trigger" data-search-open>Search the notebook <kbd>/</kbd></button><nav class="side-nav" aria-label="Chapters and resources">{nav(slug)}</nav>
<div class="side-bottom"><span id="progress-label">0 of {len(CHAPTERS)} chapters completed</span><div class="progress-track" aria-hidden="true"><div class="progress-fill" id="progress-fill"></div></div><span>Saved in this browser</span></div></aside>
<div class="mobile-backdrop" id="backdrop"></div><div class="workspace"><header class="topbar"><button class="menu-toggle" aria-controls="sidebar" aria-expanded="false">Menu</button><span class="topbar-path">Notebook <span aria-hidden="true"> / </span> {e(section)}</span><div class="topbar-links"><a href="labs.html">Labs</a><a href="{REPO}">GitHub ↗</a><button class="print-button" data-print>Print notes</button></div></header>
<main class="page" id="main">{body}<footer class="footer"><span>AI Evals Atlas · Learn, build, measure.</span><span><a href="sources.html">Sources</a> · <a href="{REPO}">Edit on GitHub</a> · Edition 01 / October 2026</span></footer></main></div>
<dialog id="search-dialog" aria-labelledby="search-title"><div class="search-head"><label for="site-search" id="search-title" class="sr-only">Search all chapters</label><input id="site-search" type="search" class="text-input" placeholder="Search topics, terms, and explanations…" autocomplete="off"><button data-search-close aria-label="Close search">Esc</button></div><div class="search-results" id="search-results" aria-live="polite"><p class="search-help">Search across the complete notebook.</p></div></dialog>
</body></html>'''


def write_page(slug,title,body,description='',section='The notebook'):
    (ROOT/f'{slug}.html').write_text(shell(slug,title,body,description,section),encoding='utf-8')


def header(eyebrow,title,lead):
    heading = e(title).replace('\n','<br>')
    return f'<div class="eyebrow">{e(eyebrow)}</div><h1>{heading}</h1><p class="lead">{e(lead)}</p>'


def code(text):
    return f'<div class="code-block"><button class="copy-button" aria-label="Copy code">Copy</button><pre><code>{e(text)}</code></pre></div>'


def main():
    (ROOT/'assets/diagrams').mkdir(parents=True,exist_ok=True)
    for slug in DIAGRAMS:
        (ROOT/f'assets/diagrams/{slug}.svg').write_text(svg(slug),encoding='utf-8')
    for slug in DETAILS:
        (ROOT/f'assets/diagrams/{slug}.svg').write_text(detailed_svg(slug),encoding='utf-8')
    index=header('Field notes / 001','Understand AI.\nMeasure what it can do.','A practical notebook on AI evaluations and benchmarking. Start with the basics, train a small model, and work toward reliable evaluation systems.')
    index += f'<div class="hero-meta"><span>{len(CHAPTERS)} chapters</span><span>{len(DIAGRAMS)+len(DETAILS)} system diagrams</span><span>4 runnable labs</span><span>Beginner → advanced</span></div><div class="button-row"><a class="primary" href="foundations.html">Start reading <span aria-hidden="true">→</span></a><a class="secondary" href="coverage.html">See the complete guide map</a></div>'
    index += '<div class="hero-diagram"><div class="mini-label">The idea behind every evaluation</div><div class="workflow"><div class="workflow-step"><b>Define the task</b><small>What should happen?</small></div><span class="workflow-arrow" aria-hidden="true">→</span><div class="workflow-step"><b>Run the system</b><small>Under known conditions</small></div><span class="workflow-arrow" aria-hidden="true">→</span><div class="workflow-step"><b>Measure the result</b><small>With a valid grader</small></div><span class="workflow-arrow" aria-hidden="true">→</span><div class="workflow-step"><b>Make a decision</b><small>Keep the uncertainty</small></div></div></div>'
    index += '<div class="section-heading"><h2>The learning path</h2><span>Read in order, or choose a topic</span></div>'
    for stage in dict.fromkeys(c['stage'] for c in CHAPTERS):
        matching=[(i,c) for i,c in enumerate(CHAPTERS,1) if c['stage']==stage]
        index += f'<section class="curriculum-group"><div><div class="group-title">{e(stage)}</div><div class="group-range">Chapters {matching[0][0]:02d}–{matching[-1][0]:02d}</div></div><div>'
        for i,c in matching:
            index += f'<a class="lesson-row" href="{c["slug"]}.html"><span class="lesson-id">{i:02d}</span><div><div class="lesson-name">{e(c["title"])}</div><div class="lesson-summary">{e(c["summary"])}</div></div><span class="row-arrow" aria-hidden="true">↗</span></a>'
        index += '</div></section>'
    index += '<div class="section-heading"><h2>Keep these pages nearby</h2><span>Reference & practice</span></div><div class="resource-grid">'
    for slug,title,description in [('benchmarks','Benchmark directory','Compare what each benchmark measures and where it falls short.'),('playground','Metric playground','Change the counts. See accuracy, uncertainty, and reliability change.'),('labs','Practical labs','Train a small model and evaluate stored predictions with Python.'),('glossary','The glossary','Plain definitions for the terms used throughout the notebook.')]:
        index += f'<a class="resource" href="{slug}.html"><h3>{title} ↗</h3><p>{description}</p></a>'
    index += '</div><div class="home-aside"><section><h3>Start without a background in AI</h3><p>The first chapters define the terms. Basic Python helps with the labs. The small-model and stored-prediction labs need no GPU, API key, or external dataset.</p></section><section><h3>Connect the whole evaluation lifecycle</h3><p>Study prediction models, language models, multimodal systems, and agents. Build datasets, run experiments, interpret uncertainty, and make release decisions. The <a href="coverage.html">guide map</a> lists outcomes and specialist boundaries.</p></section></div>'
    write_page('index','A notebook on AI evaluation',index,'Learn AI evaluation from first principles to advanced systems with diagrams, runnable labs, and public sources.','Overview')
    search=[]
    for i,c in enumerate(CHAPTERS,1):
        words=sum(len(s[1].split()) for s in c['sections'])
        extra_diagrams = [key for key,value in DETAILS.items() if value[0]==c['slug']]
        diagram_count=1+len(extra_diagrams)
        body=f'<div class="article-header">{header(f"Chapter {i:02d} / " + c["stage"],c["title"],c["summary"])}<div class="article-meta"><span>Learning level {c["level"]}</span><span>{max(3,round(words/180))} min read + practice</span><span>{diagram_count} diagram{"s" if diagram_count>1 else ""} · 1 exercise</span></div></div>'
        article=''
        toc=''
        for j,(title,text) in enumerate(c['sections'],1):
            article+=f'<section id="section-{j}"><h2>{e(title)}</h2>'+''.join(f'<p>{e(p)}</p>' for p in text.split('\n'))+'</section>'
            toc+=f'<a href="#section-{j}">{e(title)}</a>'
            if j==1: article+=figure(c['slug'],i)
            if j==2:
                article+=''.join(detailed_figure(key) for key in extra_diagrams)
        if c['slug'] in ('small-model','tiny-transformer'):
            filename='tiny_lm.py' if c['slug']=='small-model' else 'tiny_transformer.py'
            article+=code(f'python labs/{filename}'+(' --steps 50' if c['slug']=='tiny-transformer' else ''))
            article+='<p><a href="labs.html">Open the lab instructions and source files →</a></p>'
        if c.get('code'):
            article+='<h3 id="commands">Commands for this note</h3>'+code(c['code'])
            toc+='<a href="#commands">Commands</a>'
        article+=f'<section class="exercise" id="practice"><div class="mini-label">Try it yourself</div><p>{e(c["exercise"])}</p></section><details class="knowledge"><summary>{e(c["question"])}</summary><p>{e(c["answer"])}</p></details>'
        if c['refs']:
            article+='<h3 id="reading">Sources & further reading</h3><ul class="sources-list">'+''.join(f'<li><a href="{SOURCES[r][1]}">{e(SOURCES[r][0])}</a> <span>· {e(SOURCES[r][2])}</span></li>' for r in c['refs'])+'</ul>'
            toc+='<a href="#reading">Sources & reading</a>'
        article+=f'<div class="complete-row"><button class="secondary complete-btn" data-complete="{c["slug"]}" aria-pressed="false">Mark chapter complete</button><span>Progress stays on this device.</span></div><nav class="pagination" aria-label="Adjacent chapters">'
        prev=CHAPTERS[i-2] if i>1 else {'slug':'index','title':'Notebook overview'}
        nex=CHAPTERS[i] if i<len(CHAPTERS) else {'slug':'labs','title':'Put it into practice'}
        article+=f'<a href="{prev["slug"]}.html"><small>← Previous</small>{e(prev["title"])}</a><a href="{nex["slug"]}.html"><small>Next →</small>{e(nex["title"])}</a></nav>'
        body+=f'<div class="article-layout"><article class="article-content">{article}</article><aside class="toc" aria-label="On this page"><div class="toc-title">In this note</div>{toc}<a href="#practice">Try it yourself</a></aside></div>'
        write_page(c['slug'],c['title'],body,c['summary'],c['stage'])
        search.append({'kind':'chapter','title':c['title'],'url':c['slug']+'.html','summary':c['summary'],'text':' '.join(t for _,t in c['sections'])})

    directory=header('Reference / Benchmarks','Know what the score means.','A benchmark is useful when its task and protocol match your question. Start with the measurement, then inspect the limitations.')
    directory+='<div class="filter-bar"><label class="sr-only" for="benchmark-search">Search benchmarks</label><input class="text-input" id="benchmark-search" type="search" placeholder="Search benchmarks…"><label class="sr-only" for="benchmark-category">Benchmark category</label><select id="benchmark-category"><option value="all">All categories</option>'+''.join(f'<option>{e(cat)}</option>' for cat in sorted(set(b[1] for b in BENCHMARKS)))+f'</select></div><p class="result-count" id="benchmark-count" aria-live="polite">{len(BENCHMARKS)} benchmarks and suites</p>'
    for name,category,ref,description,metric,limitation in BENCHMARKS:
        directory+=f'<article class="benchmark-card" data-category="{category}"><div class="benchmark-meta"><span class="tag">{category}</span></div><h2><a href="{SOURCES[ref][1]}">{e(name)} ↗</a></h2><p>{e(description)}</p><div class="benchmark-detail"><div><strong>Read the metric</strong>{e(metric)}</div><div><strong>Keep this limitation</strong>{e(limitation)}</div></div></article>'
    directory+='<p id="benchmark-empty" hidden>No benchmarks match. Try another term or select all categories.</p><div class="note">This directory explains benchmark families. It is not a live leaderboard. Versions, contamination, prompts, and tool budgets affect comparisons.</div>'
    write_page('benchmarks','Benchmark directory',directory,section='Reference')

    diagrams=header('Visual reference / Systems','The diagram notebook.','Follow the data, the decisions, and the feedback loops. Each diagram links to the lesson that explains it.')+'<div class="note">Diagrams simplify the system to teach one idea. Arrow labels and captions state the scope. Download any diagram as an editable SVG.</div><div class="diagram-index">'
    for i,c in enumerate(CHAPTERS,1):
        diagrams+=f'<section id="{c["slug"]}"><h2>{i:02d} · {e(DIAGRAMS[c["slug"]][0])}</h2>{figure(c["slug"],i)}<a class="section-link" href="{c["slug"]}.html">Read the note: {e(c["title"])} →</a></section>'
        for key,value in DETAILS.items():
            if value[0]==c['slug']:
                diagrams+=f'<section id="{key}"><h2>{e(value[1])}</h2>{detailed_figure(key)}</section>'
    write_page('diagrams','Diagram notebook',diagrams+'</div>',section='Visual reference')

    playground=header('Interactive notes / Metrics','Change a number.\nUnderstand the result.','These calculators run in your browser. The values are teaching examples, not measurements of a real model.')
    playground+='''<section class="tool" id="wilson-tool"><h2>01 · Accuracy and uncertainty</h2><p>Enter independent binary task outcomes. The 95% Wilson interval describes uncertainty under that sampling assumption.</p><div class="field-grid"><label>Successful tasks<input id="successes" type="number" min="0" max="10000000" step="1" value="80"></label><label>Total tasks<input id="total" type="number" min="1" max="10000000" step="1" value="100"></label></div><div class="tool-output" id="wilson-output" aria-live="polite"></div><div class="interval-track" aria-hidden="true"><div class="interval-range" id="interval-range"></div><div class="interval-point" id="interval-point"></div><div class="scale"><span>0%</span><span>50%</span><span>100%</span></div></div><p>Try 80/100, then 800/1000. The observed rate stays the same while the interval narrows. Repeated attempts on one task are not independent tasks.</p></section>
<section class="tool"><h2>02 · Precision, recall, and F1</h2><p>Define the positive class before using these counts. A zero denominator means the corresponding metric is undefined.</p><div class="field-grid"><label>True positives<input id="tp" type="number" min="0" max="10000000" step="1" value="8"></label><label>False positives<input id="fp" type="number" min="0" max="10000000" step="1" value="4"></label><label>False negatives<input id="fn" type="number" min="0" max="10000000" step="1" value="2"></label></div><div class="tool-output" id="f1-output" aria-live="polite"></div></section>
<section class="tool"><h2>03 · Success once or every time?</h2><p>This simplified probability model assumes independent attempts with the same success probability p. It is not the finite-sample pass@k estimator.</p><div class="field-grid"><label>Per-attempt success (%)<input id="probability" type="number" min="0" max="100" step="1" value="80"></label><label>Attempts (k)<input id="attempts" type="number" min="1" max="1000" step="1" value="5"></label></div><div class="tool-output" id="reliability-output" aria-live="polite"></div><p>At least one success: 1 − (1 − p)ᵏ. All attempts succeed: pᵏ. Real task difficulty and correlated attempts can invalidate this simple model.</p></section>
<section class="tool"><h2>04 · Plan an evaluation budget</h2><p>Estimate model-token charges using prices you supply. Add tool costs, graders, failed attempts, and infrastructure separately.</p><div class="field-grid"><label>Cases<input id="cost-cases" type="number" min="1" max="10000000" step="1" value="1000"></label><label>Trials per case<input id="cost-trials" type="number" min="1" max="10000" step="1" value="3"></label><label>Input tokens / trial<input id="input-tokens" type="number" min="0" max="10000000" step="1" value="1000"></label><label>Output tokens / trial<input id="output-tokens" type="number" min="0" max="10000000" step="1" value="500"></label><label>Input price / 1M tokens ($)<input id="input-price" type="number" min="0" max="100000" step="0.01" value="1"></label><label>Output price / 1M tokens ($)<input id="output-price" type="number" min="0" max="100000" step="0.01" value="4"></label></div><div class="tool-output" id="cost-output" aria-live="polite"></div><p>Default prices are illustrative inputs. They are not a quote for any provider.</p></section>'''
    write_page('playground','Metric playground',playground,section='Practice')

    labs=header('Practice / Runnable experiments','Learn by running the experiment.','Four Python labs connect the notebook to training, stored-prediction evaluation, and a real model endpoint. Each lab has a clear scope and records its result.')
    labs+='<div class="note">Run these commands from the repository root. Python 3.10+ is required. Only the transformer lab needs PyTorch. The website itself needs no installation.</div>'
    labs+=code('git clone https://github.com/Prathmesh333/ai-evals-atlas.git\ncd ai-evals-atlas')
    lab_data=[('01','Train a character language model','tiny_lm.py','python labs/tiny_lm.py','No dependencies beyond Python. The script fits unigram and bigram models, selects smoothing on validation text, and evaluates the final choices on test text.','The report contains validation losses, test perplexity, input hashes, and the unknown-character rate. Read labs/runs/tiny-lm.json. A generated sample is not a quality score.'),('02','Train a tiny byte transformer','tiny_transformer.py','python -m venv .venv\n# Windows: .venv\\Scripts\\activate\n# macOS / Linux: source .venv/bin/activate\npython -m pip install -r labs/requirements-transformer.txt\npython labs/tiny_transformer.py --steps 50','A CPU smoke experiment with 137,216 parameters: two layers, four heads, and a 64-byte context. Use more data and training for a meaningful language experiment.','The script selects the lowest-validation-loss checkpoint, evaluates it on test data, and writes a checkpoint plus a JSON report. The tiny sample corpus cannot train a useful assistant.'),('03','Evaluate two sets of predictions','evaluate.py','python labs/evaluate.py','No API calls. The dataset and both prediction files are synthetic teaching fixtures. The script scores every case, including missing answers.','Expected result: baseline 7/12, candidate 10/12. The paired bootstrap interval crosses zero, so the small example does not establish a reliable improvement. Read labs/runs/evaluation.json.')]
    lab_data.append(('04','Collect predictions from a model endpoint','collect_predictions.py','python labs/collect_predictions.py --model YOUR_LOCAL_MODEL --base-url http://127.0.0.1:1234/v1 --output labs/runs/local-model','Start a compatible local model server first. This standard-library client sends case inputs without the answer key. Hosted endpoints are optional and can charge for requests.','The run writes predictions.json and manifest.json. Missing responses count as task failures. Read the real-model chapter for baseline and candidate collection, credentials, and endpoint compatibility.'))
    for num,title,file,command,description,result in lab_data:
        labs+=f'<section class="lab-section"><div class="eyebrow">Lab {num}</div><h2>{title}</h2><p>{description}</p>{code(command)}<p>{result}</p><a class="section-link" href="labs/{file}" download>Download {file} ↓</a> · <a class="section-link" href="{REPO}/blob/main/labs/{file}">Read source ↗</a></section>'
    labs+='<section class="lab-section"><h2>Make the experiment yours</h2><ol><li>Replace the sample data with permitted, separate document splits.</li><li>Define a task-specific scoring rule before inspecting candidate results.</li><li>Save the dataset version and model configuration with the report.</li><li>Explain failures and limits in the report template.</li></ol><p><a href="labs/report-template.md" download>Download the report template ↓</a></p><p><a href="labs/data/cases.jsonl" download>Evaluation cases</a> · <a href="labs/data/baseline.json" download>Baseline predictions</a> · <a href="labs/data/candidate.json" download>Candidate predictions</a></p></section>'
    labs+='<p><a href="real-model.html">Read the real-model evaluation procedure →</a></p><p><a href="tooling.html">Run a public benchmark with an evaluation harness →</a></p>'
    write_page('labs','Practical labs',labs,section='Practice')

    coverage=header('Curriculum / Coverage audit','The complete guide map.','A connected path through AI evaluation and benchmarking: learn the concepts, build experiments, inspect evidence, and make a defensible decision.')
    coverage+='<div class="note">Complete here means an end-to-end practical curriculum with explicit learning outcomes. It does not mean every benchmark, every mathematical proof, every industry requirement, or undisclosed lab methods.</div>'
    coverage+='<h2>Choose a route</h2><div class="table-wrap"><table class="matrix"><thead><tr><th>Goal</th><th>Read and do</th><th>Evidence of completion</th></tr></thead><tbody>'
    tracks=[('New to AI','foundations','Start with foundations, prediction models, tokens, and the training labs.','Explain the data splits and produce a held-out training report.'),('Build an application eval','dataset-design','Study dataset design, metrics, experiments, graders, and human review.','Create a labeled dataset and validate a grader.'),('Compare real models','real-model','Collect endpoint outputs, run a public harness, and compare paired results.','Save run manifests, outputs, intervals, and representative failures.'),('Evaluate complex systems','rag-agents','Study retrieval, agents, long context, multimodal systems, and safeguards.','Test final states, evidence use, memory, and relevant failure modes.'),('Operate at scale','serving-performance','Study serving performance, platforms, production, and release decisions.','Publish quality and load results with a release and rollback decision.')]
    for goal,slug,route,evidence in tracks:
        coverage+=f'<tr><td><a href="{slug}.html">{goal}</a></td><td>{route}</td><td>{evidence}</td></tr>'
    coverage+='</tbody></table></div><h2>Chapter-by-chapter outcomes</h2><p class="reading-note">Use each exercise as a checkpoint. Completing the reading alone is not a demonstration of practical mastery.</p>'
    for i,c in enumerate(CHAPTERS,1):
        coverage+=f'<section class="source-entry"><div class="mini-label">{i:02d} / {e(c["stage"])}</div><h2><a href="{c["slug"]}.html">{e(c["title"])}</a></h2><p>{e(c["exercise"])}</p></section>'
    coverage+='<h2>What needs specialist treatment</h2><p>Robotics, embodied-control safety, causal inference, formal verification, privacy guarantees, and regulated domain validation each require additional methods and domain expertise. This guide introduces the evaluation principles that connect to those areas. It does not replace their specialist curricula.</p><p>Frontier-lab sections explain public disclosures and explicitly labeled engineering synthesis. Private training mixtures, hidden test sets, and internal release decisions cannot be reconstructed from public leaderboard scores.</p><h2>Finish with a reproducible decision</h2><p>Complete the <a href="capstone.html">capstone</a> and <a href="labs/report-template.md">report template</a>. Include the task contract, data provenance, versions, budget, grader checks, uncertainty, failure analysis, and release conditions.</p><p>Start with the <a href="labs/dataset-card.md" download>dataset card template</a> and <a href="labs/rubric.example.json" download>example grading rubric</a>. Adapt and validate the rubric for your task before using its scores to make a decision.</p>'
    write_page('coverage','Guide map and learning outcomes',coverage,section='Curriculum')

    glossary=header('Reference / Terminology','One term, one meaning.','The terms used throughout the notebook, explained in plain language.')+'<label for="glossary-search" class="sr-only">Filter glossary</label><input id="glossary-search" class="text-input" type="search" placeholder="Find a term…"><p class="result-count" id="glossary-count" aria-live="polite"></p><dl class="glossary">'
    for term,definition in sorted(GLOSSARY.items()):
        glossary+=f'<div class="glossary-entry"><dt>{e(term)}</dt><dd>{e(definition)}</dd></div>'
    write_page('glossary','Glossary',glossary+'</dl>',section='Reference')

    sources=header('Reference / Evidence','Read the original sources.','Primary papers, public engineering notes, and official documentation behind the notebook.')
    sources+='<div class="note">Source links were reviewed on 13 October 2026. Public pages can change. The frontier-lab chapter distinguishes dated disclosures from this notebook’s engineering synthesis. This site is not affiliated with the labs or benchmark authors.</div>'
    for key,(title,url,author,description) in SOURCES.items():
        sources+=f'<section class="source-entry" id="{key}"><div class="mini-label">{e(author)}</div><h2><a href="{url}">{e(title)} ↗</a></h2><p>{e(description)}</p></section>'
    sources+='<section class="source-entry"><h2>Writing and editorial method</h2><p>Explanations use the project’s <a href="https://github.com/Prathmesh333/controlled-technical-english-writing-skill">Controlled Technical English writing skill</a>: consistent terms, explicit conditions, and short steps. This is an independent writing aid, not a claim of compliance with an external language standard.</p><p>The notebook and diagrams are original educational material prepared with AI assistance. Examples are labeled as synthetic where applicable. Corrections can be proposed through the repository.</p></section>'
    write_page('sources','Sources and further reading',sources,section='Reference')
    write_page('404','Page not found',header('404 / Missing note','This page is not in the notebook.','Use the overview to find the chapter you need.')+'<a class="primary" href="/ai-evals-atlas/index.html">Open the notebook →</a>')
    for slug,title,description in [('benchmarks','Benchmark directory',' · '.join(b[0] for b in BENCHMARKS)),('diagrams','Diagram notebook','Visual systems training model architecture RAG agent loops evaluation infrastructure'),('playground','Metric playground','Wilson confidence interval precision recall F1 pass@k cost calculator'),('labs','Practical labs','Python small model transformer evaluate endpoint collector runnable code'),('glossary','Glossary',' '.join(GLOSSARY)),('sources','Sources and reading','Papers and primary sources for the notebook')]:
        search.append({'kind':'resource','title':title,'url':slug+'.html','summary':description,'text':description})
    search.append({'kind':'resource','title':'Guide map and learning outcomes','url':'coverage.html','summary':'Curriculum coverage, learning routes, exercises, and specialist boundaries.','text':'Complete guide coverage audit roadmap curriculum'})
    (ROOT/'assets/search-index.js').write_text('window.ATLAS_SEARCH = '+json.dumps(search,ensure_ascii=False)+';\n',encoding='utf-8')
    (ROOT/'.nojekyll').touch()
    print(f'Built {len(CHAPTERS)+9} HTML pages and {len(DIAGRAMS)+len(DETAILS)} SVG diagrams.')


if __name__=='__main__':
    main()
