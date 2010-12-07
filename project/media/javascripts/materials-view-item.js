$(function() {
  
  $(".view-item-navigation a.item-link").click(function() {
    $(".view-item-navigation form").attr("action", $(this).attr("href")).submit();
    return false;
  }); 
});
