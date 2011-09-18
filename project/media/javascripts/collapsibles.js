oer.collapsibles = {};

oer.collapsibles.switch_collapsible = function($button) {
  var $parent = $button.closest(".collapsible");
  if ($button.hasClass("collapsed")) {
    $parent.find(".collapsed").removeClass("collapsed").addClass("expanded");
  } else {
    $parent.find(".expanded").removeClass("expanded").addClass("collapsed");
  }
};

oer.collapsibles.init = function($container) {
  $container.delegate("a.expand-button", "click", function(e) {
    e.preventDefault();
    oer.collapsibles.switch_collapsible($(this));
  });
  $container.delegate("a.expand-link", "click", function(e) {
    e.preventDefault();
    oer.collapsibles.switch_collapsible($(this));
  });
  $container.delegate("a.expand-all", "click", function(e) {
    e.preventDefault();
    var $parent = $(this).closest(".collapsibles");
    $parent.find(".collapsed").removeClass("collapsed").addClass("expanded");
  });
  $container.delegate("a.collapse-all", "click", function(e) {
    e.preventDefault();
    var $parent = $(this).closest(".collapsibles");
    $parent.find(".expanded").removeClass("expanded").addClass("collapsed");
  });
};
