oer.tags_form = {};

$.template("user-tags-item", '<li data-id="${id}" class="tag rc3"><a href="${url}">${name}</a> <a href="#" class="delete">Delete</a></li>');

oer.tags_form.init = function() {
    var $form = $("#add-tags-form");
    var $input = $form.find("#id_tags");
    var $user_tags = $("ul.user-tags");

    $input.autocomplete({
    minLength : 2,
    source : "/autocomplete/tags/tag/name",
    select : function(event, ui) {
        $form.submit();
    }
    });

    $form.submit(function(e) {
        $input.autocomplete("close");
        e.preventDefault();
        var value = $.trim($input.val());
        if (value === "") {
            return;
        }
        var $existing_tag = $user_tags.find("a:contains(" + value + ")").closest("li");
        if ($existing_tag.length) {
            $existing_tag.effect("pulsate", 200);
            return;
        }
        $input.addClass("loading");
        $.post($form.attr("action"), {
            "tags" : value
        }, function(response, status, request) {
            $input.removeClass("loading");
            $.each(response.tags, function(i, tag) {
                var $tag = $.tmpl("user-tags-item", tag).appendTo($user_tags);
                if (window.rocon != undefined) {
                  rocon.update($tag.get(0));
                }
            });
            $input.val("");
        });
    });

    $user_tags.delegate("a.delete", "click", function(e) {
        e.preventDefault();
        $this = $(this);
        $li = $this.closest("li");
        $li.fadeOut(250, function() {
            $(this).detach();
        });
        var tag_id = $li.data("id");
        $.post("/tags/delete", {
            id : tag_id
        }, function(response, status, request) {
        });
    });
};

oer.tags_portlet = {};

oer.tags_portlet.init = function() {
    var $body = $("body");
    if ($body.hasClass("authenticated")) {
        return;
    }
    var $portlet = $("section.portlet.item-tags");
    $portlet.find(".login a").click(function(e) {
        e.preventDefault();
        oer.login.show_popup();
    });

    var $document = $(document);
    $document.bind(oer.login.LOGGED_IN_EVENT, function(e) {
      var $user_tags = $("ul.user-tags");
      $user_tags.empty().hide();
      var $form = $("#add-tags-form");
      $.getJSON($form.attr("action").replace("/tags/add/", "/tags/get-tags/"), function(data, status) {
          var user_tags = data.user_tags;
          var $item_tags = $portlet.find("ul:first li.tag");
          $.each(user_tags, function(index, tag) {
              $item_tags.filter(":contains(" + tag.name + ")").fadeOut(300);
              var $tag = $.tmpl("user-tags-item", tag).appendTo($user_tags);
            if (window.rocon != undefined) {
              rocon.update($tag.get(0));
            }
          });
          $user_tags.fadeIn(300);
      });
    });
};