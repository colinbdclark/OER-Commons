var DescribeStep = function (tool) {
  this.tool = tool;
  this.$form = $("#describe-form");

  this.$form.find("#id_learning_goals").tagit({
    allowSpaces: true,
    placeholderText: "Enter new learning goal"
  });

  this.$form.find("#id_keywords").tagit({
    allowSpaces: true,
    placeholderText: "Enter new keyword"
  });

  var $step = $("#step-describe");
  $step.find("div.buttons a").click(function(e) {
    e.preventDefault();
    tool.slider.slideTo($(this).attr("href"));
  });

};
