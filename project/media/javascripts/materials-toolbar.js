oer.materials.toolbar = {};

oer.materials.toolbar.init = function() {
    oer.materials.toolbar.resize_iframe();

    var $iframe = $("#resource");

    $(window).resize(function(e) {
        oer.materials.toolbar.resize_iframe();
    });

    oer.materials.toolbar.init_tags();
    oer.materials.toolbar.init_save();
};

oer.materials.toolbar.resize_iframe = function() {
    var $window = $(window);
    var $iframe = $("#resource");
    var $toolbar = $("#toolbar");
    $iframe.height($window.height() - $toolbar.outerHeight());
};

oer.materials.toolbar.init_tags = function() {
    var $dialog = $("#add-tags-dialog").dialog({
    modal : true,
    width : 400,
    autoOpen : false,
    resizable : false
    });

    var $form = $("#add-tags-form");
    var $input = $form.find("#id_tags");
    var $user_tags = $dialog.find("ul.user-tags");

    $("a.tags").click(function(e) {
        e.preventDefault();
        var $this = $(this);
        oer.login.check_login(function() {
            $form.hide();
            $user_tags.empty();
            $form.attr("action", $this.attr("href"));
            $input.val("");
            $.getJSON($form.attr("action").replace("/tags/add/", "/tags/get-tags/"), function(data, status) {
                var item_tags = data.tags;
                var user_tags = data.user_tags;
                $.each(user_tags, function(index, tag) {
                    $.tmpl("user-tags-item", tag).appendTo($user_tags);
                });
                $form.show();
            });
            $dialog.dialog("option", "title", "Add tags to " + ITEM_TITLE);
            $dialog.dialog("open");
        });
    });
    oer.tags_form.init();
};

oer.materials.toolbar.init_save = function() {
    var $toolbar = $("#toolbar");
    var $save_btn = $toolbar.find("a.save");
    var $unsave_btn = $toolbar.find("a.unsave");

    $save_btn.click(function(e) {
        e.preventDefault();
        var $this = $(this);
        if ($this.hasClass("loading")) {
            return;
        }
        $this.addClass("loading");
        oer.login.check_login(function() {
            $.post($this.attr("href"), function(data) {
                if (data.status === "success") {
                    $this.hide();
                    $unsave_btn.show();
                    oer.status_message.success(data.message, true);
                }
                $this.removeClass("loading");
            });
        });
    });

    $unsave_btn.click(function(e) {
        e.preventDefault();
        var $this = $(this);
        if ($this.hasClass("loading")) {
            return;
        }
        $this.addClass("loading");
        oer.login.check_login(function() {
            $.post($this.attr("href"), function(data) {
                if (data.status === "success") {
                    $this.hide();
                    $save_btn.show();
                    oer.status_message.success(data.message, true);
                }
                $this.removeClass("loading");
            });
        });
    });
}