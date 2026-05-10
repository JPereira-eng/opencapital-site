/**
 * back-link.js
 * Atualiza o link "Voltar" do back-bar de cada artigo de conhecimento
 * para apontar a sub-secção correta (atualidade, opiniao, estrategia, regulamentos),
 * em vez do link genérico para conhecimento.html (que e redirect).
 *
 * Funcionamento:
 *   - Le o slug actual a partir de window.location.pathname
 *   - Faz fetch a /conhecimento-catalog.json
 *   - Encontra a entrada cujo slug corresponde
 *   - Atualiza href e texto do <a class="back-link">
 *
 * Fallback: se fetch falhar ou slug nao for encontrado, o link estatico
 * (../conhecimento/atualidade.html) continua a funcionar.
 */
(function () {
  const link = document.querySelector('.back-link');
  if (!link) return;

  const path = window.location.pathname;
  const m = path.match(/\/conhecimento\/([^/]+)\.html$/);
  if (!m) return;
  const slug = m[1];

  const SECTION_LABELS = {
    atualidade:   'Atualidade',
    opiniao:      'Opinião',
    estrategia:   'Estratégia e Gestão',
    regulamentos: 'Regulamentos e Conceitos',
  };

  fetch('../conhecimento-catalog.json')
    .then(r => r.ok ? r.json() : Promise.reject(r.status))
    .then(data => {
      const entry = (data.articles || []).find(a => a.slug === slug);
      if (!entry || !entry.subseccao) return;
      const sec = entry.subseccao;
      const label = SECTION_LABELS[sec] || 'Conhecimento';
      link.href = '../conhecimento/' + sec + '.html';
      link.innerHTML = '&larr; Voltar a ' + label;
    })
    .catch(err => { /* silencioso, fallback estatico mantem-se */ });
})();
