# AI Evals Atlas

A white, notebook-style website for learning AI evaluation and benchmarking. Read the basics, train a small model, and build a reproducible evaluation system.

**Website:** https://prathmesh333.github.io/ai-evals-atlas/

## Inside the notebook

- 18 chapters covering foundations, small models, evaluation design, statistics, graders, benchmarks, RAG, agents, safety, frontier-lab disclosures, scaling, and production.
- 26 original SVG diagrams, including detailed attention, transformer, retrieval, and distributed-system figures.
- 3 runnable Python labs: a character language model, a tiny byte transformer, and a stored-prediction evaluator.
- A benchmark directory, glossary, primary-source reading list, and four interactive metric calculators.
- Search, local chapter progress, mobile navigation, and print styles.

The focus is language models and their surrounding systems. This is a structured foundation with advanced engineering topics, not an exhaustive account of every AI subfield or a proprietary frontier training recipe.

## Open locally

Open `index.html` directly, or serve the directory:

```sh
python -m http.server 8000
```

Then visit http://localhost:8000. All lesson text and navigation are static HTML. JavaScript adds search, calculators, and local progress. No API key, npm install, external fonts, or server is required for the website.

## Publish on GitHub Pages

The included workflow validates the site and deploys the static files when `main` changes.

1. Open the repository's **Settings → Pages**.
2. Select **GitHub Actions** as the build source.
3. Push to `main`, or run the **Validate and deploy Pages** workflow manually.
4. Open the Pages URL after the deployment succeeds.

Alternatively, choose **Deploy from a branch**, select `main` and `/ (root)`, and disable the deployment workflow if you use that route. The checked-in HTML needs no build step for branch publishing.

## Edit the notebook

- `content.json`: chapter prose, exercises, answers, and source keys.
- `tools/build.py`: shared HTML layout and reference pages.
- `tools/diagrams.py`: chapter overview diagrams.
- `tools/detail_diagrams.py`: detailed SVG diagrams.
- `assets/style.css`: notebook layout and responsive styling.
- `assets/app.js`: browser interactions.
- `labs/`: runnable examples and synthetic teaching fixtures.

After editing source content, regenerate the checked-in HTML:

```sh
python tools/build.py
```

Use Python 3.10 or later. The generator uses only the standard library. Relative links support the GitHub Pages project path. The 404 page has a project-specific base path; update it if you rename the repository.

## Run the labs

```sh
python labs/tiny_lm.py
python labs/evaluate.py
```

The transformer lab is optional:

```sh
python -m pip install -r labs/requirements-transformer.txt
python labs/tiny_transformer.py --steps 50
```

Run dependency installation in a virtual environment. The transformer uses a CPU by default. A 50-step run is a smoke test, not a useful assistant. The sample corpus is original, synthetic teaching text. Reports go to `labs/runs/`, which Git ignores. The evaluation fixtures are stored answers, not results from real model providers.

The transformer dependency allows PyTorch 2.x. The initial smoke test used PyTorch 2.6.0+cpu. Reports record the actual version. Pin an environment for a research comparison.

## Validate

```sh
python tools/build.py
python tests/check_site.py
python -m unittest discover -s tests -p "test_*.py"
node --check assets/app.js
```

For browser checks:

```sh
python -m pip install playwright
python -m playwright install chromium
python tests/browser_checks.py
```

Browser checks start their own local server. They cover navigation, search, progress persistence, filters, calculator edge cases, desktop and mobile overflow, and reading without JavaScript.

## Sources and writing

Each relevant chapter links to primary sources. `sources.html` collects the reading list. Public lab frameworks are dated disclosures, not proof of undisclosed internal practices. The explanations distinguish public evidence from this notebook's engineering synthesis.

Prose follows [Controlled Technical English](https://github.com/Prathmesh333/controlled-technical-english-writing-skill/blob/main/SKILL.md): consistent terminology, explicit conditions, and clear procedural steps. The material was prepared with AI assistance. The writing skill is an independent aid and does not certify compliance with an external standard.

## Privacy

The site makes no model API calls and includes no analytics. Chapter progress is stored only in browser local storage. External source links take you to their respective publishers.

## License

Original code, diagrams, and prose are MIT licensed. Linked papers, benchmark datasets, and third-party projects retain their own licenses.
