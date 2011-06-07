/* Form to align resource to a certain curriculum standards tag */

oer.align_form = {};

oer.align_form.LOADING_EVENT = "oer-align-form-loading";
oer.align_form.LOADED_EVENT = "oer-align-form-loaded";

$.template("align-user-tags-item", '<li data-id="${id}"><a href="#" class="delete">Delete</a> <span>${code}</span></li>');

oer.align_form.init = function() {

    var $form = $("#align-form");

    var $user_tags = $("ul#align-user-tags");

    $user_tags.delegate("a.delete", "click", function(e) {
        e.preventDefault();
        $this = $(this);
        $li = $this.closest("li");
        $li.fadeOut(250, function() {
            $(this).detach();
        });
        var id = $li.data("id");
        $.post($form.data("delete-url"), {
            id : id
        }, function(response, status, request) {
        });
    });

    var $buttons = $form.find("#align-form-buttons");
    $buttons.find(":submit").button();

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

    var $document = $(document);

    $document.trigger(oer.align_form.LOADING_EVENT);
    $.post($standard.data("source"), function(data) {
        oer.align_form.load_options($standard, data);
        $document.trigger(oer.align_form.LOADED_EVENT);
    });

    $tag.change(function(e) {
        var value = $tag.val();
        if (value === "-") {
            $buttons.hide();
        } else {
            $buttons.show();
        }
    });

    $form.submit(function(e) {
        e.preventDefault();
        var value = $tag.val();
        if (value === "" || value === "-") {
            return;
        }
        var code = $tag.find(":selected").data("code");
        var $existing_tag = $user_tags.find("span:contains('" + code + "')").closest("li");
        if ($existing_tag.length) {
            $existing_tag.effect("bounce");
            return;
        }
        $document.trigger(oer.align_form.LOADING_EVENT);
        $.post($form.attr("action"), {
            tag : value
        }, function(data) {
            if (data.status === "success") {
                $.tmpl("align-user-tags-item", data.tag).hide().appendTo($user_tags).fadeIn(300); 
            }
            $document.trigger(oer.align_form.LOADED_EVENT);
        });
    });

};

oer.align_form.init_dropdown = function($dropdown) {
    var $form = $dropdown.closest("form");
    var $document = $(document);
    var $field = $dropdown.closest("div.field");
    var $next_fields = $field.nextAll("div.field");
    var $next_dropdowns = $next_fields.find("select");
    var $prev_fields = $field.prevAll("div.field");
    var $prev_dropdowns = $prev_fields.find("select");
    var $next_field = $next_fields.first();
    var $next_dropdown = $next_dropdowns.first();
    var $buttons = $form.find("#align-form-buttons");
    $dropdown.change(function(e) {
        var value = $dropdown.val();
        $buttons.hide();
        $next_fields.hide();
        $next_dropdowns.empty();
        if (value !== "-") {
            var data = {};
            data[$dropdown.attr("name")] = value;
            $prev_dropdowns.each(function(i) {
                var $d = $(this);
                data[$d.attr("name")] = $d.val();
            });
            $document.trigger(oer.align_form.LOADING_EVENT);
            $field.addClass("loading");
            $.post($next_dropdown.data("source"), data, function(data) {
                oer.align_form.load_options($next_dropdown, data);
                $next_field.show();
                $document.trigger(oer.align_form.LOADED_EVENT);
                $field.removeClass("loading");
            });
        }
    });
};

oer.align_form.load_options = function($dropdown, data) {
    $dropdown.empty();
    $dropdown.append($("<option>").val("-").text("").attr("selected", "selected"));
    if ("options" in data) {
        $.each(data.options, function(i, item) {
            var $option = $("<option>").val(item.id).text(item.name);
            if ("code" in item) {
                $option.data("code", item.code);
            }
            $dropdown.append($option);
        });
    } else if ("optgroups" in data) {
        $.each(data.optgroups, function(i, optgroup) {
            var $optgroup = $("<optgroup>").attr("label", optgroup.title);
            $.each(optgroup.items, function(j, item) {
                var $option = $("<option>").val(item.id).text(item.name);
                if ("code" in item) {
                    $option.data("code", item.code);
                }
                $optgroup.append($option);
            });
            $dropdown.append($optgroup);
        });
    }
};

oer.align_form.reset = function() {
    var $form = $("#align-form");

    $form.find("#id_curriculum_standard").val("-");

    $form.find("#id_curriculum_grade").empty();
    $form.find("div.field.grade").hide();

    $form.find("#id_curriculum_category").empty();
    $form.find("div.field.category").hide();

    $form.find("#id_curriculum_tag").empty();
    $form.find("div.field.tag").hide();

    $form.find("#align-form-buttons").hide();
};
