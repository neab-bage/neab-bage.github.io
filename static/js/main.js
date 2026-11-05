// Menu no celular: abre/fecha a navegação principal.
(function () {
  const btn = document.querySelector('.menu-btn');
  const nav = document.getElementById('menu');
  if (!btn || !nav) return;

  function fechar() {
    btn.setAttribute('aria-expanded', 'false');
    nav.classList.remove('aberto');
  }

  btn.addEventListener('click', function () {
    const aberto = btn.getAttribute('aria-expanded') === 'true';
    btn.setAttribute('aria-expanded', String(!aberto));
    nav.classList.toggle('aberto', !aberto);
  });

  document.addEventListener('keydown', function (e) {
    if (e.key === 'Escape') fechar();
  });

  // ao navegar, fecha o menu
  nav.addEventListener('click', function (e) {
    if (e.target.closest('a')) fechar();
  });
})();
