oer.advanced_search = {};

oer.advanced_search.init = function() {

    var $form = $("form[name='advanced-search']");

    $form.find(".filter dd :checkbox").click(function() {
        $checkbox = $(this);
        $filter = $checkbox.parents(".filter").first();
        if ($checkbox.attr("checked")) {
            if ($filter.find("dd :checkbox").length == $filter.find("dd :checkbox[checked=true]").length) {
                $filter.find("dt :checkbox").attr("checked", true);
            }
        } else {
            $filter.find("dt :checkbox").attr("checked", false);
        }
    });

    $form.find(".filter dt :checkbox").click(function() {
        $checkbox = $(this);
        $filter = $checkbox.parents(".filter").first();
        $filter.find(".collapsed").removeClass("collapsed").addClass("expanded");
        if ($checkbox.attr("checked")) {
            $filter.find("dd :checkbox").attr("checked", true);
        } else {
            $filter.find("dd :checkbox").attr("checked", false);
        }
    });

    var $standard = $form.find("#id_curriculum_standard");
    var $standard_ct = $form.find("div.field.standard");

    var $grade = $form.find("#id_curriculum_grade");
    var $grade_ct = $form.find("div.field.grade");

    var $category = $form.find("#id_curriculum_category");
    var $category_ct = $form.find("div.field.category");

    var $tag = $form.find("#id_curriculum_tag");
    var $tag_ct = $form.find("div.field.tag");

    oer.align_form.init_dropdown($standard);
    oer.align_form.init_dropdown($grade);
    oer.align_form.init_dropdown($category);

    var $tag_input = $form.find("input[name='f.alignment']");

    var $document = $(document);

    $document.trigger(oer.align_form.LOADING_EVENT);
    $.post($standard.data("source"), function(data) {
        oer.align_form.load_options($standard, data);
        $document.trigger(oer.align_form.LOADED_EVENT);
    });

    $form.submit(function(e) {
        $standard.attr("disabled", "disabled");
        $grade.attr("disabled", "disabled");
        $category.attr("disabled", "disabled");
        var alignment_tag_code = $tag.find(":selected").data("code");
        if (alignment_tag_code !== undefined) {
            $tag_input.val(alignment_tag_code);
        } else {
            $tag_input.attr("disabled", "disabled");
        }
        $tag.attr("disabled", "disabled");
    });

    oer.collapsibles.init($("#content"));

};
