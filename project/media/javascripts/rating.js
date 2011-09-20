oer.rating = {};

oer.rating.get_class = function($rating) {
  var classes = $rating.attr('class').split(/\s+/);
  for (var j = 0; j < classes.length; j++) {
    var class_name = classes[j];
    if (class_name.search(/^s\d{2}$/) !== -1) {
      return class_name;
    }
  }
};

oer.rating.submit = function(e) {
  var $this = $(this);
  var is_materials_index = $this.closest("div.materials-index").length > 0;
  oer.login.check_login(function() {
    $.post("/rate", {
      number: $this.data("number"),
      identifier: $this.data("identifier")
    }, function(data) {
      if (data.status === "success") {
        $this.removeClass("hover");
        var class_name = data.stars_class;
        $this.removeClass(oer.rating.get_class($this)).addClass(class_name);
        $this.data("initial_class", class_name);
        if (is_materials_index) {
          oer.materials.index.item_message($this.closest("article.item"), data.message);
        } else {
          oer.status_message.success(data.message, true);
        }
      } else if (data.status === "error") {
        $this.removeClass("hover");
        $this.removeClass(oer.rating.get_class($this)).addClass($this.data("initial_class"));
        if (is_materials_index) {
          oer.materials.index.item_message($this.closest("article.item"), data.message);
        } else {
          oer.status_message.error(data.message, true);
        }
      }
    });
  });
};

oer.rating.init = function() {

  var $ratings = $("div.stars");

  var star_width = $ratings.first().width() / 5;

  $.each($ratings, function(i, rating) {
    var $rating = $(rating);
    $rating.data("initial_class", oer.rating.get_class($rating));
    $rating.data("width", $rating.width());

    $rating.mouseout(function() {
      var $this = $(this);
      $this.removeClass("hover");
      $this.removeClass(oer.rating.get_class($this)).addClass($this.data("initial_class"));
    });

    $rating.mousemove(function(e) {
      var $this = $(this);
      $this.addClass("hover");
      var x = null;
      if (e.offsetX !== undefined) {
        x = e.offsetX;
      } else {
        x = e.pageX - $this.offset().left;
      }
      var number = parseInt(x / star_width) + 1;
      if (number < 1) {
        number = 1;
      }
      if (number > 5) {
        number = 5;
      }
      $this.data("number", number);
      $this.removeClass(oer.rating.get_class($this));
      $this.addClass("s" + number + "0");
    });

    $rating.click(oer.rating.submit);

  });

};
