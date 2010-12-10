oer.collapsibles = {};

oer.collapsibles.switch_collapsible = function($button) {
    $parent = $button.closest(".collapsible");
    if ($button.hasClass("collapsed")) {
      $parent.find(".collapsed").removeClass("collapsed").addClass("expanded");
    } else {
      $parent.find(".expanded").removeClass("expanded").addClass("collapsed");
    }
}

oer.collapsibles.init = function($container) {
  $container.find("a.expand-button").click(
    function() {
      oer.collapsibles.switch_collapsible($(this));
      return false;
    }
  );
  $container.find("a.expand-link").click(
    function() {
      oer.collapsibles.switch_collapsible($(this));
      return false;
    }
  );
  $container.find("a.expand-all").click(
    function() {
      var $parent = $(this).closest(".collapsibles");
      $parent.find(".collapsed").removeClass("collapsed").addClass("expanded");
      return false;
    }
  );
  $container.find("a.collapse-all").click(
    function() {
      var $parent = $(this).closest(".collapsibles");
      $parent.find(".expanded").removeClass("expanded").addClass("collapsed");
      return false;
    }
  );
};
