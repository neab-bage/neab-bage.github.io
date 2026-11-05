// Navegação principal: menu do celular e grupos suspensos.
(function () {
  var btn = document.querySelector('.menu-btn');
  var nav = document.getElementById('menu');
  if (!nav) return;

  var grupos = Array.prototype.slice.call(nav.querySelectorAll('.nav__grupo'));

  function fecharGrupos(exceto) {
    grupos.forEach(function (g) {
      if (g !== exceto) {
        g.setAttribute('aria-expanded', 'false');
        g.parentNode.classList.remove('aberto');
      }
    });
  }

  function fecharTudo() {
    fecharGrupos(null);
    if (btn) {
      btn.setAttribute('aria-expanded', 'false');
      nav.classList.remove('aberto');
    }
  }

  grupos.forEach(function (g) {
    g.addEventListener('click', function (e) {
      e.stopPropagation();
      var aberto = g.getAttribute('aria-expanded') === 'true';
      fecharGrupos(g);
      g.setAttribute('aria-expanded', String(!aberto));
      g.parentNode.classList.toggle('aberto', !aberto);
    });
  });

  if (btn) {
    btn.addEventListener('click', function (e) {
      e.stopPropagation();
      var aberto = btn.getAttribute('aria-expanded') === 'true';
      btn.setAttribute('aria-expanded', String(!aberto));
      nav.classList.toggle('aberto', !aberto);
      if (aberto) fecharGrupos(null);
    });
  }

  document.addEventListener('click', function (e) {
    if (!nav.contains(e.target) && (!btn || !btn.contains(e.target))) fecharTudo();
  });

  document.addEventListener('keydown', function (e) {
    if (e.key === 'Escape') fecharTudo();
  });

  nav.addEventListener('click', function (e) {
    if (e.target.closest('a')) fecharTudo();
  });
})();
