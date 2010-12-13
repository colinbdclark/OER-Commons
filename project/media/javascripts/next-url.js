oer.next_url = {};

oer.next_url.init = function() {
  var $form = $("form[name='next-url']");
  $("a.with-next-url").click(function() {
    $form.attr("action", $(this).attr("href"));
    $form.submit();
    return false;
  });
};
