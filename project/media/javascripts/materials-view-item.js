oer.materials.view_item = {};

oer.materials.view_item.init = function() {
  var $navigation = $("div.view-item-navigation");
  $navigation.find("a.item-link").click(
    function() {
      $navigation.find("form").attr("action", $(this).attr("href")).submit();
      return false;
  }); 
  
  var $rate_form = $("form[name='rate']");
  var $show_rate_form_button = $("div.view-item a.rate-item");
  $show_rate_form_button.click(
    function() {
      var $this = $(this);
      $rate_form.find("select").val("5");
      $rate_form.fadeIn(300);
      $this.hide();
      return false;
    }
  );
  
  $rate_form.find("a.cancel").click(
    function() {
      $rate_form.hide();
      $show_rate_form_button.show();
      return false;
    }
  );
  
  $rate_form.find("a.rate").click(
    function() {
      var $this = $(this);
      if ($rate_form.attr("method") == "post") {
        $.post($rate_form.attr("action"), {rating: $rate_form.find("select").val()},
          function(data) {
            data = $.parseJSON(data);
            var $stars = $this.closest("div.right").find("div.stars");
            $stars.removeClass().addClass("stars").addClass(data.stars_class);
            var $main_column = $("div.column-main");
            $main_column.find("div.status-message").remove();
            $("<div></div>").addClass("status-message").text(data.message).hide().prependTo($main_column).fadeIn(300).delay(3000).fadeOut(1000, function() {$(this).remove();});
            $rate_form.hide();
            $show_rate_form_button.show();
          }, "application/json");
      } else {
        $rate_form.submit();
      }
      return false;
    }
  );
  
};
