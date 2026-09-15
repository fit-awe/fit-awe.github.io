// Close the mobile menu when following the homepage section link.
document.addEventListener('click', function (event) {
  if (!event.target.closest('.industry-nav-link')) return;
  var menu = document.querySelector('.navbar-collapse');
  if (!menu || !window.jQuery) return;
  var $menu = window.jQuery(menu);
  if (menu.classList.contains('collapsing')) {
    $menu.one('shown.bs.collapse', function () { $menu.collapse('hide'); });
  } else if (menu.classList.contains('in')) {
    $menu.collapse('hide');
  }
});
