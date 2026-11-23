(() => {
  'use strict';

  const $ = (id) => document.getElementById(id);
  const input = $('input');
  const output = $('output');
  const convertBtn = $('convert');
  const copyBtn = $('copy');
  const clearBtn = $('clear');
  const sampleBtn = $('sample');
  const hl = $('hl');
  const statusEl = $('status');

  const SAMPLE =
    'Byl jsem u slyšení, kde se mluvilo o obyvatelích našeho města. ' +
    'Vysoký sýr leží na stole, ale mysl se mi toulá jinam.\n\n' +
    'Náš systém analýzy nám pomohl pochopit symboly, psychologii i fyziku.';

  let lastText = '';

  function plural(n, one, few, many) {
    if (n === 1) return one;
    if (n >= 2 && n <= 4) return few;
    return many;
  }

  function setStatus(message, isError = false) {
    statusEl.textContent = message;
    statusEl.classList.toggle('error', isError);
  }

  function render(segments) {
    const frag = document.createDocumentFragment();
    for (const seg of segments) {
      if (seg.k === 'changed') {
        const el = document.createElement('mark');
        el.className = 'chg';
        el.textContent = seg.t;
        frag.append(el);
      } else if (seg.k === 'foreign') {
        const el = document.createElement('span');
        el.className = 'frn';
        el.title = 'Cizí slovo – výjimka, ponecháno beze změny';
        el.textContent = seg.t;
        frag.append(el);
      } else {
        frag.append(document.createTextNode(seg.t));
      }
    }
    output.replaceChildren(frag);
  }

  function describe(stats) {
    const parts = [];
    if (stats.changedLetters > 0) {
      const n = stats.changedLetters;
      const w = stats.changedWords;
      parts.push(
        `Změněno ${n} ${plural(n, 'písmeno', 'písmena', 'písmen')} ` +
        `v ${w} ${plural(w, 'slově', 'slovech', 'slovech')}.`
      );
    } else {
      parts.push('Žádná změna – po obojetných souhláskách tu není žádné y/ý.');
    }
    if (stats.foreignKept > 0) {
      const f = stats.foreignKept;
      parts.push(`Cizí ${plural(f, 'slovo', 'slova', 'slov')} ponecháno: ${f}.`);
    }
    return parts.join(' ');
  }

  async function run() {
    const text = input.value;
    if (!text.trim()) {
      output.replaceChildren();
      lastText = '';
      copyBtn.disabled = true;
      setStatus('Napište nebo vložte nějaký text.');
      input.focus();
      return;
    }

    convertBtn.disabled = true;
    setStatus('Převádím…');
    try {
      const res = await fetch('/api/convert', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text }),
      });
      const data = await res.json().catch(() => ({}));
      if (!res.ok) throw new Error(data.error || `Chyba serveru (${res.status}).`);

      lastText = data.text;
      render(data.segments);
      copyBtn.disabled = false;
      setStatus(describe(data.stats));
    } catch (err) {
      setStatus(err.message || 'Převod se nezdařil.', true);
    } finally {
      convertBtn.disabled = false;
    }
  }

  async function copyResult() {
    if (!lastText) return;
    try {
      await navigator.clipboard.writeText(lastText);
      setStatus('Výsledek je zkopírovaný do schránky.');
    } catch {
      const range = document.createRange();
      range.selectNodeContents(output);
      const sel = window.getSelection();
      sel.removeAllRanges();
      sel.addRange(range);
      setStatus('Kopírování se nepovedlo – text je vybraný, zkopírujte ho ručně (Ctrl/⌘ + C).', true);
    }
  }

  convertBtn.addEventListener('click', run);
  copyBtn.addEventListener('click', copyResult);
  sampleBtn.addEventListener('click', () => {
    input.value = SAMPLE;
    input.focus();
  });
  clearBtn.addEventListener('click', () => {
    input.value = '';
    output.replaceChildren();
    lastText = '';
    copyBtn.disabled = true;
    setStatus('');
    input.focus();
  });
  hl.addEventListener('change', () => output.classList.toggle('no-hl', !hl.checked));
  input.addEventListener('keydown', (e) => {
    if (e.key === 'Enter' && (e.ctrlKey || e.metaKey)) {
      e.preventDefault();
      run();
    }
  });

  output.classList.toggle('no-hl', !hl.checked);
})();
