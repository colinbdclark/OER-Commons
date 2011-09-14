oer.materials.view_item = {};

oer.materials.view_item.init = function() {
    oer.materials.view_item.init_navigation();
};

oer.materials.view_item.init_navigation = function() {
    var $navigation = $("nav.view-item-navigation");
    if ($navigation.length) {
        var $form = $navigation.find("form");
        $navigation.find("a.item-link").click(function() {
            $.cookie("_i", $form.serialize(), {path: "/"});
        });
        $("div.details h1 a").click(function() {
            $.cookie("_i", $form.serialize(), {path: "/"});
        });
        $("#goto").click(function() {
            $.cookie("_i", $form.serialize(), {path: "/"});
        });
    }
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
