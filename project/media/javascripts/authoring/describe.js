var DescribeStep = function (tool) {
  this.tool = tool;
  this.$step = $("#step-describe");

  this.$step.find("#id_learning_goals").tagit({
    allowSpaces: true,
    placeholderText: "Enter new learning goal"
  });

  this.$step.find("#id_keywords").tagit({
    allowSpaces: true,
    placeholderText: "Enter new keyword"
  });

  var $step = $("#step-describe");
  $step.find("div.buttons a").click(function(e) {
    e.preventDefault();
    tool.slider.slideTo($(this).attr("href"));
  });

};
