'use strict';
(() => {
  const $ = (selector) => document.querySelector(selector);
  const all = (selector) => [...document.querySelectorAll(selector)];
  const storageKey = 'ai-evals-atlas-progress-v1';
  const chapters = (window.ATLAS_SEARCH || []).filter(item => !['benchmarks.html','diagrams.html','playground.html','labs.html','glossary.html','sources.html'].includes(item.url));
  let completed = [];
  try {
    const saved = JSON.parse(localStorage.getItem(storageKey) || '[]');
    if (Array.isArray(saved)) completed = [...new Set(saved)].filter(slug => chapters.some(c => c.url === slug + '.html'));
  } catch { /* Reading and navigation remain available without storage. */ }
  function updateProgress() {
    $('#progress-label').textContent = `${completed.length} of ${chapters.length} chapters completed`;
    $('#progress-fill').style.width = `${chapters.length ? completed.length / chapters.length * 100 : 0}%`;
    all('[data-complete]').forEach(button => {
      const done = completed.includes(button.dataset.complete);
      button.setAttribute('aria-pressed', String(done));
      button.textContent = done ? '✓ Chapter completed' : 'Mark chapter complete';
    });
  }
  updateProgress();
  all('[data-complete]').forEach(button => button.addEventListener('click', () => {
    const slug = button.dataset.complete;
    completed = completed.includes(slug) ? completed.filter(item => item !== slug) : [...completed, slug];
    try { localStorage.setItem(storageKey, JSON.stringify(completed)); }
    catch { button.parentElement.querySelector('span').textContent = 'Storage is unavailable. Progress lasts for this page only.'; }
    updateProgress();
  }));

  const menu = $('.menu-toggle');
  function setMenu(open) {
    $('#sidebar').classList.toggle('open', open);
    $('#backdrop').classList.toggle('visible', open);
    menu.setAttribute('aria-expanded', String(open));
    if (matchMedia('(max-width: 700px)').matches) $('#sidebar').inert = !open;
  }
  menu.addEventListener('click', () => setMenu(menu.getAttribute('aria-expanded') !== 'true'));
  $('#backdrop').addEventListener('click', () => setMenu(false));
  function syncMenu() {
    if (!matchMedia('(max-width: 700px)').matches) { $('#sidebar').inert = false; setMenu(false); }
    else setMenu(false);
  }
  syncMenu();
  matchMedia('(max-width: 700px)').addEventListener('change', syncMenu);
  document.addEventListener('keydown', event => {
    if (event.key === 'Escape' && menu.getAttribute('aria-expanded') === 'true') { setMenu(false); menu.focus(); }
  });
  all('[data-print]').forEach(button => button.addEventListener('click', () => window.print()));

  const dialog = $('#search-dialog');
  const input = $('#site-search');
  let searchOpener;
  function openSearch(opener) {
    searchOpener = opener;
    if (!dialog.open) dialog.showModal();
    input.focus();
    renderSearch();
  }
  function closeSearch() { dialog.close(); searchOpener?.focus(); }
  all('[data-search-open]').forEach(button => button.addEventListener('click', () => openSearch(button)));
  $('[data-search-close]').addEventListener('click', closeSearch);
  dialog.addEventListener('click', event => { if (event.target === dialog) closeSearch(); });
  document.addEventListener('keydown', event => {
    const typing = /INPUT|TEXTAREA|SELECT/.test(document.activeElement.tagName) || document.activeElement.isContentEditable;
    if (event.key === 'Escape' && dialog.open) { event.preventDefault(); closeSearch(); return; }
    if (event.key === '/' && !typing && !dialog.open) { event.preventDefault(); openSearch(document.activeElement); }
  });
  function renderSearch() {
    const query = input.value.trim().toLowerCase();
    const results = $('#search-results');
    results.replaceChildren();
    const terms = query.split(/\s+/).filter(Boolean);
    const matches = (window.ATLAS_SEARCH || []).map(item => ({item, score: terms.reduce((s,term) => s + (item.title.toLowerCase().includes(term) ? 3 : 0) + (item.summary.toLowerCase().includes(term) ? 1 : 0), 0)}))
      .filter(({item}) => terms.every(term => `${item.title} ${item.summary} ${item.text}`.toLowerCase().includes(term)))
      .sort((a,b) => b.score - a.score).slice(0, 12);
    const status = document.createElement('p');
    status.className = 'search-help';
    status.textContent = query ? (matches.length ? `${matches.length} matching notes (up to 12 shown)` : 'No matching notes. Try a broader term such as “data” or “agent”.') : 'Start with a chapter, or search any term.';
    results.append(status);
    for (const {item} of matches) {
      const link = document.createElement('a'); link.className = 'search-result'; link.href = item.url;
      const title = document.createElement('strong'); title.textContent = item.title;
      const summary = document.createElement('span'); summary.textContent = item.summary;
      link.append(title,summary); results.append(link);
    }
  }
  input.addEventListener('input', renderSearch);

  all('.copy-button').forEach(button => button.addEventListener('click', async () => {
    const text = button.parentElement.querySelector('code').textContent;
    try { await navigator.clipboard.writeText(text); button.textContent = 'Copied'; }
    catch { button.textContent = 'Select code to copy'; }
    setTimeout(() => { button.textContent = 'Copy'; }, 2000);
  }));

  if ($('#benchmark-search')) {
    function filterBenchmarks() {
      const query = $('#benchmark-search').value.trim().toLowerCase();
      const category = $('#benchmark-category').value;
      let count = 0;
      all('.benchmark-card').forEach(card => {
        card.hidden = !(card.textContent.toLowerCase().includes(query) && (category === 'all' || category === card.dataset.category));
        if (!card.hidden) count++;
      });
      $('#benchmark-count').textContent = `${count} benchmarks and suites`;
      $('#benchmark-empty').hidden = count !== 0;
    }
    $('#benchmark-search').addEventListener('input', filterBenchmarks);
    $('#benchmark-category').addEventListener('change', filterBenchmarks);
  }
  if ($('#glossary-search')) {
    function filterGlossary() {
      let count = 0;
      const query = $('#glossary-search').value.trim().toLowerCase();
      all('.glossary-entry').forEach(entry => { entry.hidden = !entry.textContent.toLowerCase().includes(query); if (!entry.hidden) count++; });
      $('#glossary-count').textContent = count ? `${count} terms` : 'No matching terms. Try another search.';
    }
    $('#glossary-search').addEventListener('input',filterGlossary); filterGlossary();
  }
  if ($('#wilson-tool')) {
    const pct = value => `${(value*100).toFixed(1)}%`;
    function value(id, integer=true) {
      const el = $('#' + id), n = el.valueAsNumber;
      if (!Number.isFinite(n) || !el.checkValidity() || (integer && !Number.isInteger(n))) throw new Error('Enter valid numbers within the displayed limits. Task counts must be whole numbers.');
      return n;
    }
    function output(id,main,detail) {
      const el=$('#'+id); el.replaceChildren(); el.classList.remove('error');
      const strong=document.createElement('strong'); strong.textContent=main;
      const small=document.createElement('small'); small.textContent=detail;
      el.append(strong,small);
    }
    function protect(id,fn) {
      try { fn(); } catch(error) { const el=$('#'+id); el.textContent=error.message; el.classList.add('error'); }
    }
    function calculate() {
      protect('wilson-output', () => {
        $('#interval-range').hidden=true; $('#interval-point').hidden=true;
        const n=value('total'), s=value('successes');
        if(s>n) throw new Error('Successful tasks cannot exceed total tasks.');
        const p=s/n,z=1.959963984540054,d=1+z*z/n,center=(p+z*z/(2*n))/d,radius=z*Math.sqrt(p*(1-p)/n+z*z/(4*n*n))/d;
        const low=Math.max(0,center-radius),high=Math.min(1,center+radius);
        output('wilson-output',`${pct(p)} observed success`, `95% Wilson interval: ${pct(low)} to ${pct(high)} · ${s} successes in ${n} tasks`);
        $('#interval-range').style.left=pct(low); $('#interval-range').style.width=pct(high-low); $('#interval-point').style.left=pct(p);
        $('#interval-range').hidden=false; $('#interval-point').hidden=false;
      });
      protect('f1-output', () => {
        const tp=value('tp'),fp=value('fp'),fn=value('fn');
        const metric=(a,b)=>b===0?'undefined':pct(a/b);
        output('f1-output',`F1: ${metric(2*tp,2*tp+fp+fn)}`,`Precision: ${metric(tp,tp+fp)} · Recall: ${metric(tp,tp+fn)}`);
      });
      protect('reliability-output', () => {
        const p=value('probability',false)/100,k=value('attempts');
        output('reliability-output',`${pct(1-(1-p)**k)} at least one success`,`${pct(p**k)} all ${k} attempts succeed · Independent, identical attempts assumed`);
      });
      protect('cost-output', () => {
        const cases=value('cost-cases'),trials=value('cost-trials'),input=value('input-tokens'),out=value('output-tokens'),ip=value('input-price',false),op=value('output-price',false);
        const cost=cases*trials*(input*ip+out*op)/1e6;
        output('cost-output',`$${cost.toLocaleString('en-US',{minimumFractionDigits:2,maximumFractionDigits:2})} estimated token charges`,`${(cases*trials).toLocaleString('en-US')} trials · Excludes graders, tools, retries, and infrastructure`);
      });
    }
    all('.tool input').forEach(el => el.addEventListener('input',calculate)); calculate();
  }
})();
