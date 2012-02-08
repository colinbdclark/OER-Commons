var Describe = function () {
  var tool = this;

  this.$form = $("#describe-form");

  this.$form.find("#id_learning_goals").tagit({
    allowSpaces: true,
    placeholderText: "Enter new learning goal"
  });

  this.$form.find("#id_keywords").tagit({
    allowSpaces: true,
    placeholderText: "Enter new keyword"
  });

  this.$form.find("div.buttons a").click(function(e) {
    e.preventDefault();
    var $next = tool.$form.find("input[name='next']");
    if ($(this).hasClass("next")) {
      $next.val("true");
    } else {
      $next.val("false");
    }
    tool.$form.submit();
  });

};
