oer.saved_search = {};

oer.saved_search.init = function() {
  var $form = $("form[name='save-search']");
  var $show_form_link = $("a.save-search");
  
  var coordinates = $show_form_link.offset();
  
  $form.offset({left: coordinates.left - $form.width() + $show_form_link.width(), top: coordinates.top + 100});
  
  $show_form_link.click(
    function() {
      $form.slideDown(300);
    }
  );
  
  $form.find(":submit[name='cancel']").click(
    function() {
      $form.hide();
      return false;
    }
  );
  
  $form.submit(
    function() {
      if ($form.attr("method") == "post") {
        var data = {
          url: $form.find("input[name='url']").val(),
          title: $form.find("input[name='title']").val()
        };
        $.post($form.attr("action"), data,
          function(data) {
            var $main_column = $("div.column-main");
            $main_column.remove("div.status-message");
            var $message = $("<div></div>");
            $message.addClass("status-message").text(data).hide().prependTo($main_column).fadeIn(500).delay(3000).fadeOut(1000);
          }, "application/json");
        $form.hide();
        return false;
      }
    }
  );
  
};