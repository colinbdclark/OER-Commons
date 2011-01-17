oer.send_this = {};

oer.send_this.init = function() {
  var $form = $("form[name='send-this']");
  var $show_form_link = $("a.send-this");
  
  var coordinates = $show_form_link.offset();
  
  $form.offset({left: coordinates.left - $form.width() + $show_form_link.width(), top: coordinates.top + 100});
  
  $show_form_link.click(
    function(e) {
      e.preventDefault();
      $form.slideDown(300);
    }
  );
  
  $form.find(":submit[name='cancel']").click(
    function(e) {
      e.preventDefault();
      $form.hide();
    }
  );
  
  $form.validate({
    submitHandler: function(form) {
      if ($form.attr("method") == "post") {
        var data = {
          path: $form.find("input[name='path']").val(),
          email: $form.find("input[name='email']").val(),
          comment: $form.find("textarea[name='comment']").val(),
          ajax: "yes",
          send: "send"
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
      form.submit();
    },
    rules: oer.validation.rules.send_this
  });
};
