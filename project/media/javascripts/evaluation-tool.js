oer.evaluation_tool = {};

oer.evaluation_tool.init_rubrics = function() {

    var $rubrics = $("div.rubrics");
    var evaluate_url = $rubrics.data("evaluate-url");
    var $sections = $rubrics.children("section");

    function open_section($section) {
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
        var tag_id = $tag.data("tag-id");
        $tags_ct.children(".selected").removeClass("selected");
        $tags_ct.find("div.tag-description[data-tag-id='" + tag_id + "']").addClass("selected");
        $tags_ct.find("div.scores[data-tag-id='" + tag_id + "']").addClass("selected");
        $tags_ct.find("div.footer[data-tag-id='" + tag_id + "']").addClass("selected");
        $tag.addClass("selected");
    }

    var $tags_ct = $rubrics.find("div.tags");
    $tags_ct.delegate("a.tag", "click", function(e) {
        e.preventDefault();
        select_tag($(this));
    });

    var $score_selectors = $rubrics.find("div.scores");
    $score_selectors.delegate("a", "click", function(e) {
        e.preventDefault();
        var $this = $(this);
        var $score = $this.closest("div");
        if ($score.hasClass("selected")) {
            return;
        }
        var $scores_ct = $this.closest("div.scores");
        $scores_ct.find("div.selected").removeClass("selected");
        $score.addClass("selected");

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
        } else {
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
        var data = {delete: "yes"};
        if (tag_id) {
            data["tag_id"] = tag_id;
        } else if (rubric_id) {
            data["rubric_id"] = rubric_id;
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
                    height: 650
                }).appendTo($dialog);
                $dialog.appendTo($("body"));
                $dialog.dialog({
                    title: "Evaluate to Rubrics",
                    width: 600
                });
            } else {
                $dialog.find("iframe").attr("src", url);
                $dialog.dialog("open");
            }
        });
    });
};
