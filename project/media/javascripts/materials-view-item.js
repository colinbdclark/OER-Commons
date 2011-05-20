oer.materials.view_item = {};

oer.materials.view_item.init = function() {
    oer.materials.view_item.init_navigation();
    var $navigation = $("div.view-item-navigation");
    if ($navigation.length > 0) {
        $("div.details h3 a").click(function(e) {
            e.preventDefault();
            $navigation.find("form").attr("action", $(this).attr("href")).submit();
        });
    }
    oer.materials.view_item.init_align_form();
};

oer.materials.view_item.init_navigation = function() {
    var $navigation = $("div.view-item-navigation");
    $navigation.find("a.item-link").click(function(e) {
        e.preventDefault();
        $navigation.find("form").attr("action", $(this).attr("href")).submit();
    });
}

oer.materials.view_item.init_content_actions = function() {
    var $content_actions = $("#content div.content-actions");
    $content_actions.delegate("dl dt a", "click", function(e) {
        e.preventDefault();
        e.stopPropagation();
        var $menu = $(this).closest("dl");
        $content_actions.find("dl").not($menu).removeClass("active");
        if ($menu.hasClass("active")) {
            $menu.removeClass("active");
        } else {
            $menu.addClass("active");
        }
    });

    $(document).click(function(event) {
        $content_actions.find("dl").removeClass("active");
    });
};

oer.materials.view_item.init_align_form = function() {
    var $dialog = $("#align-dialog").dialog({
    modal : true,
    width : "auto",
    height : "auto",
    autoOpen : false,
    resizable : false
    });

    var $document = $(document);
    $document.bind(oer.align_form.LOADING_EVENT, function(e) {
        $dialog.dialog("widget").addClass("loading");
    });
    $document.bind(oer.align_form.LOADED_EVENT, function(e) {
        $dialog.dialog("widget").removeClass("loading");
    });

    var $form = $("#align-form");
    var $user_tags = $("#align-user-tags");
    
    var $show_form_btn = $("#show-align-form");
    
    $show_form_btn.click(function(e) {
        e.preventDefault();
        var $this = $(this);
        var $item = $("#content div.item");
        
        oer.login.check_login(function() {
            $form.hide();
            $form.attr("action", $this.attr("href"));
            var initialized = !!$form.find("#id_curriculum_standard option").length;
            if (initialized) {
                oer.align_form.reset();
            } else {
                oer.align_form.init();
            }
            $user_tags.empty();
            $.getJSON($form.attr("action").replace("/add/", "/get-tags/"), function(data, status) {
                $.each(data.tags, function(index, tag) {
                    $.tmpl("align-user-tags-item", tag).appendTo($user_tags);
                });
                $form.show();
            });
            $dialog.dialog("option", "title", "Align " + $item.find("h3 a").first().text());
            $dialog.dialog("open");
        });
    });
};
