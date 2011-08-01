oer.authoring = {};

oer.authoring.autosave = function($form) {
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
    setTimeout(function() {
        oer.authoring.autosave($form);
    }, 5000);
};

oer.authoring.init_define_form = function() {
    var $form = $("#define-form");

    oer.authoring.autosave($form);

    var $student_levels = $form.find("div.student-levels");
    $student_levels.find("a").click(function(e) {
        e.preventDefault();
        $student_levels.children("ul").hide();
        $(this).hide();
        $student_levels.find("div.field ul").fadeIn();
    });

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
            goals: "null",
            language: "required"
        },
        submitHandler: function(form) {
            $.post($form.attr("action"), $form.serialize(), function(response) {
                if (response.status === "success") {
                    oer.status_message.success(response.message, true);
                } else if (response.status === "error") {
                    validator.showErrors(response.errors);
                }
            });
        }
    });
};

oer.authoring.init_organize_form = function() {
    var $form = $("#organize-form");

    oer.authoring.autosave($form);

    $("#id_instruction_date").datepicker({dateFormat: "mm/dd/yy"});

    oer.autocomplete_list_widget.init();

    var validator = $form.validate({
        rules: {
            instruction_date: "date"
        },
        submitHandler: function(form) {
            $.post($form.attr("action"), $form.serialize(), function(response) {
                if (response.status === "success") {
                    oer.status_message.success(response.message, true);
                } else if (response.status === "error") {
                    validator.showErrors(response.errors);
                }
            });
        }
    });


    var $dialog = $("#align-dialog").dialog({
        modal : true,
        width : "650",
        height : "auto",
        position: ["center", 150],
        autoOpen : false,
        resizable : false
    });

    var $document = $(document);
    $document.bind(oer.align_form.LOADING_EVENT, function() {
        $dialog.dialog("widget").addClass("loading");
    });
    $document.bind(oer.align_form.LOADED_EVENT, function() {
        $dialog.dialog("widget").removeClass("loading");
    });

    var $form = $("#align-form");
    var $form_user_tags = $form.find("ul.align-user-tags");

    var $align = $("section.align");
    var $align_user_tags = $align.find("ul.align-user-tags");

    var $all_user_tags = $("ul.align-user-tags");
    oer.align_form.init_user_tags($all_user_tags, $form);
    oer.align_form.init_tag_tooltip($all_user_tags.find("a:first"));

    var $show_form_btn = $("#show-align-form");

    $show_form_btn.click(function(e) {
        e.preventDefault();
        var initialized = !!$form.find("#id_curriculum_standard option").length;
        if (initialized) {
            oer.align_form.reset();
        } else {
            oer.align_form.init();
            $dialog.dialog("option", "title", "Align OER");
            $align_user_tags.children("li").each(function(i, el) {
                var $li = $(el).clone(true);
                $form_user_tags.append($li);
            });
            $document.trigger(oer.align_form.TAGS_CHANGED_EVENT);
        }
        $dialog.dialog("open");
    });

    var $image_widget = $form.find("section.image");
    var $image = $image_widget.find("img");
    var $image_upload = $image_widget.find("a.upload");
    var $image_remove = $image_widget.find("a.remove");
    $image_upload.upload({
        action: $image_upload.attr("href"),
        onComplete: function(response) {
            response = $.parseJSON(response);
            if (response.status === "error") {
                oer.status_message.error(response.message, true);
            } else if (response.status === "success") {
                $image.attr("src", response.url);
                $image_remove.show();
            }
            $image_widget.removeClass("loading");
            $image.show();
        },
        onSubmit: function() {
            $image_widget.addClass("loading");
            $image.hide();
        }
    });
    $image_remove.click(function(e) {
        e.preventDefault();
        $image.attr("src", "http://placehold.it/220x150/dddddd/333333&text=No%20image");
        $image_remove.hide();
        $.post($image_remove.attr("href"), function(response) {
            oer.status_message.success(response.message, true);
        });
    });
};

$.template("authoring-outline-item", '<input name="title" value="" type="text" /><input type="hidden" name="id" value="${id}" /><span class="handle rc3"></span><span class="remove rc3">x</span>');

oer.authoring.init_outline_form = function() {
    var $form = $("#outline-form");
    
    oer.authoring.autosave($form);

    $form.submit(function(e) {
        e.preventDefault();
        $.post($form.attr("action"), $form.serialize(), function(response) {
            if (response.status === "success") {
                oer.status_message.success(response.message, true);
            }
        });
    });

    var $chapters = $form.find("#chapters");

    var $add_chapter_btn = $form.find("a.add");
    $add_chapter_btn.click(function(e) {
        e.preventDefault();
        var $li = $("<li></li>").addClass("loading");
        $li.appendTo($chapters);
        $.post(window.location.href, {"add-chapter": "yes"}, function(response) {
            $.tmpl("authoring-outline-item", response).appendTo($li);
            $li.removeClass("loading");
        });
    });

    $chapters.delegate("span.remove", "click", function(e) {
        e.preventDefault();
        apprise("Delete this chapter?", {verify: true}, function(r) {
            if (r) {
                var $chapter = $(e.target).closest("li");
                $.post(document.location.href, {"delete-chapter": "yes", "id": $chapter.data("id")});
                $chapter.remove();
            }
        });
    });

    $chapters.sortable({
        placeholder: "ui-state-highlight",
        cursor: "crosshair",
        handle: ".handle"
    });
};