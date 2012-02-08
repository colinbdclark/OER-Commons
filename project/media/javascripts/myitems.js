oer.myitems = {};

oer.myitems.init = function() {
    var $form = $("#folder-create-form");
    var $button = $("#folder-create-button");
    var $submit = $("#folder-create-submit");

    $button.click(function(e) {
        $form.show();
        $submit.show();
        $button.hide();
        e.preventDefault();
    });
    $submit.click(function(e) {
        $.post($form.attr("action"), $form.serialize(), function(response) {});
        $form.hide();
        $submit.hide();
        $button.show();
        e.preventDefault();
    });
};

oer.myitems.index = {};

oer.myitems.index.init_action_panel = function() {
    var $form = $("div.action-panel form");
    $form.find("select[name='batch_size']").change(function() {
        $form.submit();
    });
    $form.find("select[name='sort_by']").change(function() {
        $form.submit();
    });
};

oer.myitems.index.init = function() {

    oer.myitems.index.init_action_panel();
    oer.materials.index.init_actions_menus();

    oer.collapsibles.init($("#content"));

};

oer.myitems.index.init_saved_items = function() {
    var $confirmation = $("div.unsave-confirmation");

    $confirmation.find("a.cancel").click(function(e) {
        e.preventDefault();
        $confirmation.hide();
    });

    $confirmation.find("a.unsave").click(function(e) {
        e.preventDefault();
        var $item = $confirmation.closest("article.item");
        $confirmation.hide().detach();
        var url = $item.find("a.unsave-item").attr("href");
        $.post(url,
            function() {
                $item.fadeOut(500);
            });
    });

    $("#content").delegate("a.unsave-item", "click", function(e) {
        e.preventDefault();
        var $this = $(this);
        var $details = $this.closest("article.item").find("div.details");
        $confirmation.detach().appendTo($details).fadeIn(300);
    });
};

