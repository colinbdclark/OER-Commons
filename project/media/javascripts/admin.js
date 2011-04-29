oer.admin = {};

oer.admin.tags = {};

oer.admin.tags.init = function() {
    var $tags = $("div.form-row.tags ul");
    $tags.delegate("a.delete", "click", function(e) {
        e.preventDefault();
        var $this = $(this);
        var $li = $this.closest("li");
        var tag_name = $li.find("span").text();
        $li.fadeOut(300);
        $.post(window.location + "delete_tag/", {
            name : tag_name
        }, function(data) {
            if (data.status == "success") {
                $li.remove();
            } else {
                $li.show();
            }
        });
    });
};