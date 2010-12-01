$(function() {
  
  function switch_collapsible(button) {
    $button = $(button);
    $parent = $button.parents(".collapsible").first();
    if ($button.hasClass("collapsed")) {
      $parent.find(".collapsed").removeClass("collapsed").addClass("expanded");
    } else {
      $parent.find(".expanded").removeClass("expanded").addClass("collapsed");
    }
  } 
  
  $(".expand-button").click(function() {switch_collapsible(this); return false;});
  $(".expand-link").click(function() {switch_collapsible(this); return false;});
  $(".expand-all").click(function() {
    $button = $(this);
    $parent = $button.parents(".collapsibles").first();
    $parent.find(".collapsed").removeClass("collapsed").addClass("expanded");
    return false;
  });
  $(".collapse-all").click(function() {
    $button = $(this);
    $parent = $button.parents(".collapsibles").first();
    $parent.find(".expanded").removeClass("expanded").addClass("collapsed");
    return false;
  });
});
