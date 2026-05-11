/**
 * back-link.js
 * Atualiza o link "Voltar" do back-bar de cada artigo de conhecimento
 * para apontar a sub-secção correta (atualidade, opiniao, estrategia, regulamentos).
 *
 * Funcionamento:
 *   - Lê o slug a partir de window.location.pathname
 *     (formato esperado: /conhecimento/<slug>/  — clean URLs)
 *   - Faz fetch ao catálogo
 *   - Encontra a entrada cujo slug corresponde
 *   - Atualiza href e texto do <a class="back-link">
 *
 * Fallback: se fetch falhar, o link estático (../atualidade/) continua a funcionar.
 *
 * Os artigos vivem em conhecimento/<slug>/index.html, portanto:
 *   - para chegar à raiz a partir do artigo: ../../
 *   - para chegar a um hub irmão: ../<seccao>/
 */
(function () {
  const link = document.querySelector('.back-link');
  if (!link) return;

  const path = window.location.pathname;
  // Aceita /conhecimento/<slug>/ ou /conhecimento/<slug>
  const m = path.match(/\/conhecimento\/([^/]+)\/?$/);
  if (!m) return;
  const slug = m[1];
  // Excluir os próprios hubs
  if (['atualidade', 'opiniao', 'estrategia', 'regulamentos'].includes(slug)) return;

  const SECTION_LABELS = {
    atualidade:   'Atualidade',
    opiniao:      'Opinião',
    estrategia:   'Estratégia e Gestão',
    regulamentos: 'Regulamentos e Conceitos',
  };

  // Catálogo está na raiz; do artigo (depth 2) sobe ../../
  fetch('../../conhecimento-catalog.json')
    .then(r => r.ok ? r.json() : Promise.reject(r.status))
    .then(data => {
      const entry = (data.articles || []).find(a => a.slug === slug);
      if (!entry || !entry.subseccao) return;
      const sec = entry.subseccao;
      const label = SECTION_LABELS[sec] || 'Conhecimento';
      // De conhecimento/<slug>/ para conhecimento/<sec>/ é ../<sec>/
      link.href = '../' + sec + '/';
      link.innerHTML = '&larr; Voltar a ' + label;
    })
    .catch(err => { /* silencioso, fallback estatico mantem-se */ });
})();
