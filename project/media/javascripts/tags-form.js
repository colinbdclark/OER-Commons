oer.tags_form = {};

$.template("user-tags-item", '<li id="tag${id}"><a href="#" class="delete">Delete</a><div><a href="${url}">${name}</a></div></li>');

oer.tags_form.init = function() {
    var $form = $("#add-tags-form");
    var $input = $form.find("#id_tags");
    var $user_tags = $("ul.user-tags");

    $input.autocomplete({
    minLength : 2,
    source : "/autocomplete/tags/tag/name",
    select : function(event, ui) {
        $form.submit();
    }
    });

    $form.submit(function(e) {
        $input.autocomplete("close");
        e.preventDefault();
        var value = $.trim($input.val());
        if (value === "") {
            return;
        }
        $input.addClass("loading");
        $.post($form.attr("action"), {
            "tags" : value
        }, function(response, status, request) {
            $input.removeClass("loading");
            $.each(response.tags, function(i, tag) {
                $.tmpl("user-tags-item", tag).appendTo($user_tags);
            });
            $input.val("");
        });
    });

    $user_tags.delegate("a.delete", "click", function(e) {
        e.preventDefault();
        $this = $(this);
        $li = $this.closest("li");
        $li.fadeOut(250, function() {
            $(this).detach();
        });
        var tag_id = $li.attr("id").slice(3);
        $.post("/tags/delete", {
            id : tag_id
        }, function(response, status, request) {
        });
    });
};

oer.tags_portlet = {};

oer.tags_portlet.init = function() {
    var $body = $("body");
    if ($body.hasClass("authenticated")) {
        return;
    }
    var $portlet = $("section.portlet.item-tags");
    $portlet.find(".login a").click(function(e) {
        e.preventDefault();
        oer.login.show_popup(function() {
            var $user_tags = $("ul.user-tags");
            $user_tags.empty().hide();
            var $form = $("#add-tags-form");
            $.getJSON($form.attr("action").replace("/tags/add/", "/tags/get-tags/"), function(data, status) {
                var item_tags = data.tags;
                var user_tags = data.user_tags;
                $.each(user_tags, function(index, tag) {
                    $.tmpl("user-tags-item", tag).appendTo($user_tags);
                });
                $user_tags.fadeIn(300);
            });
        });
    });
};