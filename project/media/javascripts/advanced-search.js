oer.advanced_search = {};

oer.advanced_search.init = function () {

  var $form = $("form[name='advanced-search']");

  $form.find(".filter dd :checkbox").click(function () {
    var $checkbox = $(this);
    var $filter = $checkbox.parents(".filter").first();
    if ($checkbox.attr("checked")) {
      if ($filter.find("dd :checkbox").length == $filter.find("dd :checkbox[checked=true]").length) {
        $filter.find("dt :checkbox").attr("checked", true);
      }
    } else {
      $filter.find("dt :checkbox").attr("checked", false);
    }
  });

  $form.find(".filter dt :checkbox").click(function () {
    var $checkbox = $(this);
    var $filter = $checkbox.parents(".filter").first();
    $filter.find(".collapsed").removeClass("collapsed").addClass("expanded");
    if ($checkbox.attr("checked")) {
      $filter.find("dd :checkbox").attr("checked", true);
    } else {
      $filter.find("dd :checkbox").attr("checked", false);
    }
  });

  var $standard = $form.find("#id_curriculum_standard");
  var $grade = $form.find("#id_curriculum_grade");
  var $category = $form.find("#id_curriculum_category");
  var $tag = $form.find("#id_curriculum_tag");

  oer.align_form.init_dropdown($standard);
  oer.align_form.init_dropdown($grade);
  oer.align_form.init_dropdown($category);

  var $standard_input = $form.find("input[name='f.alignment_standard']");
  var $grade_input = $form.find("input[name='f.alignment_grade']");
  var $category_input = $form.find("input[name='f.alignment_category']");
  var $tag_input = $form.find("input[name='f.alignment']");
  var $cluster_input = $form.find("input[name='f.cluster']");

  var $document = $(document);

  $document.trigger(oer.align_form.LOADING_EVENT);
  $.post($standard.data("source"), function (data) {
    oer.align_form.load_options($standard, data);
    $document.trigger(oer.align_form.LOADED_EVENT);
  });

  $form.submit(function (e) {
    var standard = $standard.val();
    if (standard && standard !== "-") {
      $standard_input.val(standard);
    } else {
      $standard_input.attr("disabled", "disabled");
    }
    $standard.attr("disabled", "disabled");

    var grade = $grade.val();
    if (grade && grade !== "-") {
      $grade_input.val(grade);
    } else {
      $grade_input.attr("disabled", "disabled");
    }
    $grade.attr("disabled", "disabled");

    var category = $category.val();
    if (category && category !== "-") {
      $category_input.val(category);
    } else {
      $category_input.attr("disabled", "disabled");
    }
    $category.attr("disabled", "disabled");

    var code = $tag.find(":selected").data("code");
    if (code) {
      if (code.match(/^cluster:/)) {
        code = code.split(":")[1];
        $cluster_input.val(code);
        $tag_input.attr("disabled", "disabled");
      } else {
        $tag_input.val(code);
        $cluster_input.attr("disabled", "disabled");
      }
      $standard_input.attr("disabled", "disabled");
      $grade_input.attr("disabled", "disabled");
      $category_input.attr("disabled", "disabled");
    } else {
      $tag_input.attr("disabled", "disabled");
      $cluster_input.attr("disabled", "disabled");
    }
    $tag.attr("disabled", "disabled");
  });

  oer.collapsibles.init($("#content"));

};
