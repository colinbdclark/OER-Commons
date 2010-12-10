oer.advanced_search = {}

oer.advanced_search.init = function() {
  
  var $form = $("form[name='advanced-search']");
  
  $form.find(".filter dd :checkbox").click(function() {
    $checkbox = $(this);
    $filter = $checkbox.parents(".filter").first();
    if ($checkbox.attr("checked")) {
      if ($filter.find("dd :checkbox").length == $filter.find("dd :checkbox[checked=true]").length) {
        $filter.find("dt :checkbox").attr("checked", true);
      }
    } else {
      $filter.find("dt :checkbox").attr("checked", false);
    }
  });

  $form.find(".filter dt :checkbox").click(function() {
    $checkbox = $(this);
    $filter = $checkbox.parents(".filter").first();
    $filter.find(".collapsed").removeClass("collapsed").addClass("expanded");
    if ($checkbox.attr("checked")) {
      $filter.find("dd :checkbox").attr("checked", true);
    } else {
      $filter.find("dd :checkbox").attr("checked", false);
    }
  });
  
  oer.collapsibles.init($("#content"));
  
};