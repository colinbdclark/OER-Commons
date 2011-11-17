oer.evaluation_tool = {};

oer.evaluation_tool.init_rubrics = function() {

  var $rubrics = $("div.rubrics");
  var evaluate_url = $rubrics.data("evaluate-url");
  var $sections = $rubrics.children("section");
  var $tags_ct = $rubrics.find("div.tags");

  // Comment button
  var $comment_btn = $("a.comment");
  var $comment_form = $("#comment-form");
  var $comment_popup = $("<div/>").qtip({
    content: $comment_form,
    style: {
      classes: "comment-popup ui-tooltip-rounded ui-tooltip-shadow"
    },
    position: {
      my: "top left",
      at: "bottom center",
      target: "event",
      effect: false,
      viewport: $(window)
    },
    show: {
      target: $comment_btn,
      event: "click"
    },
    hide: {
      target: $comment_btn,
      event: "click"
    },
    events: {
      show: function(event) {
        var $target = $(event.originalEvent.target);
        $comment_form.find("textarea").val($target.data("comment"));
        $comment_form.data("target", $target);
      }
    }
  });

  function hide_comment_popup() {
    $comment_popup.qtip("api").hide();
  }

  $comment_form.find("a.clear").click(function(e) {
    e.preventDefault();
    $comment_form.find("textarea").val("");
    $comment_form.data("target").removeClass("checked").data("comment", "");
    hide_comment_popup();
  });

  $comment_form.find("a.save").click(function(e) {
    e.preventDefault();
    var text = $.trim($comment_form.find("textarea").val());
    var $target = $comment_form.data("target");
    $target.data("comment", text);
    if (text === "") {
      $target.removeClass("checked");
    } else {
      $target.addClass("checked");
    }
    hide_comment_popup();
  });

  function save_score($section, callback) {
    var $spinner = $section.find(".footer .spinner");
    $section.ajaxStart(function() {
      $section.unbind("ajaxStart");
      $spinner.addClass("active");
    });
    $section.ajaxStop(function() {
      $section.unbind("ajaxStop");
      $spinner.removeClass("active");
      if (callback) {
        callback();
      }
    });
    var scored = false;
    $.each($section.find("div.scores"), function(i, scores) {
      var $scores = $(scores);
      var $score = $scores.find("div.selected");
      if ($score.length) {
        scored = true;
      } else {
        return;
      }
      var score_id = $score.data("score-id");
      if ($scores.data("tag-id") !== undefined) {
        var tag_id = $scores.data("tag-id");
        $.post(evaluate_url, {
          score_id: score_id, tag_id: tag_id,
          comment: $section.find("div.footer[data-tag-id='" + tag_id + "'] a.comment").data("comment")
        });
      } else if ($scores.data("rubric-id") !== undefined) {
        var rubric_id = $scores.data("rubric-id");
        $.post(evaluate_url, {
          score_id: score_id, rubric_id: rubric_id,
          comment: $section.find("div.footer a.comment").data("comment")
        });
      }
    });
    if (scored) {
      $section.removeClass("not-scored").addClass("scored");
    } else {
      // Remove AJAX events even if not AJAX calls were made.
      $section.unbind("ajaxStart");
      $section.unbind("ajaxStop");
      // Run callback even if nothing is scored, thus not AJAX calls were made.
      if (callback) {
        callback();
      }
      $section.removeClass("scored").addClass("not-scored");
    }
  }

  function clear_score($scores) {
    var $section = $scores.closest("section");

    $scores.find("div.selected").removeClass("selected");
    $scores.find(":radio").attr("checked", false);

    var data = {"delete": "yes"};

    if ($scores.data("tag-id") !== undefined) {
      var tag_id = $scores.data("tag-id");
      data.tag_id = tag_id;
      var $tag = $section.find("a.tag[data-tag-id='" + tag_id + "']");
      $tag.find("span.value").text("No score");
      $tag.removeClass("scored");
    } else if ($scores.data("rubric-id") !== undefined) {
      data.rubric_id = $scores.data("rubric-id");
    }

    rcorners($scores.find("a"));

    $.post(evaluate_url, data);

    var scored = false;
    $.each($section.find("div.scores"), function(i, scores) {
      var $scores = $(scores);
      var $score = $scores.find("div.selected");
      if ($score.length) {
        scored = true;
      }
    });
    if (!scored) {
      $section.removeClass("scored").addClass("not-scored");
    }
  }

  function open_section($section) {
    hide_comment_popup();
    var $current_section = $sections.filter(".expanded");
    if (!$current_section.hasClass("intro") && !$current_section.hasClass("scored")) {
      $current_section.addClass("not-scored");
    }
    $current_section.removeClass("expanded").find("div.body").show().slideUp("fast");
    if (!$section.hasClass("expanded")) {
      $section.addClass("expanded").find("div.body").hide().slideDown("fast");
    }
  }

  $sections.find("h1 a:first").click(function(e) {
    e.preventDefault();
    var $section = $(this).closest("section");
    if (!$section.hasClass("expanded")) {
      open_section($section);
    }
  });

  function select_tag($tag) {
    if ($tag.hasClass("selected")) {
      return;
    }

    hide_comment_popup();

    $tags_ct.children(".selected").removeClass("selected");
    var tag_id = $tag.data("tag-id");
    $tags_ct.find("div.tag-description[data-tag-id='" + tag_id + "']").addClass("selected");
    $tags_ct.find("div.scores[data-tag-id='" + tag_id + "']").addClass("selected");
    $tags_ct.find("div.footer[data-tag-id='" + tag_id + "']").addClass("selected");
    $tag.addClass("selected");

    rcorners($tags_ct.find("a.tag"));
  }

  $tags_ct.delegate("a.tag", "click", function(e) {
    e.preventDefault();
    select_tag($(this));
  });

  var $score_selectors = $rubrics.find("div.scores");
  $score_selectors.delegate("a,:radio", "click", function(e) {
    var $this = $(this);
    var $score = $this.closest("div");
    var $scores = $this.closest("div.scores");

    if ($score.hasClass("selected")) {
      if ($this.is("a")) {
        $score.find(":radio").attr("checked", false);
        e.preventDefault();
      } else {
        $this.attr("checked", false);
        e.stopPropagation();
      }
      clear_score($scores);
      return;
    }

    if ($this.is("a")) {
      $score.find(":radio").attr("checked", true);
      e.preventDefault();
    } else {
      e.stopPropagation();
    }

    $scores.find("div.selected").removeClass("selected");
    $score.addClass("selected");

    rcorners($scores.find("a"));

    if ($scores.data("tag-id") !== undefined) {
      var tag_id = $scores.data("tag-id");
      var $tag_selector = $tags_ct.find("a.tag[data-tag-id='" + tag_id + "']");
      var score_text = null;
      if ($score.is(":last-child")) {
        score_text = "N/A";
      } else {
        score_text = $score.find("a").text();
      }
      $tag_selector.find("span.value").text(score_text);
      $tag_selector.addClass("scored");
    }

  });

  $score_selectors.find("a").mouseenter(function() {
    var $this = $(this);
    $this.closest("div").addClass("hover");
    rcorners($this.closest("div.scores").find("a"));
  });

  $score_selectors.find("a").mouseleave(function() {
    var $this = $(this);
    $this.closest("div").removeClass("hover");
    rcorners($this.closest("div.scores").find("a"));
  });

  $rubrics.delegate("a.clear", "click", function(e) {
    e.preventDefault();
    var $this = $(this);
    var $section = $this.closest("section");
    var $scores = null;
    if ($section.hasClass("rubric")) {
      $scores = $section.find("div.scores");
    } else {
      var tag_id = $this.closest("div.footer").data("tag-id");
      $scores = $section.find("div.scores[data-tag-id='" + tag_id + "']");
    }
    clear_score($scores);
  });

  $rubrics.delegate("a.next", "click", function(e) {
    e.preventDefault();
    var $section = $(this).closest("section");
    if (!$section.hasClass("intro")) {
      save_score($section);
    }
    open_section($section.next("section"));
  });

  $rubrics.delegate("a.next-tag", "click", function(e) {
    e.preventDefault();
    var $this = $(this);
    var tag_id = $this.closest("div.footer").data("tag-id");
    var $tag = $tags_ct.find("a.tag[data-tag-id='" + tag_id + "']").next("a.tag");
    select_tag($tag);
  });

  $rubrics.delegate("a.prev-tag", "click", function(e) {
    e.preventDefault();
    var $this = $(this);
    var tag_id = $this.closest("div.footer").data("tag-id");
    var $tag = $tags_ct.find("a.tag[data-tag-id='" + tag_id + "']").prev("a.tag");
    select_tag($tag);
  });

  $rubrics.find("a.save,a.add-standard").click(function(e) {
    e.preventDefault();
    var $this = $(this);
    var $section = $this.closest("section");
    save_score($section, function() {
      window.location.href = $this.attr("href");
    });
  });

  var hash = window.location.hash;
  var result = hash.match(/^#(standard|rubric)(\d+)?$/);
  if (result !== null) {
    if (result[1] === "standard") {
      open_section($("#alignment"));
      var $tag = null;
      if (result[2]) {
        $tag = $tags_ct.find("a.tag[data-tag-id='" + result[2] + "']");
      } else if ($tags_ct.find("a.tag").length) {
        $tag = $tags_ct.find("a.tag").first();
      }
      if ($tag) {
        select_tag($tag);
      }
    } else if (result[1] === "rubric") {
      var $section = $sections.filter("[data-rubric-id='" + result[2] + "']");
      open_section($section);
    }
  }

};

oer.evaluation_tool.open_tool = function(url) {

  // Allow to drag the dialog out of the viewport.
  if (!$.ui.dialog.prototype._makeDraggableBase) {
    $.ui.dialog.prototype._makeDraggableBase = $.ui.dialog.prototype._makeDraggable;
    $.ui.dialog.prototype._makeDraggable = function() {
      this._makeDraggableBase();
      this.uiDialog.draggable("option", "containment", false);
    };
  }

  var $dialog = null;
  oer.login.check_login(function() {
    if ($dialog === null) {
      $dialog = $("<div id='evaluate-dialog'></div>");
      $("<iframe />", {
        src: url,
        width: 600,
        height: 700,
        frameBorder: 0,
        scrolling: "no"
      }).appendTo($dialog);
      $dialog.appendTo($("body"));
      $dialog.dialog({
        title: "<span>Achieve</span> OER Evaluation Tool",
        width: 600,
        resizable: false,
        dialogClass: "evaluate-dialog expanded",
        position: [$("body").innerWidth() - 620, 50]
      });

      var $minimize = $('<a>', {href: "#"}).text("Minimize").addClass("minimize");
      $minimize.click(function(e) {
        e.preventDefault();
        $dialog.dialog("widget").toggleClass("expanded collapsed");
      });
      $minimize.insertBefore($dialog.dialog("widget").find(".ui-dialog-titlebar .ui-dialog-titlebar-close"));

    } else {
      $dialog.find("iframe").attr("src", url);
      $dialog.dialog("open");
    }
  });
};

oer.evaluation_tool.init_evaluate_button = function() {
  var $button = $("#evaluate-btn");
  $button.click(function(e) {
    e.preventDefault();
    oer.evaluation_tool.open_tool($(this).attr("href"));
  });
};

oer.evaluation_tool.init_align = function() {
  oer.align_form.init();

  var $document = $(document);
  var $form = $("#align-form");
  var $tags = $form.find("ul.align-tags");

  $.getJSON($form.attr("action").replace("/add/", "/get-tags/") + "?randNum=" + new Date().getTime(), function(data) {
    $.each(data.tags, function(index, tag) {
      var template = "id" in tag ? "align-user-tag" : "align-tag";
      var $tag = $.tmpl(template, tag).appendTo($tags);
      rcorners($tag);
      oer.align_form.init_tag_tooltip($tag.find("a:first"));
    });
    $document.trigger(oer.align_form.TAGS_CHANGED_EVENT);
    $form.show();
  });

  var $close_btn = $form.find("div.buttons a.close");
  $close_btn.unbind("click");
  $close_btn.attr("href", $("div.align").data("evaluate-url"));
};

oer.evaluation_tool.init_results = function() {
  $("span.comment").qtip({
    content: {
      text: function() {
        return $(this).data("comment");
      }
    },
    style: {
      classes: "comment-popup ui-tooltip-rounded ui-tooltip-shadow"
    },
    position: {
      my: "top center",
      at: "bottom center",
      effect: false
    }});
  $("a.finalize").click(function(e) {
    e.preventDefault();
    $("#finalize-form").submit();
  });
};
