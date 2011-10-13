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

oer.materials.index.pjax = function(url) {
  var selector = "#content div.materials-index";
  var $materials_index = $(selector);
  $materials_index.fadeOut("fast", function() {
    $materials_index.empty();
    $materials_index.addClass("loading").show();
    $.pjax({
      container: selector,
      url: url,
      timeout: 5000
    });
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

  $form.submit(function(e) {
    var disabled_filters = oer.materials.index.disable_unecessary_filters($form);
    if ($.support.pjax) {
      e.preventDefault();
      var url = $form.attr("action") + "?" + $form.serialize();
      $.each(disabled_filters, function(i, f) {
        $(f).removeAttr("disabled");
      });
      oer.materials.index.pjax(url);
    }
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
    if ($.support.pjax) {
      $form.submit();
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
    if ($.support.pjax) {
      $form.submit();
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
    modal: true,
    width: 400,
    autoOpen: false,
    resizable: false
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
    modal: true,
    width: "650",
    height: "auto",
    autoOpen: false,
    resizable: false
  });

  var $document = $(document);
  $document.bind(oer.align_form.LOADING_EVENT, function() {
    $dialog.dialog("widget").addClass("loading");
  });
  $document.bind(oer.align_form.LOADED_EVENT, function() {
    $dialog.dialog("widget").removeClass("loading");
  });

  var $form = $("#align-form");
  var $tags = $("ul.align-tags");

  oer.align_form.init_user_tags($tags, $form);

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
      $tags.empty();
      $.getJSON($form.attr("action").replace("/add/", "/get-tags/") + "?randNum=" + new Date().getTime(), function(data) {
        $.each(data.tags, function(index, tag) {
          var $tag = $.tmpl("align-tag", tag).appendTo($tags);
          oer.align_form.init_tag_tooltip($tag.find("a:first"));
        });
        $.each(data.user_tags, function(index, tag) {
          var $tag = $.tmpl("align-user-tag", tag).appendTo($tags);
          oer.align_form.init_tag_tooltip($tag.find("a:first"));
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

  if ($.support.pjax) {

    $.pjax.renderResponse = function($container, data) {
      var $action_panel = $("div.action-panel");
      var $first_item_number = $action_panel.find("span.first-item-number");
      var $last_item_number = $action_panel.find("span.last-item-number");
      var $total_items = $action_panel.find("strong.total-items");
      var $title = $("title");
      var base_window_title = $.trim($title.text().split("|").pop());
      var $page_title = $("h1.page-title");
      data = $.parseJSON(data);
      $container.hide().removeClass("loading");
      $container.html(data.items);
      oer.rating.init();
      $first_item_number.text(data.first_item_number);
      $last_item_number.text(data.last_item_number);
      $total_items.text(data.total_items);
      var title = null;
      var page_title = null;
      if (data.page_subtitle !== "") {
        title = data.page_title + " : " + data.page_subtitle + " | " + base_window_title;
        page_title = data.page_title + ": <span>" + data.page_subtitle + "</span>";
      } else {
        title = data.page_title + " : " + base_window_title;
        page_title = data.page_title;
      }
      $title.text(title);
      $page_title.html(page_title);
      $container.fadeIn("fast");
    };

    var $materials_index = $("#content div.materials-index");
    $materials_index.delegate("ul.pagination a", "click", function(e) {
      e.preventDefault();
      var url = $(this).attr("href");
      oer.materials.index.pjax(url);
    });
  }
};
