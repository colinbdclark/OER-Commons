oer.tags_form = {};

oer.tags_form.init = function() {
    var $form = $("form[name='tags']");
    var $input = $form.find("#id_tags");
    var $user_tags = $("ul.user-tags");

    $input.autocomplete({
    minLength : 2,
    source : "/autocomplete/tags/tag/name",
    select : function(event, ui) {
        $form.submit();
    }
    });

    $.template("user-tags-item", '<li id="tag${id}"><a href="#" class="delete">Delete</a><div><a href="${url}">${name}</a></div></li>');

    $form.submit(function(e) {
        e.preventDefault();
        var value = $input.val().trim();
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
        console.log(tag_id);
    });
};