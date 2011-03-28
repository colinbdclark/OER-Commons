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
        }, "json");
    });

    $user_tags.delegate("a.delete", "click", function(e) {
        e.preventDefault();
        $this = $(this);
        $li = $this.closest("li");
        var tag_id = $li.attr("id").slice(3);
        $.post("/tags/delete", {
            id : tag_id
        }, function(response, status, request) {
            $li.fadeOut(250, function() {
                $(this).detach();
            });
        });
    });
};