const $ = (id) => document.getElementById(id);
function node(tag, text, cls) { const el = document.createElement(tag); el.textContent = text; if (cls) el.className = cls; return el; }
function sourceLink(doc) { const a = node('a', `Ley 24.240 · Art. ${doc.article} ↗`); a.href = 'https://www.argentina.gob.ar/normativa/nacional/ley-24240-638/actualizacion'; a.target = '_blank'; a.rel = 'noopener noreferrer'; return a; }
fetch('/health').then(r => { if (!r.ok) throw Error(); return r.json(); }).then(data => { $('mode').textContent = 'DEMO LISTA'; $('article-count').textContent = data.corpus.articles; $('snapshot-date').textContent = new Date(data.corpus.retrieved_at).toLocaleDateString('es-AR'); }).catch(() => { $('mode').textContent = 'SIN CONEXIÓN'; });
document.querySelectorAll('[data-query]').forEach(button => button.addEventListener('click', () => { $('question').value = button.dataset.query; $('question').focus(); }));
$('query-form').addEventListener('submit', async (event) => {
  event.preventDefault(); $('error').textContent = ''; $('submit').disabled = true; $('submit').textContent = 'Buscando evidencia…';
  try {
    const response = await fetch('/api/ask', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ question: $('question').value }) });
    if (!response.ok) throw Error(response.status === 429 ? 'La demo está ocupada. Reintentá en un minuto.' : 'No se pudo completar la consulta. Verificá el servidor e intentá otra vez.');
    const data = await response.json(); $('results').hidden = false; $('empty').hidden = true;
    $('timing').textContent = `${data.latency_ms} ms · ${data.mode}${data.fallback ? ' / respaldo extractivo' : ''}`;
    $('result-message').textContent = data.message; $('claims').replaceChildren(); $('evidence').replaceChildren(); $('trace').replaceChildren();
    const docs = new Map(data.evidence.map(d => [d.id, d]));
    data.claims.forEach((claim, index) => { const card = node('article', '', 'claim'); card.append(node('span', `EVIDENCIA ${String(index + 1).padStart(2, '0')}`, 'eyebrow'), node('p', claim.statement), node('blockquote', claim.quote), sourceLink(docs.get(claim.evidence_id))); $('claims').append(card); });
    data.evidence.forEach(doc => { const section = node('article', '', 'full-article'); section.append(sourceLink(doc), node('p', doc.text)); $('evidence').append(section); });
    data.trace.forEach(step => { const item = node('li', ''); item.append(node('strong', step.step), node('span', step.status)); if (step.queries) item.append(node('p', step.queries.join(' → '))); if (step.query) item.append(node('p', step.query)); if (step.reason) item.append(node('p', step.reason)); if (step.method) item.append(node('p', step.method)); $('trace').append(item); });
    $('results').scrollIntoView({ behavior: 'smooth', block: 'start' });
  } catch (error) { $('error').textContent = error.message; }
  finally { $('submit').disabled = false; $('submit').textContent = 'Explorar la ley ↗'; }
});
