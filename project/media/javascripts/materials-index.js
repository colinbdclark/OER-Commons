oer.materials.index = {};

oer.materials.index.init_action_panel = function() {
    var $filters_portlet = $("section.portlet.index-filters");
    var $form = $filters_portlet.find("form[name='index-filters']");
    var $action_panel = $("div.action-panel");

    $action_panel.find("select[name='batch_size']").change(function() {
        var $this = $(this);
        $form.find("input[name='batch_size']").val($this.val());
        $form.submit();
    });

    $action_panel.find("select[name='sort_by']").change(function() {
        var $this = $(this);
        $form.find("input[name='sort_by']").val($this.val());
        $form.submit();
    });

};

oer.materials.index.disable_unecessary_filters = function($form) {
    var disabled_filters = [];
    $form.find("dl.filter").each(function() {
        var $filter = $(this);
        if ($filter.find("dd :checkbox").length == $filter.find("dd :checkbox[checked=true]").length) {
            var $checkbox = $filter.find(":checkbox");
            $checkbox.attr("disabled", "disabled");
            disabled_filters.push($checkbox);
        }
    });
    var $search_filter = $form.find("input[name='f.search']");
    if ($search_filter.val() === "") {
        $search_filter.attr("disabled", "disabled");
        disabled_filters.push($search_filter);
    }

    return disabled_filters;
};

oer.materials.index.init_filters = function() {
    var $filters_portlet = $("section.portlet.index-filters");
    var $form = $filters_portlet.find("form[name='index-filters']");

    $form.find("div.search input[type='submit']").click(function() {
        if ($form.find("input[name='f.search']").val() !== "") {
            $form.find("input[name='sort_by']").val("search");
        }
    });

    $form.submit(function() {
        oer.materials.index.disable_unecessary_filters($form);
    });

    $form.delegate("dl.filter dd :checkbox", "click", function() {
        var $checkbox = $(this);
        var $filter = $checkbox.parents("dl.filter").first();
        if ($checkbox.attr("checked")) {
            if ($filter.find("dd :checkbox").length == $filter.find("dd :checkbox[checked=true]").length) {
                $filter.find("dt :checkbox").attr("checked", true);
            }
        } else {
            $filter.find("dt :checkbox").attr("checked", false);
        }
    });

    $form.delegate("dl.filter dt :checkbox", "click", function(e) {
        var $checkbox = $(this);
        var $filter = $checkbox.parents("dl.filter").first();
        $filter.find(".collapsed").removeClass("collapsed").addClass("expanded");
        if ($checkbox.attr("checked")) {
            $filter.find("dd :checkbox").attr("checked", true);
        } else {
            $filter.find("dd :checkbox").attr("checked", false);
        }
    });

};

oer.materials.index.init_top_keywords = function() {
    var $top_keywords_portlet = $("section.portlet.top-keywords");
    $top_keywords_portlet.find("a.see-more").click(function(e) {
        e.preventDefault();
        $(this).hide();
        $top_keywords_portlet.find("div.top").hide();
        $top_keywords_portlet.find("div.all").fadeIn(300);
    });
};

oer.materials.index.init_item_links = function() {
    var $filters_portlet = $("section.portlet.index-filters");
    var $form = $filters_portlet.find("form[name='index-filters']");
    $("#content div.materials-index").delegate("h1 a", "click", function() {
        oer.materials.index.disable_unecessary_filters($form);
        $form.find("input[name='index_path']").attr("disabled", false);
        $.cookie("_i", $form.serialize(), {path: "/"});
    });
};

oer.materials.index.item_message = function($item, message) {
    var $details = $item.find("div.details");
    $details.find("div.message").remove();
    $("<div></div>").addClass("message").text(message).hide().appendTo($details).fadeIn(300).delay(3000).fadeOut(1000, function() {
        $(this).remove();
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

    $(document).click(function() {
        $materials_index.find("dl.actions").removeClass("active");
    });

    $materials_index.delegate("dl.actions a.save-item", "click", function(e) {
        e.preventDefault();
        var $this = $(this);
        oer.login.check_login(function() {
            $.post($this.attr("href"), function(data) {
                oer.materials.index.item_message($this.closest("article.item"), data.message);
            });
        });
        var $menu = $this.closest("dl.actions");
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
        oer.login.check_login(function() {
            $form.hide();
            $user_tags.empty();
            $form.attr("action", $this.attr("href"));
            $input.val("");
            $.getJSON($form.attr("action").replace("/tags/add/", "/tags/get-tags/") + "?randNum=" + new Date().getTime(), function(data) {
                var user_tags = data.user_tags;
                $.each(user_tags, function(index, tag) {
                    $.tmpl("user-tags-item", tag).appendTo($user_tags);
                });
                $form.show();
            });
            $dialog.dialog("option", "title", "Add tags to " + $this.closest("article.item").find("h1 a").first().text());
            $dialog.dialog("open");
        });
    });
    oer.tags_form.init();
};

oer.materials.index.init_align_form = function() {
    var $dialog = $("#align-dialog").dialog({
    modal : true,
    width : "650",
    height : "auto",
    autoOpen : false,
    resizable : false
    });

    var $document = $(document);
    $document.bind(oer.align_form.LOADING_EVENT, function() {
        $dialog.dialog("widget").addClass("loading");
    });
    $document.bind(oer.align_form.LOADED_EVENT, function() {
        $dialog.dialog("widget").removeClass("loading");
    });

    var $form = $("#align-form");
    var $user_tags = $("ul.align-user-tags");

    oer.align_form.init_user_tags($user_tags, $form);

    var $materials_index = $("#content div.materials-index");
    $materials_index.delegate("dl.actions a.align-item", "click", function(e) {
        e.preventDefault();
        var $this = $(this);
        var $menu = $this.closest("dl.actions");
        $menu.removeClass("active");
        var $item = $this.closest("article.item");

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
            $.getJSON($form.attr("action").replace("/add/", "/get-tags/") + "?randNum=" + new Date().getTime(), function(data) {
                $.each(data.tags, function(index, tag) {
                    var $tags = $.tmpl("align-user-tags-item", tag).appendTo($user_tags);
                    oer.align_form.init_tag_tooltip($tags.find("a:first"));
                });
                $document.trigger(oer.align_form.TAGS_CHANGED_EVENT);
                $form.show();
            });
            $dialog.dialog("option", "title", "Align " + $item.find("h1 a").first().text());
            $dialog.dialog("open");
        });
    });
};

oer.materials.index.init = function() {

    oer.materials.index.init_action_panel();
    oer.materials.index.init_top_keywords();
    oer.materials.index.init_filters();
    oer.materials.index.init_item_links();
    oer.materials.index.init_actions_menus();
    oer.materials.index.init_tags_form();
    oer.materials.index.init_align_form();

    var $filters_portlet = $("section.portlet.index-filters");

    oer.collapsibles.init($("#content"));
    oer.collapsibles.init($filters_portlet);

    $("dl.cou a.tooltip-button").qtip(RIGHTSIDE_TOOLTIP_OPTIONS);
    $("dl.grade-levels a.tooltip-button").qtip(RIGHTSIDE_TOOLTIP_OPTIONS);

    $("section.portlet.cou li a").qtip(DEFAULT_TOOLTIP_OPTIONS);
    $("#content div.cou-bucket").qtip(RIGHTSIDE_TOOLTIP_OPTIONS);

};
