oer.authoring = {};

oer.authoring.init_edit_lesson = function() {
  var $form = $("#edit-lesson-form");

  var $student_levels = $form.find("div.student-levels");
  $student_levels.find("a").click(function(e) {
      e.preventDefault();
      $student_levels.children("ul").hide();
      $(this).hide();
      $student_levels.find("div.field ul").fadeIn();
  });


  var autosave = function() {
    var serialized = $form.data("serialized");
    var current_serialized = $form.serialize();
    if (serialized === undefined) {
        $form.data("serialized", current_serialized);
    } else {
        if (serialized !== current_serialized) {
            $form.submit();
            $form.data("serialized", current_serialized);
        }
    }
    setTimeout(autosave, 10000);
  };

  autosave();

  var $goals_field = $form.find("div.field.goals");
  var $goals_list = $goals_field.find("ul");
  $goals_field.find("a").click(function(e) {
      e.preventDefault();
      var $item = $goals_list.find("li").eq(0).clone();
      $item.find("input").val("").removeAttr("id");
      $item.appendTo($goals_list);
  });


  $.validator.addMethod("null", function(value, element) {
      return true;
  }, "");
  var validator = $form.validate({
    rules: {
        title: "required",
        summary: "required",
        subjects: "required",
        goals: "null"
    },
    submitHandler: function(form) {
        $.post($form.attr("action"), $form.serialize(), function(response) {
            if (response.status === "success") {
                oer.status_message.success(response.message, true);
            } else if (response.status === "error") {
                console.log(response.errors);
                validator.showErrors(response.errors);
            }
        });
    }
  });
};