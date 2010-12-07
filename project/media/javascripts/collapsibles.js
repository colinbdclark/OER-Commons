$(function() {
  
  function switch_collapsible(button) {
    $button = $(button);
    $parent = $button.closest(".collapsible");
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
    $parent = $button.closest(".collapsibles");
    $parent.find(".collapsed").removeClass("collapsed").addClass("expanded");
    return false;
  });
  $(".collapse-all").click(function() {
    $button = $(this);
    $parent = $button.closest(".collapsibles");
    $parent.find(".expanded").removeClass("expanded").addClass("collapsed");
    return false;
  });
});
