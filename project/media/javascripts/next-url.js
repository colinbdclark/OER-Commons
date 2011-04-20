oer.next_url = {};

oer.next_url.init = function() {
  var $form = $("form[name='next-url']");
  $(document).delegate("a.with-next-url:not(.require-login)", "click", function(e) {
    e.preventDefault();
    $form.attr("action", $(this).attr("href"));
    $form.submit();
  });
};
