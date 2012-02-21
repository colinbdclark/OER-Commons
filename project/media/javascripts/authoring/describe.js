var Describe = function () {

  this.$form = $("#describe-form");

  this.$form.find("#id_learning_goals").tagit({
    allowSpaces: true,
    placeholderText: "Enter new learning goal"
  });

  this.$form.find("#id_keywords").tagit({
    allowSpaces: true,
    placeholderText: "Enter new keyword"
  });

};
