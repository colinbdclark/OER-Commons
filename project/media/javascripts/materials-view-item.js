oer.materials.view_item = {};

oer.materials.view_item.init = function() {
  var $navigation = $("div.view-item-navigation");
  $navigation.find("a.item-link").click(
    function(e) {
      e.preventDefault();
      $navigation.find("form").attr("action", $(this).attr("href")).submit();
  }); 
  
  var $rate_form = $("form[name='rate']");
  var $show_rate_form_button = $("div.view-item a.rate-item");
  $show_rate_form_button.click(
    function(e) {
      e.preventDefault();
      var $this = $(this);
      $rate_form.find("select").val("5");
      $rate_form.fadeIn(300);
      $this.hide();
    }
  );
  
  $rate_form.find("a.cancel").click(
    function(e) {
      e.preventDefault();
      $rate_form.hide();
      $show_rate_form_button.show();
    }
  );
  
  $rate_form.find("a.rate").click(
    function(e) {
      e.preventDefault();
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
    }
  );
  
};

oer.materials.view_item.init_content_actions = function() {
  var $content_actions = $("#content div.content-actions");
  $content_actions.delegate("dl dt a", "click",
    function(e) {
      e.preventDefault();
      e.stopPropagation();
      var $menu = $(this).closest("dl");
      $content_actions.find("dl").not($menu).removeClass("active");
      if ($menu.hasClass("active")) {
        $menu.removeClass("active");
      } else {
        $menu.addClass("active");    
      }
    }
  );
  
  $(document).click(
    function(event) {
      $content_actions.find("dl").removeClass("active");
    }
  );
};
