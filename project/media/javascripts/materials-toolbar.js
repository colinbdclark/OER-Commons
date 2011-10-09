oer.materials.toolbar = {};

oer.materials.toolbar.init = function() {
  oer.materials.toolbar.resize_iframe();

  $(window).resize(function() {
    oer.materials.toolbar.resize_iframe();
  });

  oer.materials.toolbar.init_tags();
  oer.materials.toolbar.init_save();
  oer.materials.toolbar.init_review();
  oer.materials.view_item.init_navigation();
  oer.evaluation_tool.init_evaluate_button();
  var $evaluate_btn = $("#evaluate-btn");
  var result = window.location.hash.match(/^#evaluate(?::(?:(standard|rubric\d+)))?$/);
  if (result) {
    if (result[1]) {
       oer.evaluation_tool.open_tool($evaluate_btn.data("evaluate-url") + "#" + result[1]);
    } else {
      oer.evaluation_tool.open_tool($evaluate_btn.attr("href"));
    }
  }
};

oer.materials.toolbar.resize_iframe = function() {
  var $window = $(window);
  var $iframe = $("#resource");
  var $toolbar = $("#toolbar");
  $iframe.height($window.height() - $toolbar.outerHeight());
};

oer.materials.toolbar.init_tags = function() {
  var $toolbar = $("#toolbar");

  var $dialog = $("#add-tags-dialog").dialog({
    modal: false,
    width: 400,
    autoOpen: false,
    resizable: false,
    position: [$toolbar.width() - 400 - 30, $toolbar.height() + 10]
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
      $.getJSON($form.attr("action").replace("/tags/add/", "/tags/get-tags/") + "?randNum=" + new Date().getTime(), function(data) {
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
};

oer.materials.toolbar.init_review = function() {
  var $toolbar = $("#toolbar");

  var $dialog = $("#review-dialog").dialog({
    modal: false,
    width: 583,
    autoOpen: false,
    resizable: false,
    title: "Add review",
    position: [$toolbar.width() - 583 - 30, $toolbar.height() + 10]
  });

  var $review_btn = $toolbar.find("a.review");

  $review_btn.click(function(e) {
    e.preventDefault();
    oer.login.check_login(function() {
      $dialog.dialog("open");
    });
  });

  var $form = $("#review-form");

  var $submit_btn = $form.find("input[type='submit']").button();

  $form.submit(function(e) {
    e.preventDefault();
    $dialog.dialog("widget").addClass("loading");
    $submit_btn.button("option", "disabled", true);
    $.post($form.attr("action"), $form.serialize(), function(data) {
      $dialog.dialog("widget").removeClass("loading");
      $submit_btn.button("option", "disabled", false);
      if (data.status === "success") {
        oer.status_message.success(data.message, true);
        $dialog.dialog("close");
      }
    });
  });

};
