oer.materials.index = {};

oer.materials.index.init_action_panel = function() {
    var $filters_portlet = $("div.portlet.index-filters");
    var $form = $filters_portlet.find("form[name='index-filters']");
    var $action_panel = $("div.action-panel");

    $action_panel.find("select[name='batch_size']").change(function() {
        $this = $(this);
        $form.find("input[name='batch_size']").val($this.val());
        $form.submit();
    });

    $action_panel.find("select[name='sort_by']").change(function() {
        $this = $(this);
        $form.find("input[name='sort_by']").val($this.val());
        $form.submit();
    });

};

oer.materials.index.init_filters = function() {
    var $filters_portlet = $("div.portlet.index-filters");
    var $form = $filters_portlet.find("form[name='index-filters']");

    $form.find("div.search input[type='submit']").click(function() {
        if ($form.find("input[name='f.search']").val() !== "") {
            $form.find("input[name='sort_by']").val("search");
        }
    });

    $form.submit(function() {
        $form.find("dl.filter").each(function() {
            $filter = $(this);
            if ($filter.find("dd :checkbox").length == $filter.find("dd :checkbox[checked=true]").length) {
                $filter.find(":checkbox").attr("disabled", true);
            }
        });
        if ($form.find("input[name='f.search']").val() === "") {
            $form.find("input[name='f.search']").attr("disabled", true);
        }
    });

    $form.delegate("dl.filter dd :checkbox", "click", function(e) {
        $checkbox = $(this);
        $filter = $checkbox.parents("dl.filter").first();
        if ($checkbox.attr("checked")) {
            if ($filter.find("dd :checkbox").length == $filter.find("dd :checkbox[checked=true]").length) {
                $filter.find("dt :checkbox").attr("checked", true);
            }
        } else {
            $filter.find("dt :checkbox").attr("checked", false);
        }
    });

    $form.delegate("dl.filter dt :checkbox", "click", function(e) {
        $checkbox = $(this);
        $filter = $checkbox.parents("dl.filter").first();
        $filter.find(".collapsed").removeClass("collapsed").addClass("expanded");
        if ($checkbox.attr("checked")) {
            $filter.find("dd :checkbox").attr("checked", true);
        } else {
            $filter.find("dd :checkbox").attr("checked", false);
        }
    });

};

oer.materials.index.init_top_keywords = function() {
    var $top_keywords_portlet = $("div.portlet.top-keywords");
    $top_keywords_portlet.find("a.see-more").click(function(e) {
        e.preventDefault();
        $(this).hide();
        $top_keywords_portlet.find("div.top").hide();
        $top_keywords_portlet.find("div.all").fadeIn(300);
    });
};

oer.materials.index.init_item_links = function() {
    var $filters_portlet = $("div.portlet.index-filters");
    var $form = $filters_portlet.find("form[name='index-filters']");
    $("#content div.materials-index").delegate("h3 a.item-link", "click", function(e) {
        e.preventDefault();
        $form.attr("action", $(this).attr("href")).attr("method", "post");
        $form.find("input[name='index_path']").attr("disabled", false);
        $form.submit();
    });
};

oer.materials.index.init_actions_menus = function() {
    var $materials_index = $("#content div.materials-index");
    $materials_index.delegate("dl.actions dt a", "click", function(e) {
        e.preventDefault();
        e.stopPropagation();
        var $menu = $(this).closest("dl.actions");
        $materials_index.find("dl.actions").not($menu).removeClass("active");
        if ($menu.hasClass("active")) {
            $menu.removeClass("active");
        } else {
            $menu.addClass("active");
        }
    });

    $(document).click(function(e) {
        $materials_index.find("dl.actions").removeClass("active");
    });

    $materials_index.delegate("dl.actions a.save-item", "click", function(e) {
        e.preventDefault();
        var $this = $(this);
        $.post($this.attr("href"), function(data) {
            var $details = $this.closest("div.item").find("div.details");
            $details.find("div.message").remove();
            $("<div></div>").addClass("message").text(data).hide().appendTo($details).fadeIn(300).delay(3000).fadeOut(1000, function() {
                $(this).remove();
            });
        }, "application/json");
        var $menu = $this.closest("dl.actions");
        $menu.removeClass("active");
    });

    var $rate_form = $("form[name='rate']");
    $rate_form.find("a.rate").click(function(e) {
        e.preventDefault();
        var $this = $(this);
        if ($rate_form.attr("method") == "post") {
            $.post($rate_form.attr("action"), {
                rating : $rate_form.find("select").val()
            }, function(data) {
                data = $.parseJSON(data);
                var $stars = $this.closest("div.right").find("div.stars");
                $stars.removeClass().addClass("stars").addClass(data.stars_class);
                var $details = $this.closest("div.item").find("div.details");
                $details.find("div.message").remove();
                $("<div></div>").addClass("message").text(data.message).hide().appendTo($details).fadeIn(300).delay(3000).fadeOut(1000, function() {
                    $(this).remove();
                });
                $rate_form.hide();
            }, "application/json");
        } else {
            $rate_form.submit();
        }
    });

    $rate_form.find("a.cancel").click(function(e) {
        e.preventDefault();
        $rate_form.hide();
    });

    $materials_index.delegate("dl.actions a.rate-item", "click", function(e) {
        e.preventDefault();
        var $this = $(this);
        var $menu = $this.closest("dl.actions");
        $rate_form.find("select").val("5");
        $rate_form.attr("action", $this.attr("href"));
        $rate_form.detach().insertAfter($menu).fadeIn(300);
        $menu.removeClass("active");
    });

};

oer.materials.index.init_tags_form = function() {
    var $dialog = $("#add-tags-dialog").dialog({
    modal : true,
    width : 400,
    autoOpen : false,
    resizable : false
    });

    var $form = $("#add-tags-form");
    var $input = $form.find("#id_tags");
    var $user_tags = $dialog.find("ul.user-tags");

    var $materials_index = $("#content div.materials-index");
    $materials_index.delegate("dl.actions a.tag-item", "click", function(e) {
        e.preventDefault();
        var $this = $(this);
        var $menu = $this.closest("dl.actions");
        $menu.removeClass("active");
        if ($form.hasClass("can-add")) {
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
        }
        $dialog.dialog("option", "title", "Add tags to " + $this.closest("div.item").find("h3 a").first().text());
        $dialog.dialog("open");
    });

    oer.tags_form.init();
};

oer.materials.index.init = function() {

    oer.materials.index.init_action_panel();
    oer.materials.index.init_top_keywords();
    oer.materials.index.init_filters();
    oer.materials.index.init_item_links();
    oer.materials.index.init_actions_menus();
    oer.materials.index.init_tags_form();

    var $filters_portlet = $("div.portlet.index-filters");

    oer.collapsibles.init($("#content"));
    oer.collapsibles.init($filters_portlet);

    $filters_portlet.find("dl.cou a.tooltip-button").cluetip({
    local : true,
    arrows : true,
    width : 300
    });
    $filters_portlet.find("dl.grade-levels a.tooltip-button").cluetip({
    local : true,
    arrows : true,
    width : 200
    });

};
