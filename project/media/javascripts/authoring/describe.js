var DescribeStep = function (tool) {
  this.tool = tool;
  this.$step = $("#step-describe");

  this.$step.find("ul.learning-goals-widget").learningGoalsWidget();

  oer.autocomplete_list_widget.init();

};
