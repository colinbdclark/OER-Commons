oer.authoring = {};

oer.authoring.Editor = function () {
  var $editor = $("#editor");
  var $toolbar = $editor.find(".toolbar");
  var $area = $editor.find(".editor-area");

  function execCommand(command) {
    if (arguments.length == 2) {
      document.execCommand(command, false, arguments[1]);
    } else {
      document.execCommand(command, false, null);
    }
  }

  function focusOnNode($node) {
    var range, selection;
    var node = $node.get(0);
    if (document.createRange)//Firefox, Chrome, Opera, Safari, IE 9+
    {
      range = document.createRange();//Create a range (a range is a like the selection but invisible)
      range.selectNodeContents(node);//Select the entire contents of the element with the range
      range.collapse(false);//collapse the range to the end point. false means collapse to end rather than the start
      selection = window.getSelection();//get the selection object (allows you to change selection)
      selection.removeAllRanges();//remove any selections already made
      selection.addRange(range);//make the range you have just created the visible selection
    }
    else if (document.selection)//IE 8 and lower
    {
      range = document.body.createTextRange();//Create a range (a range is a like the selection but invisible)
      range.moveToElementText(node);//Select the entire contents of the element with the range
      range.collapse(false);//collapse the range to the end point. false means collapse to end rather than the start
      range.move("character", -1);
      range.select();//Select the range (make it the visible selection)
    }
  }

  var $currentNode = null; // Active element inside editor area.
  var $currentBlock = null; // Active block level element inside editor area.

  // Find the currently active block in editable area when user clicks on
  // any of toolbar buttons. We use mousedown here because IE looses the focus
  // when mouse button is released so it becomes impossible to find the active
  // block.
  $toolbar.mousedown(function(e) {
    var anchorNode;
    if (window.getSelection) {
      anchorNode = window.getSelection().anchorNode;
      if (!anchorNode) {
        return;
      }
      if (anchorNode.nodeType === 3) { // Text node
        anchorNode = anchorNode.parentNode;
      }
    } else if (document.selection) {
      var textRange = document.selection.createRange();
      textRange.collapse(true);
      anchorNode = textRange.parentElement();
    } else {
      return;
    }
    var $anchorNode = $(anchorNode);
    if ($anchorNode.closest($area).length === 0) {
      // The node is contained outside of editor area
      return;
    }
    $currentNode = $anchorNode;
    // Get the top level node inside editor area containing the active node.
    var $parents = $anchorNode.parentsUntil($area);
    if ($parents.length === 0) {
      $currentBlock = $anchorNode;
    } else {
      $currentBlock = $parents.last();
    }
  });

  function changeBlockType(newType) {
    if (!$currentBlock) {
      return;
    }
    if ($currentBlock.is(newType)) {
      return;
    }
    var inner;
    if ($currentBlock.is("p,div,h2,h3,blockquote")) {
      inner = $currentBlock.html();
    } else if ($currentBlock.is("ul,ol")) {
      inner = $currentBlock.text();
    } else {
      return;
    }
    var $newBlock = $("<" + newType + "/>");
    $newBlock.html(inner);
    $newBlock.insertAfter($currentBlock);
    $currentBlock.remove();
    focusOnNode($newBlock);
  }

  function insertList(listType) {
    if (!$currentBlock) {
      return;
    }
    var $list = $("<" + listType + "/>");
    var $li = $("<li></li>").appendTo($list);
    $list.insertAfter($currentBlock);
    if ($currentBlock.is("p,div")) {
      $li.html($currentBlock.html());
      $currentBlock.remove();
      $currentBlock = $list;
    }
    focusOnNode($li);
  }

  // Init text style menu
  var $textStyleMenu = $toolbar.find("div.text-style");
  $textStyleMenu.find("a.select").click(function (e) {
    e.preventDefault();
    e.stopPropagation();
    $textStyleMenu.toggleClass("active");
  });
  $(document).click(function () {
    $textStyleMenu.removeClass("active");
  });
  $textStyleMenu.delegate("ul a", "click", function (e) {
    e.preventDefault();
    var $target = $(this);
    var href = $target.attr("href");
    switch (href) {
      case "#regular":
        changeBlockType("p");
        break;
      case "#header":
        changeBlockType("h2");
        break;
      case "#sub-header":
        changeBlockType("h3");
        break;
      case "#quote":
        changeBlockType("blockquote");
        break;
      default:
        break;
    }
  });

  // Init formatting buttons
  $toolbar.delegate("a.button", "click", function (e) {
    e.preventDefault();
    var $target = $(this);
    var href = $target.attr("href");
    switch (href) {
      case "#bold":
        execCommand("bold");
        break;
      case "#italic":
        execCommand("italic");
        break;
      case "#underline":
        execCommand("underline");
        break;
      case "#bullet-list":
        insertList("ul");
        break;
      case "#number-list":
        insertList("ol");
        break;
      case "#link":
        if ($currentNode.is("a") || $currentNode.parentsUntil($area, "a").length) {
          // We are inside <a> element. Do nothing.
          break;
        }
        execCommand("createLink", "#new-link");
        var $link = $area.find("a[href='#new-link']");
        $link.attr("href", "http://");
        $link.data("new", true);
        if ($link.text() === "#new-link") {
          $link.text("Link");
        }
        $link.click();
        break;
    }

  });
  $area.keyup(function (e) {
    if (e.which === 8 || e.which === 46) {
      if ($area.children().length === 0) {
        focusOnNode($("<p><br/></p>").appendTo($area));
      }
    }
  });

  var $form = $("#edit-authored-material");
  var $title = $("#material-title");
  var $titleInput = $("#id_title");

  $title.editable(function(value) {
    $titleInput.val(value);
    return value;
  }, {
    cssclass: "title-input",
    width: "none",
    height: "none",
    onblur: "submit",
    tooltip: "Click to edit..."
  });

  var $textInput = $("#id_text");
  var $preview = $editor.find("div.preview");

  var $actions = $("div.actions a");
  $actions.click(function (e) {
    e.preventDefault();
    var $this = $(this);
    var href = $this.attr("href");
    switch (href) {
      case "#save":
        $textInput.val($area.html());
        oer.status_message.clear();
        $.post($form.attr("action"), $form.serialize(), function (response) {
          if (response.status === "success") {
            oer.status_message.success(response.message, true);
          } else {
            oer.status_message.success(response.message, false);
          }
        });
        break;
      case "#preview":
        $preview.html($area.html());
        $toolbar.hide();
        $area.hide();
        $preview.show();
        $actions.filter(".edit").removeClass("hidden");
        $this.addClass("hidden");
        break;
      case "#edit":
        $preview.hide();
        $toolbar.show();
        $area.show();
        $actions.filter(".preview").removeClass("hidden");
        $this.addClass("hidden");
        break;
      default:
        break;
    }
  });

  // Link UI
  var $linkDialog = $("#edit-link-dialog");
  var $linkDialogInput = $linkDialog.find("input[name='url']");

  $linkDialog.delegate("a", "click", function(e) {
    // TODO: use form with URL validation here.
    e.preventDefault();
    var href = $(e.target).attr("href");
    var $link = $linkDialog.data("link");
    switch (href) {
      case "#save":
        $linkDialog.data("link").attr("href", $linkDialogInput.val());
        $link.data("new", false);
        break;
      case "#remove":
        if ($link.data("new")) {
          $link.remove();
        } else {
          $link.replaceWith($link.html());
        }
        break;
      case "#cancel":
        break;
      default:
        break;
    }
    $linkDialog.hide();
  });

  $area.delegate("a", "click", function(e) {
    e.preventDefault();
    var $link = $(e.target);
    $linkDialog.data("link", $link);
    $linkDialogInput.val($link.attr("href"));
    var offset = $link.offset();
    $linkDialog.css({
      left: offset.left + 10 + "px",
      top: offset.top + 16 + "px"
    });
    $linkDialog.show();
    $linkDialogInput.focus();
  });

};
