oer.materials.view_item = {};

oer.materials.view_item.init = function() {
  oer.materials.view_item.init_navigation();
  oer.materials.view_item.init_comment();
};

oer.materials.view_item.init_navigation = function() {
  var $navigation = $("nav.view-item-navigation");
  if ($navigation.length) {
    var index_cookie = unescape($navigation.data("index-cookie"));
    $navigation.find("a.item-link").click(function() {
      $.cookie("_i", index_cookie, {path: "/"});
    });
    $("div.details h1 a").click(function() {
      $.cookie("_i", index_cookie, {path: "/"});
    });
    $("#goto").click(function() {
      $.cookie("_i", index_cookie, {path: "/"});
    });
  }
};

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

  $(document).click(function() {
    $content_actions.find("dl").removeClass("active");
  });
};

$.template("comment", '<article class="author rc5"><p>{{html text}}</p><footer><a class="edit" href="#"><span>Edit</span></a> <a class="delete" href="#"><span>Delete</span></a> <span class="by">- ${author}</span></footer></article>');

oer.materials.view_item.init_comment = function() {
  var $comments = $("section.resource-comments");
  var $form = $("#comment-form");

  function init_delete_buttons() {
    $comments.find("a.delete").inlineConfirmation({
      confirm: '<a href="#" class="dashed"><strong>Yes, delete</strong></a>',
      cancel: '<a href="#" class="dashed">Cancel</a>',
      confirmCallback: function($button) {
        var $comment = $button.closest("article");
        $comment.remove();
        $.post($form.attr("action"), {"delete": "yes"});
        $form.find("textarea").val("");
        $form.detach().appendTo($comments).show();
      }
    });
  }
  init_delete_buttons();

  $form.find("div.buttons a").click(function(e) {
    e.preventDefault();
    $form.submit();
  });

  $form.validate({
    rules: {
      text: "required"
    },
    submitHandler: function() {
      if (!oer.login.is_authenticated()) {
        oer.login.show_popup(function() {
          $form.submit();
        });
        return;
      }
      $.post($form.attr("action"), $form.serialize(), function(response) {
        if (response.status === "success") {
          oer.status_message.success(response.message, true);
          $form.hide();
          var $comment = $.tmpl("comment", response);
          $comment.insertBefore($form);
          rcorners($comment);
          init_delete_buttons();
        }
      });
    }
  });

  $comments.delegate("a.edit", "click", function(e) {
    e.preventDefault();
    var $comment = $(this).closest("article");
    $form.detach().insertAfter($comment).show();
    $comment.remove();
  });

};
