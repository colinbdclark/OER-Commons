var DescribeStep = function (tool) {
  this.tool = tool;
  var $step = this.$step = $("#step-describe");

  $step.find("ul.learning-goals-widget").learningGoalsWidget();

  oer.autocomplete_list_widget.init();

  var $document = $(document);

  // Alignment tags
  var $description = $("#align-tag-description");
  var $alignButton = $("#align-form-buttons a.align");
  var $clearButton = $("#align-form-buttons a.clear");

  var initDropdown = function ($dropdown) {
    var $field = $dropdown.closest("div.field");
    var $nextFields = $field.nextAll("div.field");
    var $nextDropdowns = $nextFields.find("select");
    var $prevFields = $field.prevAll("div.field");
    var $prevDropdowns = $prevFields.find("select");
    var $nextDropdown = $nextDropdowns.first();
    $dropdown.change(function () {
      var value = $dropdown.val();
      $description.hide();
      $alignButton.addClass("disabled");
      $nextDropdowns.each(function() {
        $(this).attr("disabled", "disabled").find("option").slice(1).remove();
      });
      if (value !== "-") {
        var data = {};
        data[$dropdown.attr("name")] = value;
        $prevDropdowns.each(function () {
          var $d = $(this);
          data[$d.attr("name")] = $d.val();
        });
        $document.trigger(oer.align_form.LOADING_EVENT);
        $field.addClass("loading");
        $.post($nextDropdown.data("source"), data, function (data) {
          var firstOptionText = $nextDropdown.find("option").first().text();
          oer.align_form.load_options($nextDropdown, data);
          $nextDropdown.find("option").first().text(firstOptionText);
          $nextDropdown.removeAttr("disabled");
          $document.trigger(oer.align_form.LOADED_EVENT);
          $nextDropdown.focus();
        });
      }
    });
  };


  var $standardDropdown = $step.find("#id_curriculum_standard");
  initDropdown($standardDropdown);
  initDropdown($step.find("#id_curriculum_grade"));
  initDropdown($step.find("#id_curriculum_category"));

  var $tagDropdown = $step.find("#id_curriculum_tag");

  $tagDropdown.change(function () {
    var value = $tagDropdown.val();
    if (value === "-") {
      $alignButton.addClass("disabled");
      $description.hide();
    } else {
      $alignButton.removeClass("disabled");
      var code = $tagDropdown.find("option:selected").data("code");
      $document.trigger(oer.align_form.LOADING_EVENT);
      $description.load("/curriculum/get_tag_description/" + code, function () {
        $document.trigger(oer.align_form.LOADED_EVENT);
        $description.fadeIn();
      });
    }
  });

  var $tags = $step.find("ul.align-tags");
  $alignButton.click(function(e) {
    e.preventDefault();
    if ($alignButton.hasClass("disabled")) {
      return;
    }
    var value = $tagDropdown.val();
    if (value === "-") {
      return;
    }
    var code = $tagDropdown.find("option:selected").data("code");
    if ($tags.find("li[data-id='" + value + "']").length) {
      return;
    }
    var $tag = $.tmpl("align-user-tag", {
      id: value,
      code: code,
      url: "#"
    });
    $tag.append($('<input type="hidden" name="alignment_tags">').val(value));
    $tag.appendTo($tags);
    $clearButton.removeClass("disabled");
  });

  $tags.delegate("a", "click", function(e) {
    e.preventDefault();
  });

  $tags.delegate("a.delete", "click", function(e) {
    $(e.currentTarget).closest("li").remove();
  });

  if ($tags.children().length) {
    $clearButton.removeClass("disabled");
  }

  $clearButton.click(function(e) {
    e.preventDefault();
    if ($clearButton.hasClass("disabled")) {
      return;
    }
    $tags.empty();
    $clearButton.addClass("disabled");
  });

  $document.trigger(oer.align_form.LOADING_EVENT);
  $.post($standardDropdown.data("source"), function (data) {
    var firstOptionText = $standardDropdown.find("option").first().text();
    oer.align_form.load_options($standardDropdown, data);
    $standardDropdown.find("option").first().text(firstOptionText);
    $document.trigger(oer.align_form.LOADED_EVENT);
  });

};
