oer.materials.view_item = {};

oer.materials.view_item.init = function() {
  var $navigation = $("div.view-item-navigation");
  $navigation.find("a.item-link").click(
    function() {
      $navigation.find("form").attr("action", $(this).attr("href")).submit();
      return false;
  }); 
};
