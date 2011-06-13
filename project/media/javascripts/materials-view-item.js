oer.materials.view_item = {};

oer.materials.view_item.init = function() {
    oer.materials.view_item.init_navigation();
    var $navigation = $("nav.view-item-navigation");
    if ($navigation.length > 0) {
        $("div.details h1 a").click(function(e) {
            e.preventDefault();
            $navigation.find("form").attr("action", $(this).attr("href")).submit();
        });
    }
};

oer.materials.view_item.init_navigation = function() {
    var $navigation = $("nav.view-item-navigation");
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