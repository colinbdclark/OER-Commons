oer.tags_form = {};

oer.tags_form.init = function() {
  var $form = $("form[name='tags']");
  var $input = $form.find("textarea[name='tags']");
  
  $form.find("div.other-tags").delegate("a", "click",
    function(e) {
      e.preventDefault();
      var value = $(this).text();
      var tags = $.grep($input.val().split("\n"), function(t) { return $.trim(t) !== ""; });
      if ($.inArray(value, tags) == -1) {
        tags.push(value);
        $input.val(tags.join("\n"));
      }
    }
  );
};