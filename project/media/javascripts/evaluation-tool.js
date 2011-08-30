oer.evaluation_tool = {};

oer.evaluation_tool.init_rubrics = function() {

    var $rubrics = $("div.rubrics");
    var evaluate_url = $rubrics.data("evaluate-url");
    var $sections = $rubrics.children("section");
    var $tags_ct = $rubrics.find("div.tags");

    function save_score($scores_ct) {
        var $score = $scores_ct.find("div.selected");
        if (!$score.length) {
            return;
        }

        var score_id = $score.data("score-id");
        if ($scores_ct.data("tag-id") !== undefined) {
            var tag_id = $scores_ct.data("tag-id");
            var $tag_selector = $tags_ct.find("a.tag[data-tag-id='" + tag_id + "']");
            var score_text = null;
            if ($score.is(":last-child")) {
                score_text = "N/A";
            } else {
                score_text = $score.find("a").text();
            }
            $tag_selector.find("span.value").text(score_text);
            $tag_selector.addClass("scored");
            $.post(evaluate_url, {score_id: score_id, tag_id: tag_id});
            var $section = $tag_selector.closest("section");
            if ($section.find("a.tag").not(".scored").length === 0) {
                $section.find("h1").addClass("scored");
            }
        } else if ($scores_ct.data("rubric-id") !== undefined) {
            var rubric_id = $scores_ct.data("rubric-id");
            $.post(evaluate_url, {score_id: score_id, rubric_id: rubric_id});
            $scores_ct.closest("section.rubric").children("h1:first").addClass("scored");
        }
        $scores_ct.data("saved", true);
    }


    function save_unsaved_score() {
        // This saves scores which were selected automatically.

        // Save score for currently selected alignment tag.
        var $current_tag = $tags_ct.children(".selected");
        var current_tag_id = $current_tag.data("tag-id");
        var $current_tag_scores_ct = $tags_ct.find("div.scores[data-tag-id='" + current_tag_id + "']");
        if (!$current_tag_scores_ct.data("saved")) {
            save_score($current_tag_scores_ct);
        }

        // Save score for currently selected rubrics section
        var $current_section_scores_ct = $sections.filter(".rubric.expanded").find("div.scores");
        if ($current_section_scores_ct.length && !$current_section_scores_ct.data("saved")) {
            save_score($current_section_scores_ct);
        }
    }

    function open_section($section) {
        save_unsaved_score();
        $sections.filter(".expanded").removeClass("expanded").find("div.body").show().slideUp("fast");
        if (!$section.hasClass("expanded")) {
            $section.addClass("expanded").find("div.body").hide().slideDown("fast");
        }
    }

    $sections.find("h1 a").click(function(e) {
        e.preventDefault();
        open_section($(this).closest("section"));
    });

    function select_tag($tag) {
        if ($tag.hasClass("selected")) {
            return;
        }

        save_unsaved_score();
        $tags_ct.children(".selected").removeClass("selected");

        var tag_id = $tag.data("tag-id");
        $tags_ct.find("div.tag-description[data-tag-id='" + tag_id + "']").addClass("selected");
        $tags_ct.find("div.scores[data-tag-id='" + tag_id + "']").addClass("selected");
        $tags_ct.find("div.footer[data-tag-id='" + tag_id + "']").addClass("selected");
        $tag.addClass("selected");

        if (window.rocon != undefined) {
            $tags_ct.find("a.tag").each(function(e, el) {
                rocon.update(el);
            });
        }
    }

    $tags_ct.delegate("a.tag", "click", function(e) {
        e.preventDefault();
        select_tag($(this));
    });

    var $score_selectors = $rubrics.find("div.scores");
    $score_selectors.delegate("a,:radio", "click", function(e) {
        var $this = $(this);
        var $score = $this.closest("div");
        if ($score.hasClass("selected")) {
            e.preventDefault();
            return;
        }
        if ($this.is("a")) {
            $score.find(":radio").attr("checked", true);
            e.preventDefault();
        } else {
            e.stopPropagation();
        }
        var $scores_ct = $this.closest("div.scores");
        $scores_ct.find("div.selected").removeClass("selected");
        $score.addClass("selected");

        if (window.rocon != undefined) {
            $scores_ct.find("a").each(function(e, el) {
                rocon.update(el);
            });
        }
        save_score($scores_ct);
    });

    $score_selectors.find("a").mouseenter(function() {
        var $this = $(this);
        $this.closest("div").addClass("hover");
        if (window.rocon != undefined) {
            $this.closest("div.scores").find("a").each(function(e, el) {
                rocon.update(el);
            });
        }
    });

    $score_selectors.find("a").mouseleave(function() {
        var $this = $(this);
        $this.closest("div").removeClass("hover");
        if (window.rocon != undefined) {
            $this.closest("div.scores").find("a").each(function(e, el) {
                rocon.update(el);
            });
        }
    });

    $rubrics.delegate("a.clear", "click", function(e) {
        e.preventDefault();
        var $this = $(this);
        var $section = $this.closest("section");
        var $scores_ct = null;
        var tag_id = null;
        var rubric_id = null;
        if ($section.hasClass("rubric")) {
            $scores_ct = $section.find("div.scores");
            rubric_id = $scores_ct.data("rubric-id");
        } else {
            tag_id = $this.closest("div.footer").data("tag-id");
            $scores_ct = $section.find("div.scores[data-tag-id='" + tag_id + "']");
            var $tag = $section.find("a.tag[data-tag-id='" + tag_id + "']");
            $tag.find("span.value").text("No score");
            $tag.removeClass("scored");
        }
        $scores_ct.find("div.selected").removeClass("selected");
        $scores_ct.find(":radio").attr("checked", false);
        var data = {"delete": "yes"};
        if (tag_id) {
            data["tag_id"] = tag_id;
        } else if (rubric_id) {
            data["rubric_id"] = rubric_id;
        }
        if (window.rocon != undefined) {
            $scores_ct.find("a").each(function(e, el) {
                rocon.update(el);
            });
        }

        $.post(evaluate_url, data);
        $section.children("h1:first").removeClass("scored");
    });

    $rubrics.delegate("a.next", "click", function(e) {
        e.preventDefault();
        open_section($(this).closest("section").next("section"));
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

    $rubrics.find("a.save").click(function(e) {
        var $this = $(this);
        var $section = $this.closest("section");
        var $scores_ct = $section.find("div.scores");
        if (!$scores_ct.data("saved")) {
            save_score($scores_ct);
        }
    });

    var hash = window.location.hash;
    var result = hash.match(/^#(standard|rubric)(\d+)$/);
    if (result !== null) {
        if (result[1] === "standard") {
            open_section($("#alignment"));
            var $tag = $tags_ct.find("a.tag[data-tag-id='" + result[2] + "']");
            select_tag($tag);
        } else if (result[1] === "rubric") {
            var $section = $sections.filter("[data-rubric-id='" + result[2] + "']");
            open_section($section);
        }
    }
};

oer.evaluation_tool.init_evaluate_button = function() {
    var $button = $("#evaluate-btn");
    var $dialog = null;

    $button.click(function(e) {
        e.preventDefault();
        var url = $(this).attr("href");
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
                    title: "Evaluate Resource",
                    width: 600,
                    resizable: false
                });
            } else {
                $dialog.find("iframe").attr("src", url);
                $dialog.dialog("open");
            }
        });
    });
};

oer.evaluation_tool.init_align = function() {
    oer.align_form.init();

    var $document = $(document);
    var $form = $("#align-form");
    var $user_tags = $form.find("ul.align-user-tags");

    $.getJSON($form.attr("action").replace("/add/", "/get-tags/") + "?randNum=" + new Date().getTime(), function(data) {
        $.each(data.tags, function(index, tag) {
            var $tags = $.tmpl("align-user-tags-item", tag).appendTo($user_tags);
            oer.align_form.init_tag_tooltip($tags.find("a:first"));
        });
        $document.trigger(oer.align_form.TAGS_CHANGED_EVENT);
        $form.show();
    });

    var $close_btn = $form.find("div.buttons a.close");
    $close_btn.unbind("click");
    $close_btn.attr("href", $("div.align").data("evaluate-url"));
};
