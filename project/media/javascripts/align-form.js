/* Form to align resource to a certain curriculum standards tag */

oer.align_form = {};

oer.align_form.LOADING_EVENT = "oer-align-form-loading";
oer.align_form.LOADED_EVENT = "oer-align-form-loaded";

$.template("align-user-tags-item", '<li data-id="${id}" class="tag rc3"><a href="${url}">${code}</a> <a href="#" class="delete">x</a></li>');

oer.align_form.init_tag_tooltip = function($a) {
  $a.each(function() {
    var $this = $(this);
    $this.qtip({
        content: {
            text: 'Loading...',
            ajax: {
                url: "/curriculum/get_tag_description/" + $this.text()
            }
        },
        position: {
            target: "event",
            my: "bottom center",
            at: "top center",
            effect: false
        },
        style: {
            classes: "ui-tooltip-shadow ui-tooltip-rounded"
        }
    });
  });
};

oer.align_form.init_user_tags = function($user_tags, $form) {
    $user_tags.delegate("a.delete", "click", function(e) {
        e.preventDefault();
        var $this = $(this);
        var $li = $this.closest("li");
        var id = $li.data("id");
        $.post($form.data("delete-url"), {
                    id : id
                }, function() {
                });
        var code = $this.prev('a').text();
        var $lis = $user_tags.find("a:econtains(" + code + ")").parent();
        $lis.fadeOut(250, function() {
            $(this).detach();
        });
    });
};

oer.align_form.init = function() {

    var $form = $("#align-form");
    var $user_tags = $("ul.align-user-tags");

    oer.align_form.init_user_tags($user_tags, $form);

    var $buttons = $form.find("#align-form-buttons");
    $buttons.find(":submit").button();

    var $standard = $form.find("#id_curriculum_standard");

    var $grade = $form.find("#id_curriculum_grade");

    var $category = $form.find("#id_curriculum_category");

    var $tag = $form.find("#id_curriculum_tag");

    oer.align_form.init_dropdown($standard);
    oer.align_form.init_dropdown($grade);
    oer.align_form.init_dropdown($category);

    var $document = $(document);

    $document.trigger(oer.align_form.LOADING_EVENT);
    $.post($standard.data("source"), function(data) {
        oer.align_form.load_options($standard, data);
        $document.trigger(oer.align_form.LOADED_EVENT);
    });

    $tag.change(function() {
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
        var $existing_tag = $user_tags.find("a:econtains(" + code + ")").closest("li");
        if ($existing_tag.length) {
            $existing_tag.effect("pulsate", 200);
            return;
        }
        $document.trigger(oer.align_form.LOADING_EVENT);
        $.post($form.attr("action"), {
                    tag : value
                }, function(data) {
                    if (data.status === "success") {
                        var $tags = $.tmpl("align-user-tags-item", data.tag).appendTo($user_tags);
                        if (window.rocon != undefined) {
                            $tags.each(function(e, el) {
                                rocon.update(el);
                            });
                        }
                        oer.align_form.init_tag_tooltip($tags.find("a:first"));
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
    $dropdown.change(function() {
        var value = $dropdown.val();
        $buttons.hide();
        $next_fields.hide();
        $next_dropdowns.empty();
        if (value !== "-") {
            var data = {};
            data[$dropdown.attr("name")] = value;
            $prev_dropdowns.each(function() {
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

oer.align_tags_portlet = {};

oer.align_tags_portlet.init = function() {

    var $dialog = $("#align-dialog").dialog({
        modal : true,
        width : "650",
        height : "auto",
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

    var $portlet = $("section.align-item-tags");
    var $portlet_user_tags = $portlet.find("ul.align-user-tags");

    var $all_user_tags = $("ul.align-user-tags");
    oer.align_form.init_user_tags($all_user_tags, $form);
    oer.align_form.init_tag_tooltip($all_user_tags.find("a:first"));

    var $item_tags = $portlet.find("ul:first li.tag");
    oer.align_form.init_tag_tooltip($item_tags.find("a:first"));

    $portlet.find(".login a").click(function(e) {
        e.preventDefault();
        oer.login.show_popup();
    });

    $document.bind(oer.login.LOGGED_IN_EVENT, function(e) {
        $portlet_user_tags.empty();
        $.getJSON($form.attr("action").replace("/add/", "/get-tags/") + "?randNum=" + new Date().getTime(), function(data) {
            $.each(data.tags, function(index, tag) {
                $item_tags.filter(":econtains(" + tag.code + ")").fadeOut(300);
                var $tag = $.tmpl("align-user-tags-item", tag).appendTo($portlet_user_tags);
                if (window.rocon != undefined) {
                    rocon.update($tag.get(0));
                }
                oer.align_form.init_tag_tooltip($tag.find("a:first"));
            });
        });
    });

    var $show_form_btn = $("#show-align-form");

    $show_form_btn.click(function(e) {
        e.preventDefault();
        var $item = $("#content article.item");

        oer.login.check_login(function() {
            var initialized = !!$form.find("#id_curriculum_standard option").length;
            if (initialized) {
                oer.align_form.reset();
            } else {
                oer.align_form.init();
                $dialog.dialog("option", "title", "Align " + $item.find("h1 a").first().text());
                $portlet_user_tags.children("li").each(function(i, el) {
                    var $li = $(el).clone(true);
                    $form_user_tags.append($li);
                });
            }
            $dialog.dialog("open");
        });
    });
};
