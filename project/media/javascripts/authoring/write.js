$.blockUI.defaults.css = {
  color: "#fff",
  fontSize: "20px"
};
$.blockUI.defaults.message = "Please wait...";

jQuery.fn.outerHTML = function (s) {
  return (s) ? this.before(s).remove() : jQuery("<p></p>").append(this.eq(0).clone()).html();
};

var Write = function () {
  var tool = this;

  this.ALLOWED_TOP_LEVEL_TAGS = "p,div,h1,h2,h3,h4,ul,ol,blockquote,table,figure";
  this.TOP_LEVEL_TEXT_TAGS = "p,div,h1,h2,h3,h4,ul,ol,blockquote";
  this.ALLOWED_CLASSES = ["embed", "image", "video", "document", "download", "reference", "button", "l1", "l2", "l3", "l4", "l5"];
  for (var i = 1; i < 6; i++) {
    this.ALLOWED_CLASSES.push("text-color-" + i);
    this.ALLOWED_CLASSES.push("bg-color-" + i);
  }
  this.HEADER_LEVELS = {
    h2: 0,
    h3: 1
  };

  // Key codes for keys which don't cause the change of editor contents
  this.SPECIAL_KEY_CODES = [
    9, // tab
    16, // shift
    17, // ctrl
    18, // alt
    19, // pause/break
    20, // caps lock
    27, // escape
    45, // insert
    91, // left window key
    92, // right window key
    93, // select key
    112, // f1
    113, // f2
    114, // f3
    115, // f4
    116, // f5
    117, // f6
    118, // f7
    119, // f8
    120, // f9
    121, // f10
    122, // f11
    123, // f12
    144, // num lock
    145  // scroll lock
  ];

  this.ENTER = 13;
  this.BACKSPACE = 8;
  this.DELETE = 46;

  this.NAVIGATION_KEYS = [
    33, // page up
    34, // page down
    35, // end
    36, // home
    37, // left arrow
    38, // up arrow
    39, // right arrow
    40  // down arrow
  ];
  this.CTRL = 17;
  this.CMD = 91;

  this.$form = $("#write-form");
  this.$toolbar = $("#toolbar");
  this.$toolbarButtons = this.$toolbar.find("a.button");
  this.$area = $("#editor-area");
  this.$outline = $("#outline");
  this.$textStyleIndicator = this.$toolbar.find(".text-style > a span");
  this.$footnotes = $("#footnotes");

  this.selection = null;
  this.range = null;
  this.$anchorNode = null; // Element at the beginning of text selection
  this.$anchorBlock = null; // Top level element at the beginning of text selection
  this.$focusNode = null; // Element at the end of text selection
  this.$focusBlock = null; // Top level element at the end of text selection

  this.shouldSaveState = true; // Flag to define if we should save current state in undo history

  this.$area.find("figure,a").attr("contenteditable", "false");

  this.cleanHTML();
  this.ensureTextInput();

  // Track when user presses and releases Ctrl or Cmd keys
  this.ctrlKey = false;
  this.cmdKey = false;
  $(document).keydown(
          function (e) {
            if (e.which == tool.CTRL) {
              tool.ctrlKey = true;
            }
            if (e.which == tool.CMD) {
              tool.cmdKey = true;
            }
            if ((tool.ctrlKey || tool.cmdKey) && e.which == 90) {
              tool.undo();
              e.preventDefault();
            }
          }).keyup(function (e) {
            // Track Ctrl+Z / Cmd+Z
            if (e.which == tool.CTRL) {
              tool.ctrlKey = false;
            }
            if (e.which == tool.CMD) {
              tool.cmdKey = false;
            }
          });

  this.undoHistory = [];
  this.lastState = null;
  this.undoDepth = 0;
  this.undoDisabled = true;
  this.redoDisabled = true;

  // Prevent clicking on disabled buttons
  this.$toolbar.find("a").click(function (e) {
    if ($(this).hasClass("disabled")) {
      e.preventDefault();
      e.stopPropagation();
      e.stopImmediatePropagation();
    }
  });

  this.initTextStyleMenu();
  this.initUndoButtons();
  this.initFormattingButtons();
  this.initIndentButtons();
  this.initListButtons();
  this.initLinks();
  this.initColorButtons();
  this.initOutline();
  this.initReferences();

  new MediaDialog(this);

  this.$area.find("figure").each(function () {
    tool.initFigure($(this));
  });
  this.$area.find("figure.embed").each(function () {
    tool.loadEmbed($(this));
  });

  // Clean up HTML on paste and check for changes
  this.$area.bind("paste", function () {
    tool.saveState();
    setTimeout(function () {
      tool.cleanHTML();
    }, 200);
  });

  // Update selected nodes when user click on editor area or select text with mouse
  // and save selection.
  this.$area.mouseup(function () {
    tool.trackSelection();
  });

  // Track editor changes caused by pressing keys.
  tool.$area.keyup(function (e) {

    if ($.inArray(e.which, tool.SPECIAL_KEY_CODES) != -1) {
      return;
    }

    // Update the focused nodes if user moves the caret.
    if ($.inArray(e.which, tool.NAVIGATION_KEYS) != -1 || $.inArray(e.which, [tool.ENTER, tool.BACKSPACE, tool.DELETE]) != -1) {
      tool.trackSelection();
      if ($.inArray(e.which, [tool.BACKSPACE, tool.DELETE]) == -1) {
        return;
      }
    }

    // Update the outline if current block is a header
    if (tool.$focusBlock && tool.$focusBlock.is("h1,h2,h3")) {
      var $header = tool.$focusBlock;
      var $li = $header.data("outline");
      if (!$li) {
        tool.updateOutline();
        $li = $header.data("outline");
      }
      $li.text($header.text());
    }

  });

  var keydownTimeout = null;
  // User is about to type something. Save current state.
  tool.$area.keydown(function (e) {

    if (tool.ctrlKey || tool.cmdKey || $.inArray(e.which, tool.SPECIAL_KEY_CODES) != -1 || $.inArray(e.which, tool.NAVIGATION_KEYS) != -1) {
      return;
    }

    tool.saveState();
    tool.shouldSaveState = false;
    if (keydownTimeout) {
      clearTimeout(keydownTimeout);
    }
    keydownTimeout = setTimeout(function () {
      tool.shouldSaveState = true;
      keydownTimeout = null;
    }, 1000);
  });

  tool.$area.keyup(function (e) {
    if (e.which == tool.DELETE || e.which == tool.BACKSPACE) {
      tool.ensureTextInput();
    }
  });

  // TODO: move this to separate init... methods
  // Material title
  (function () {
    var $title = $("#material-title");
    var $titleInput = $("#id_title");

    $title.editable(function (value) {
      $titleInput.val(value);
      return value;
    }, {
      cssclass: "title-input",
      width: "none",
      height: "none",
      onblur: "submit",
      tooltip: "Click to edit..."
    });
  })();

  // Save, Cancel actions
  (function () {
    var $titleInput = $("#id_title");
    var $textInput = $("#id_text");
    var $preview = tool.$form.find("div.preview");
    var $actions = $("div.authoring-head div.actions a");
    $actions.click(function (e) {
      e.preventDefault();
      var $this = $(this);
      var href = $this.attr("href");
      switch (href) {
        case "#save":
          tool.cleanHTML();
          var html = tool.cleanHtmlPreSave(tool.$area.html());
          $textInput.val(html);
          oer.status_message.clear();
          var data = {
            title: $titleInput.val(),
            text: $textInput.val()
          };
          $.post(tool.$form.attr("action"), data, function (response) {
            if (response.status === "success") {
              oer.status_message.success(response.message, true);
            } else {
              oer.status_message.error(response.message, false);
            }
          });
          break;
        case "#preview":
          // TODO: disable table of contents
          $preview.html(tool.$area.html());
          tool.$toolbar.hide();
          tool.$area.hide();
          $preview.show();
          $actions.filter(".edit").removeClass("hidden");
          $this.addClass("hidden");
          break;
        case "#edit":
          // TODO: re-enable table of contents
          $preview.hide();
          tool.$toolbar.show();
          tool.$area.show();
          $actions.filter(".preview").removeClass("hidden");
          $this.addClass("hidden");
          break;
        default:
          break;
      }
    });
  })();

  // Next step
  this.$form.find("div.buttons a").click(function (e) {
    e.preventDefault();
    // TODO: clean and save HTML here
    var $next = tool.$form.find("input[name='next']");
    if ($(this).hasClass("next")) {
      $next.val("true");
    } else {
      $next.val("false");
    }
    $("#id_text").val(tool.cleanHtmlPreSave(tool.$area.html()));
    tool.$form.submit();
  });

};

Write.prototype.cleanHTML = function () {
  var tool = this;
  var $area = this.$area;

  var selection = null;
  if ("saveSelection" in rangy) {
    this.removeSelectionMarkers();
    selection = rangy.saveSelection();
  }

  // Clear HTML comments
  $area.html($area.html().replace(/<!--[\s\S]*?-->/g, ""));

  // Remove non-safe elements (scripts, styles, forms, inputs)
  $area.find("script,style,form,input,textarea,button").remove();

  // Unwrap <span style="">, <font>, <o:p> (comes from MS Word) and other crap
  $area.find("font,span[style],p[class^='Mso'],o\\:p").not("span.rangySelectionBoundary").replaceWith(function () {
    return $(this).contents();
  });

  // TODO: remove crap <span>s. Note that we'll use <span class="..."> for text color and selection markers

  // And we also use <span>s inside figures (although we might get rid of them).

  // Remove all 'styles' attributes
  $area.find("[style]").removeAttr("style");

  // Remove not allowed classes
  $area.find("[class]").removeClass(function (i, oldClasses) {
    oldClasses = oldClasses.split(" ");
    oldClasses.sort();
    var remove = [];
    for (i = 0; i < oldClasses.length; i++) {
      if ($.inArray(oldClasses[i], tool.ALLOWED_CLASSES) === -1) {
        remove.push(oldClasses[i]);
      }
    }
    return remove.join(" ");
  });

  // Remove class attribute from elements with empty class
  $area.find("[class='']").removeAttr("class");

  // Remove all iframes, objects, embeds which are not inside <figure class="embed">
  $area.find("iframe,object,embed,param").each(function () {
    var $this = $(this);
    if ($this.closest("figure.embed", $area).length === 0) {
      $this.remove();
    }
  });

  // Replace all <div>s with <p>s
  $area.find("div").replaceWith(function () {
    return $("<p></p>").html($(this).html());
  });

  // Unwrap nested <p>s
  $area.find("p > p").each(function () {
    var $parent = $(this).parent("p", $area);
    $parent.replaceWith(function () {
      return $(this).contents();
    });
  });

  // Wrap all top-level non-block elements in <p>s (including non-empty text nodes)
  $area.contents().not(this.ALLOWED_TOP_LEVEL_TAGS).filter(
          function () {
            if (this.nodeType === 3 && $.trim(this.text) !== "") {
              // Non-empty text node
              return true;
            }
            return this.tagName !== "p";
          }).wrap("<p></p>");

  // Remove empty paragraphs
  $area.html($area.html().replace(/<p[^>]*?>\s*?<\/\s*p>/gi, ""));

  // Replace <h1> with <h2> since this should be a top level header
  $area.find("h1").replaceWith(function () {
    return $("<h2></h2>").html($(this).html());
  });

  if (selection) {
    rangy.restoreSelection(selection);
    rangy.removeMarkers(selection);
  }

};

Write.prototype.cleanHtmlPreSave = function (html) {
  // TODO: remove interface elements here
  var $document = $("<div></div>").html(html);
  $document.find("[contenteditable]").removeAttr("contenteditable");
  return $document.html();
};

// Ensure that we always have a text block at the end of editor area
Write.prototype.ensureTextInput = function () {
  var $area = this.$area;
  if (!$area.children().last().is(this.TOP_LEVEL_TEXT_TAGS)) {
    var $p = $("<p><br/></p>").appendTo($area);
    if ($area.children().length == 1) {
      this.focusOnNode($p);
    }
  }
};

Write.prototype.execCommand = function (command) {
  if (arguments.length == 2) {
    document.execCommand(command, false, arguments[1]);
  } else {
    document.execCommand(command, false, null);
  }
};

Write.prototype.focusOnNode = function ($node) {
  // TODO: rewrite this to rangy, allow to focus at specific offset
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
  this.trackSelection();
};

Write.prototype.trackSelection = function () {

  // Rangy is not initialized?
  if (!"getSelection" in rangy) {
    return;
  }

  var selection = this.selection = rangy.getSelection();
  if (selection.rangeCount) {
    this.range = selection.getRangeAt(0);
  } else {
    this.range = null;
  }
  var anchorNode = selection.anchorNode,
          focusNode = selection.focusNode;
  if (anchorNode && anchorNode.nodeType === 3) {
    anchorNode = anchorNode.parentNode;
  }
  if (focusNode && focusNode.nodeType === 3) {
    focusNode = focusNode.parentNode;
  }
  var $anchorNode = $(anchorNode);
  var $focusNode = $(focusNode);
  var $anchorBlock = null;
  var $focusBlock = null;

  if ($anchorNode.length && !$anchorNode.is(this.$area) && $anchorNode.closest(this.$area).length) {
    if ($anchorNode.parent().is(this.$area)) {
      $anchorBlock = $anchorNode;
    } else {
      $anchorBlock = $anchorNode.parentsUntil(this.$area).slice(-1);
    }
  } else {
    $anchorNode = null;
  }

  if ($focusNode.length && !$focusNode.is(this.$area) && $focusNode.closest(this.$area).length) {
    if ($focusNode.parent().is(this.$area)) {
      $focusBlock = $focusNode;
    } else {
      $focusBlock = $focusNode.parentsUntil(this.$area).slice(-1);
    }
  } else {
    $focusNode = null;
  }

  this.$anchorNode = $anchorNode;
  this.$anchorBlock = $anchorBlock;
  this.$focusNode = $focusNode;
  this.$focusBlock = $focusBlock;

  this.updateToolbarState();

};

Write.prototype.changeBlockType = function (newType) {
  if (!this.$focusBlock) {
    return;
  }
  if (this.$focusBlock.is(newType)) {
    return;
  }
  if (!this.$focusBlock.is(this.TOP_LEVEL_TEXT_TAGS)) {
    return;
  } else if (this.$focusBlock.is("ul,ol")) {
    return;
  }
  this.saveState();
  var $newBlock = $("<" + newType + "/>");
  $newBlock.html(this.$focusBlock.html());
  $newBlock.insertAfter(this.$focusBlock);
  this.$focusBlock.remove();
  this.focusOnNode($newBlock);
};

Write.prototype.activateButton = function (button) {
  this.$toolbarButtons.filter("." + button).addClass("active");
};

Write.prototype.updateToolbarState = function () {
  var $anchorNode = this.$anchorNode;
  var $anchorBlock = this.$anchorBlock;
  var $focusNode = this.$focusNode;
  var $focusBlock = this.$focusBlock;

  this.$toolbar.find(".active").removeClass("active");
  this.disableButton("indent");
  this.disableButton("outdent");

  if (!$focusNode || !$focusBlock) {
    return;
  }

  if (!this.selection || this.selection.isCollapsed) {
    this.disableButton("bold");
    this.disableButton("italic");
    this.disableButton("underline");
    this.disableButton("text-color");
    this.disableButton("bg-color");
  } else {
    this.enableButton("bold");
    this.enableButton("italic");
    this.enableButton("underline");
    this.enableButton("text-color");
    this.enableButton("bg-color");
    if ($focusNode.closest("strong,b", this.$area).length) {
      this.activateButton("bold");
    }
    if ($focusNode.closest("em,i", this.$area).length) {
      this.activateButton("italic");
    }
    if ($focusNode.closest("u", this.$area).length) {
      this.activateButton("underline");
    }
  }

  if ($focusBlock.is("h2")) {
    this.$textStyleIndicator.text("Header");
  } else if ($focusBlock.is("h3")) {
    this.$textStyleIndicator.text("Sub-Header");
  } else if ($focusBlock.is("blockquote")) {
    this.$textStyleIndicator.text("Long Quote");
    if (this.getQuoteLevel($focusBlock) < 5) {
      this.enableButton("indent");
    }
    this.enableButton("outdent");
  } else if ($focusBlock.is("p,div")) {
    this.$textStyleIndicator.text("Paragraph");
    this.enableButton("indent");
  } else {
    this.$textStyleIndicator.text("Text style...");
  }

  if ($focusBlock.is("ul,ol")) {
    if ($focusBlock.is("ul")) {
      this.activateButton("bullet-list");
    } else if ($focusBlock.is("ol")) {
      this.activateButton("number-list");
    }
    var $anchorLi = $anchorNode.closest("li", $anchorBlock);
    var $focusLi = $focusNode.closest("li", $focusBlock);
    if ($anchorLi.length && $focusLi.length && $anchorLi.parent().is($focusLi.parent())) {
      this.enableButton("indent");
      this.enableButton("outdent");
    }
  }

};

Write.prototype.insertList = function (listType) {
  if (!this.$focusBlock) {
    return;
  }
  this.saveState();

  var $list = $("<" + listType + "/>");
  var $li = $("<li></li>").appendTo($list);
  $list.insertAfter(this.$focusBlock);
  if (this.$focusBlock.is("p,div")) {
    $li.html(this.$focusBlock.html());
    this.$focusBlock.remove();
    this.$focusBlock = $list;
  }
  this.focusOnNode($li);

  // TODO: make list from selection. If selection is not empty create list from it. Items are separated by new lines.
  // Take care of inline html.

};

Write.prototype.initUndoButtons = function () {
  var tool = this;
  this.$toolbar.find("a.button.undo").click(function (e) {
    e.preventDefault();
    tool.undo();
  });
  this.$toolbar.find("a.button.redo").click(function (e) {
    e.preventDefault();
    tool.redo();
  });
};

Write.prototype.initTextStyleMenu = function () {
  var tool = this;
  var $menu = this.$toolbar.find("div.text-style");
  $menu.find("a.select").click(function (e) {
    e.preventDefault();
    e.stopPropagation();
    $menu.toggleClass("active");
  });
  $(document).click(function () {
    $menu.removeClass("active");
  });
  $menu.delegate("ul a", "click", function (e) {
    e.preventDefault();
    var $target = $(this);
    var href = $target.attr("href");
    switch (href) {
      case "#header":
        tool.changeBlockType("h2");
        break;
      case "#sub-header":
        tool.changeBlockType("h3");
        break;
      case "#paragraph":
        tool.changeBlockType("p");
        break;
      case "#quote":
        tool.changeBlockType("blockquote");
        break;
      default:
        break;
    }
  });
};

Write.prototype.initFormattingButtons = function () {
  var tool = this;
  this.$toolbar.find("a.button.bold").click(function (e) {
    e.preventDefault();
    tool.saveState();
    tool.execCommand("bold");
    tool.trackSelection();
  });
  this.$toolbar.find("a.button.italic").click(function (e) {
    e.preventDefault();
    tool.saveState();
    tool.execCommand("italic");
    tool.trackSelection();
  });
  this.$toolbar.find("a.button.underline").click(function (e) {
    e.preventDefault();
    tool.saveState();
    tool.execCommand("underline");
    tool.trackSelection();
  });
};

Write.prototype.initListButtons = function () {
  var tool = this;
  this.$toolbar.find("a.button.bullet-list").click(function (e) {
    e.preventDefault();
    tool.insertList("ul");
  });
  this.$toolbar.find("a.button.number-list").click(function (e) {
    e.preventDefault();
    tool.insertList("ol");
  });
};

Write.prototype.getQuoteLevel = function ($quote) {
  var classes = {};
  var classNames = $quote.attr("class");
  if (!classNames) {
    return 0;
  }
  $(classNames.split(" ")).each(function () {
    classes[this] = this;
  });
  for (var className in classes) {
    var match = className.match(/l([12345])/);
    if (match) {
      return parseInt(match[1]);
    }
  }
  return 0;
};

Write.prototype.initIndentButtons = function () {
  var tool = this;

  this.$toolbar.find("a.button.indent").click(function (e) {
    e.preventDefault();
    var $anchorNode = tool.$anchorNode;
    var $anchorBlock = tool.$anchorBlock;
    var $focusBlock = tool.$focusBlock;
    var $focusNode = tool.$focusNode;
    if (!$focusBlock) {
      return;
    }

    if ($focusBlock.is("p,div")) {
      tool.changeBlockType("blockquote");
    } else if ($focusBlock.is("blockquote")) {
      var level = tool.getQuoteLevel($focusBlock);
      if (level < 5) {
        tool.saveState();
        $focusBlock.removeClass().addClass("l" + (level + 1));
        tool.trackSelection();
      }
    } else {
      var $anchorLi = $anchorNode.closest("li", $anchorBlock);
      var $focusLi = $focusNode.closest("li", $focusBlock);
      var $parent = $anchorLi.parent();
      if ($anchorLi.length && $focusLi.length && $parent.is($focusLi.parent())) {
        var $siblings = $parent.children();
        var start = $siblings.index($anchorLi);
        var end = $siblings.index($focusLi);
        if (start > end) {
          var t = start;
          start = end;
          end = t;
        }
        var $indentedLis = $siblings.slice(start, end + 1);
        var $wrapper = $parent.is("ul") ? $("<ul></ul>") : $("<ol></ol>");
        tool.saveState();
        var selection = rangy.saveSelection();
        $wrapper.insertBefore($anchorLi).append($indentedLis.detach());
        rangy.restoreSelection(selection);
        tool.trackSelection();
      }
    }
  });

  this.$toolbar.find("a.button.outdent").click(function (e) {
    e.preventDefault();
    var $anchorNode = tool.$anchorNode;
    var $anchorBlock = tool.$anchorBlock;
    var $focusBlock = tool.$focusBlock;
    var $focusNode = tool.$focusNode;
    if (!$focusBlock) {
      return;
    }
    if ($focusBlock.is("blockquote")) {
      var level = tool.getQuoteLevel($focusBlock);
      if (level === 0) {
        tool.changeBlockType("p");
      } else {
        tool.saveState();
        $focusBlock.removeClass().addClass("l" + (level - 1));
        tool.trackSelection();
      }
    } else {
      var $anchorLi = $anchorNode.closest("li", $anchorBlock);
      var $focusLi = $focusNode.closest("li", $focusBlock);
      var $parent = $anchorLi.parent();
      if ($anchorLi.length && $focusLi.length && $parent.is($focusLi.parent())) {
        var $siblings = $parent.children();
        var start = $siblings.index($anchorLi);
        var end = $siblings.index($focusLi);
        if (start > end) {
          var t = start;
          start = end;
          end = t;
        }
        var $prevLis = $siblings.slice(0, start);
        var $nextLis = $siblings.slice(end + 1);
        var $indentedLis = $siblings.slice(start, end + 1);
        var $wrapper = $parent.is("ul") ? $("<ul></ul>") : $("<ol></ol>");
        tool.saveState();
        var selection = rangy.saveSelection();
        if ($prevLis.length) {
          $prevLis = $prevLis.detach();
          $wrapper.clone(false).append($prevLis).insertBefore($parent);
        }
        if ($nextLis.length) {
          $nextLis = $nextLis.detach();
          $wrapper.clone(false).append($nextLis).insertAfter($parent);
        }
        $indentedLis.detach().insertBefore($parent);
        if (!$parent.parents("ul,li").length) {
          $indentedLis.filter("li").replaceWith(function () {
            return $("<p></p>").html($(this).html());
          });
        }
        $parent.remove();
        rangy.restoreSelection(selection);
        tool.trackSelection();
      }
    }
  });
};

Write.prototype.insertLink = function () {
  var args = {};
  if (arguments.length) {
    args = arguments[0];
  }
  this.execCommand("createLink", "#new-link");
  var $link = this.$area.find("a[href='#new-link']");
  var new_ = true;
  if (args.url) {
    $link.attr("href", args.url);
    new_ = false;
  } else {
    $link.attr("href", "http://");
  }
  if ("text" in args) {
    $link.html(args.text);
  } else if ($link.text() == "#new-link") {
    $link.text("Link");
  }
  if (args["class"]) {
    $link.addClass(args["class"]);
  }
  if (args.container) {
    $link.detach().appendTo(args.container);
  }
  if (new_) {
    $link.data("new", true);
    $link.click();
  }
  $link.attr("contenteditable", "false");
  this.trackSelection();
};

Write.prototype.initLinks = function () {
  var tool = this;

  this.$toolbarButtons.filter(".link").click(function (e) {
    e.preventDefault();
    var $link = null;
    if (tool.$focusNode) {
      $link = tool.$focusNode.closest("a", tool.$area);
    }
    if ($link && $link.length) {
      return;
    }
    if (tool.selection && tool.selection.isCollapsed) {
      tool.insertLink({text: ""});
    } else {
      tool.insertLink();
    }
  });

  var $dialog = $("#link-dialog");
  var $urlInput = $dialog.find("input[name='link_url']");
  var $textInput = $dialog.find("input[name='link_text']");

  $dialog.find("a.button[href='#cancel']").click(function (e) {
    e.preventDefault();
    var $link = $dialog.data("link");
    if ($link.data("new")) {
      $link.replaceWith(function () {
        return $(this).html();
      });
      tool.trackSelection();
    }
    $dialog.hide();
  });

  $dialog.find("a.button[href='#save']").click(function (e) {
    e.preventDefault();
    var $link = $dialog.data("link");
    if (!$link.data("new")) {
      tool.saveState();
    }
    $link.text($textInput.val());
    $link.attr("href", $urlInput.val())
    $dialog.hide();
  });

  $dialog.find("a.remove").click(function (e) {
    e.preventDefault();
    var $link = $dialog.data("link");
    if (!$link.data("new")) {
      tool.saveState();
    }
    $link.remove();
    tool.trackSelection();
    $dialog.hide();
  });

  this.$area.delegate("a", "click", function (e) {
    e.preventDefault();
    var $link = $(this);
    if ($link.is(".download,.reference")) {
      return;
    }
    $dialog.data("link", $link);
    $urlInput.val($link.attr("href"));
    $textInput.val($.trim($link.text()));
    var offset = $link.offset();
    $dialog.css({
      left: offset.left - 263 + "px",
      top: offset.top + 35 + "px"
    });
    $dialog.show();
    $urlInput.focus();
  });

};

Write.prototype.initColorButtons = function () {
  var tool = this;
  var $toolbar = this.$toolbar;
  var $selectors = $toolbar.find("div.color-selector");
  $selectors.find("a.button").click(function (e) {
    e.preventDefault();
    e.stopPropagation();
    var $this = $(this);
    var $selector = $this.parent();
    if ($selector.hasClass("active")) {
      $selector.removeClass("active");
    } else {
      var $lis = $selector.find("li").removeClass("selected");
      $lis.slice(0, 5).each(function () {
        var $li = $(this);
        var applier = rangy.createCssClassApplier($li.attr("class"));
        if (applier.isAppliedToSelection()) {
          $li.addClass("selected");
        }
      });
      if (!$lis.filter(".selected").length) {
        $lis.slice(-1).addClass("selected");
      }
      $selector.addClass("active");
    }
  });
  $selectors.delegate("li", "mousedown", function (e) {
    e.stopPropagation();
    var $this = $(this);
    var i, applier;
    tool.saveState();

    var classNames = $this.attr("class");
    var classes = {};
    var class_ = null;
    var prefix = null;
    $(classNames.split(" ")).each(function () {
      classes[this] = this;
    });
    for (var className in classes) {
      var match = className.match(/(text|bg)-color-(remove|[12345])/);
      if (match) {
        class_ = match[0];
        prefix = match[1];
        break;
      }
    }

    // TODO: initialize and save CssclassAppliers on tool initialization and re-use them here

    // Remove existing colors
    for (i = 1; i < 6; i++) {
      applier = rangy.createCssClassApplier(prefix + "-color-" + i);
      applier.undoToSelection();
    }
    if (class_.indexOf("-remove") === -1) {
      applier = rangy.createCssClassApplier(class_);
      applier.applyToSelection();
    }
  });

  $(document).click(function () {
    $selectors.removeClass("active");
  });
};

Write.prototype.initFigure = function ($figure) {
  $figure.attr("contenteditable", "false");

  if (!$figure.hasClass("inline")) {
    this.initDND($figure);
  }
};

Write.prototype.initDND = function ($block) {
  // TODO: images are glued together when dragging
  if (!$block.draggable("option", "disabled")) {
    return;
  }
  var tool = this;
  $block.draggable({
    helper: "clone",
    opacity: 0.3,
    appendTo: "body",
    addClasses: false,
    cursor: "move"
  });
  $block.bind("dragstart", function () {
    var $blocks = tool.$area.children().not($block).not($block.prev());
    $blocks.droppable({
      addClasses: false,
      tolerance: "pointer"
    });
    $blocks.bind("dropover", function () {
      var $this = $(this);
      $this.stop(true).animate({
        "margin-bottom": "70px"
      });
    });
    $blocks.bind("dropout", function () {
      var $this = $(this);
      $this.stop(true).animate({
        "margin-bottom": ""
      });
    });
    $blocks.bind("drop", function () {
      tool.$area.children().stop(true).css({
        "margin-bottom": ""
      });
      tool.saveState();
      $block.detach().insertAfter($(this));
      if ($block.is("h2,h3")) {
        tool.updateOutline();
      }
    });
  });
  $block.bind("dragstop", function () {
    tool.$area.children().droppable("destroy");
  });
};

Write.prototype.loadEmbed = function ($figure) {
  var url = $figure.data("url");
  $figure.hide();
  if (url) {
    $.post(this.$area.data("load-embed-url"), {url: url}, function (response) {
      var $caption = $figure.find("figcaption").detach();
      $figure.html(response.html).append($caption).fadeIn();
    });
  }
};

Write.prototype.newOutlineItemMessage = function (level) {
  var text = "click to add new ";
  if (level === 0) {
    text += "header";
  } else if (level === 1) {
    text += "sub-header";
  }
  return "<span>" + text + "</span>";
};

Write.prototype.updateOutline = function () {
  var tool = this;
  var prevLevel = 0;
  var $list = $("<ul></ul>").data("level", 0);
  var levels = [];
  this.$area.find("h2,h3").each(function () {
    var level = tool.HEADER_LEVELS[this.tagName.toLowerCase()];
    var i;
    if (level > prevLevel) {
      for (i = 0; i < (level - prevLevel); i++) {
        $list = $("<ul></ul>").data("level", level).appendTo($list);
      }
    } else if (level < prevLevel) {
      for (i = 0; i < (prevLevel - level); i++) {
        $list = $list.parent();
      }
    }
    var $header = $(this);
    var $li = $("<li></li>").text($header.text()).data("header", $header);
    $header.data("outline", $li);
    $list.append($li);
    levels.push(level);
    prevLevel = level;
  });
  while ($list.parent().length) {
    $list = $list.parent();
  }

  $list.find("ul").andSelf().each(function () {
    var $this = $(this);
    $this.append($("<li></li>").addClass("new").html(tool.newOutlineItemMessage($this.data("level"))));
  });

  $list.children("li:not(.new)").filter(function () {
    return $(this).next("ul").length === 0;
  });
  $list.after(function () {
    var level = $(this).parent().data("level") + 1;
    return $("<ul></ul>").data("level", level).append($("<li></li>").addClass("new").html(tool.newOutlineItemMessage(level)));
  });

  this.$outline.data("levels", levels);
  this.$outline.children("ul").remove();
  this.$outline.append($list);
};

Write.prototype.initOutline = function () {
  var tool = this;
  this.updateOutline();

  function trackChanges() {
    // Update only if the structure of headers has changed
    var areaLevels = [];
    tool.$area.find("h2,h3").each(function () {
      areaLevels.push(tool.HEADER_LEVELS[this.tagName.toLowerCase()]);
    });
    var outlineLevels = tool.$outline.data("levels");
    if (areaLevels.length != outlineLevels.length) {
      tool.updateOutline();
    } else {
      for (var i = 0; i < areaLevels.length; i++) {
        if (areaLevels[i] != outlineLevels[i]) {
          tool.updateOutline();
          break;
        }
      }
    }
    setTimeout(trackChanges, 1000);
  }

  setTimeout(trackChanges, 1000);

  tool.$outline.delegate("li.new span", "click", function () {
    var $li = $(this).parent();
    $li.empty();

    function reset() {
      $li.html(tool.newOutlineItemMessage($li.parent().data("level")));
    }

    var $input = $('<input type="text" value="">').appendTo($li);
    $input.keydown(function (e) {
      var text;
      if (e.which === tool.BACKSPACE) {
        text = $input.val();
        if (text === "") {
          e.preventDefault();
          reset();
        }
      } else if (e.which === tool.ENTER) {
        e.preventDefault();
        var level = $li.parent().data("level");
        text = $.trim($input.val());
        reset();
        if (text === "") {
          return;
        }
        var $newLi = $("<li></li>").text(text).insertBefore($li);
        if (level === 0) {
          $newLi.after($("<ul></ul>").data("level", level).append($("<li></li>").addClass("new").html(tool.newOutlineItemMessage(level + 1))));
        }
        var headerType;
        for (var t in tool.HEADER_LEVELS) {
          if (tool.HEADER_LEVELS[t] === level) {
            headerType = t;
            break;
          }
        }
        tool.saveState();
        var $header = $("<" + headerType + ">").text(text).data("outline", $newLi);
        $newLi.data("header", $header);
        var $lis = tool.$outline.find("li:not(.new)");
        var nextHeaderIndex = $lis.index($newLi[0]) + 1;
        if (nextHeaderIndex < $lis.length) {
          $header.insertBefore($($lis[nextHeaderIndex]).data("header"));
        } else {
          tool.$area.append($header);
        }
        $header.after($("<p><br/></p>"));
      }
    });
    $input.blur(reset).focus();
  });

};

Write.prototype.initReferences = function () {
  this.updateReferences();

  var tool = this;
  this.$toolbarButtons.filter(".reference").click(function (e) {
    e.preventDefault();
    var selection = tool.selection;
    if (!selection) {
      return;
    }
    if (!selection.isCollapsed) {
      selection.collapse(false);
      tool.trackSelection();
    }

    tool.saveState();

    tool.execCommand("createLink", "#new-reference");
    var $reference = tool.$area.find("a[href='#new-reference']");
    $reference.addClass("reference");
    $reference.attr("contenteditable", "false");
    $reference.attr("data-text", "");
    $reference.data("new", true);
    tool.updateReferences();
    $reference.click();
  });

  var $dialog = $("#reference-dialog");
  $dialog.find("a.button[href='#cancel']").click(function (e) {
    e.preventDefault();
    var $reference = $dialog.data("reference");
    if ($reference.data("new")) {
      $reference.remove();
    }
    $dialog.hide();
  });

  $dialog.find("a.button[href='#save']").click(function (e) {
    e.preventDefault();
    var $reference = $dialog.data("reference");
    var text = $.trim($dialog.find("textarea").val());
    if (text !== $reference.data("text")) {
      if (!$reference.data("new")) {
        tool.saveState();
      }
      $reference.attr("data-text", text);
      $reference.data("text", text);
      tool.updateReferences();
    }
    $reference.data("new", false);
    $dialog.hide();
  });

  $dialog.find("a.remove").click(function () {
    var $reference = $dialog.data("reference");
    if (!$reference.data("new")) {
      tool.saveState();
    }
    $reference.remove();
    tool.trackSelection();
    tool.updateReferences();
    $dialog.hide();
  });

  this.$area.delegate("a.reference", "click", function (e) {
    e.preventDefault();
    var $this = $(this);
    $dialog.data("reference", $this);
    $dialog.find("textarea").val($this.data("text"));
    var offset = $this.offset();
    $dialog.css({
      left: offset.left - 255 + "px",
      top: offset.top + 35 + "px"
    });
    $dialog.show();
  });

  this.$footnotes.delegate("a.ref", "click", function(e) {
    e.preventDefault();
    var $this = $(this);
    var $reference = $this.parent().data("reference");
    $dialog.data("reference", $reference);
    $dialog.find("textarea").val($reference.data("text"));
    var offset = $this.offset();
    $dialog.css({
      left: offset.left - 255 + "px",
      top: offset.top + 35 + "px"
    });
    $dialog.show();
  });


  function trackChanges() {
    // Update only if the number of references has changed
    if (tool.$area.find("a.reference").length !== tool.$footnotes.children("div.footnote").length) {
      tool.updateReferences();
    }
    setTimeout(trackChanges, 1000);
  }
  setTimeout(trackChanges, 1000);

};

Write.prototype.updateReferences = function () {
  var $footnotes = this.$footnotes.empty();
  this.$area.find("a.reference").each(function (i) {
    var $this = $(this);
    var name = "[" + (i + 1) + "]";
    $this.text(name);
    $this.attr("href", "#ref-" + (i + 1));
    var $footnote = $("<div></div>").addClass("footnote").
            append($("<a></a>").addClass("ref").attr("href", "#").text(name)).
            append($("<div></div>").text($this.data("text")).linkify());
    $footnote.data("reference", $this);
    $footnotes.append($footnote);
  });
};

Write.prototype.removeSelectionMarkers = function () {
  this.$area.find("span.rangySelectionBoundary").remove();
};

Write.prototype.saveState = function () {
  if (!this.shouldSaveState) {
    return;
  }
  var selection = rangy.saveSelection();
  this.undoHistory = this.undoHistory.slice(0, this.undoHistory.length - this.undoDepth);
  // TODO: remove UI elements before saving (placeholders, etc.)
  this.undoHistory.push({content: this.$area.html(), selection: selection});
  this.removeSelectionMarkers();
  this.undoDepth = 0;
  this.enableUndo();
  this.disableRedo();
};

Write.prototype.undo = function () {
  var historyLength = this.undoHistory.length;
  if (this.undoDisabled || this.undoDepth >= historyLength) {
    return;
  }
  if (this.undoDepth === 0) {
    var selection = rangy.saveSelection();
    this.lastState = {content: this.$area.html(), selection: selection};
    this.removeSelectionMarkers();
  }
  this.undoDepth += 1;
  var undoStep = this.undoHistory[historyLength - this.undoDepth];
  this.$area.html(undoStep.content);
  if (undoStep.selection) {
    rangy.restoreSelection(undoStep.selection);
  }
  if (this.undoDepth >= historyLength) {
    this.disableUndo();
  }
  this.enableRedo();
  this.updateOutline();
  this.updateReferences();
  this.trackSelection();
};

Write.prototype.redo = function () {
  var historyLength = this.undoHistory.length;
  if (this.redoDisabled || this.undoDepth === 0) {
    return;
  }
  this.undoDepth -= 1;
  var undoStep = null;
  if (this.undoDepth === 0 && this.lastState) {
    undoStep = this.lastState;
  } else {
    undoStep = this.undoHistory[historyLength - this.undoDepth];
  }
  if (!undoStep) {
    return;
  }
  this.$area.html(undoStep.content);
  if (undoStep.selection) {
    rangy.restoreSelection(undoStep.selection);
  }
  if (this.undoDepth === 0) {
    this.disableRedo();
  }
  this.enableUndo();
  this.updateOutline();
  this.updateReferences();
  this.trackSelection();
};

Write.prototype.disableUndo = function () {
  this.disableButton("undo");
  this.undoDisabled = true;
};

Write.prototype.enableUndo = function () {
  this.enableButton("undo");
  this.undoDisabled = false;
};

Write.prototype.disableRedo = function () {
  this.disableButton("redo");
  this.redoDisabled = true;
};

Write.prototype.enableRedo = function () {
  this.enableButton("redo");
  this.redoDisabled = false;
};

Write.prototype.disableButton = function (button) {
  this.$toolbar.find("." + button).addClass("disabled");
};

Write.prototype.enableButton = function (button) {
  this.$toolbar.find("." + button).removeClass("disabled");
};

function MediaDialog(tool) {
  this.tool = tool;
  this.displayed = false;
  this.$dialog = $("#media-dialog");
  this.$steps = this.$dialog.find("div.step");
  var uploadProgress = new MediaDialog.UploadProgressStep(this);
  this.steps = {
    uploadProgress: uploadProgress,
    upload: new MediaDialog.UploadStep(this, uploadProgress),
    image: new MediaDialog.ImageStep(this),
    video: new MediaDialog.VideoStep(this),
    document: new MediaDialog.DocumentStep(this)
  };

  var dialog = this;
  tool.$toolbar.find("a.media").click(function (e) {
    e.preventDefault();
    if (dialog.displayed) {
      dialog.hide();
    } else {
      dialog.show();
    }
  });
}
MediaDialog.prototype.openStep = function (step, data) {
  this.steps[step].open(data);
};
MediaDialog.prototype.show = function () {
  this.openStep("upload");
  this.$dialog.show();
  this.displayed = true;
  // TODO: insert placeholder here
};
MediaDialog.prototype.hide = function () {
  this.$dialog.hide();
  this.displayed = false;
  // TODO: remove placeholders here
};
MediaDialog.prototype.handleUploadResponse = function (response) {
  var result = $.parseJSON(response);
  if (result.status === "error") {
    oer.status_message.error(result.message);
    this.openStep("upload");
  } else if (result.type === "image") {
    this.openStep("image", result);
  } else if (result.type === "document") {
    this.openStep("document", result);
  } else if (result.type === "video") {
    this.openStep("video", result);
  } else if (result.type === "link") {
    this.tool.insertLink(result.url, result.name, "download");
    this.hide();
  }
};

MediaDialog.Step = function (dialog) {
  this.dialog = dialog;
  this.$step = null;
};
MediaDialog.Step.prototype.open = function (data) {
  this.prepare(data);
  this.dialog.$steps.not(this.$step).hide();
  this.$step.show();
};
//noinspection JSUnusedLocalSymbols
MediaDialog.Step.prototype.prepare = function (data) {
};

MediaDialog.UploadProgressStep = function (dialog) {
  MediaDialog.Step.call(this, dialog);
  this.$step = dialog.$steps.filter(".upload-progress");
  this.$filename = this.$step.find(".filename");
  this.$fill = this.$step.find(".fill");
  this.$legend = this.$step.find(".legend");
};
//noinspection JSCheckFunctionSignatures
MediaDialog.UploadProgressStep.prototype = new MediaDialog.Step();
MediaDialog.UploadProgressStep.prototype.constructor = MediaDialog.UploadProgressStep;
MediaDialog.UploadProgressStep.prototype.prepare = function (data) {
  this.$filename.text(data.name);
  this.$fill.css({width: "0%"});
  this.$legend.text("0%");
  oer.status_message.clear();
};
MediaDialog.UploadProgressStep.prototype.displayProgress = function (percent) {
  percent = percent + "%";
  this.$fill.css({width: percent});
  this.$legend.text(percent);
};

MediaDialog.UploadStep = function (dialog, uploadProgress) {
  MediaDialog.Step.call(this, dialog);
  var $step = this.$step = this.dialog.$steps.filter(".upload");
  var $input = this.$input = $step.find("input:text");
  this.uploadProgress = uploadProgress;

  $step.find("a.submit").click(function (e) {
    e.preventDefault();
    oer.status_message.clear();
    $step.block();
    $.post($step.data("url"), {url: $input.val()}, function (response) {
      dialog.handleUploadResponse(response);
      $step.unblock();
    }, "text");
  });

  var $dropZone = $step.find("div.drop-zone");

  $("#fileupload").fileupload({
    url: $step.data("url"),
    dropZone: $dropZone,
    formData: [
      {name: "fakefile_file", value: "authoring_tool_test_image"}
    ]
  });
  $dropZone.bind("fileuploadsend", function (e, data) {
    dialog.openStep("uploadProgress", {
      name: data.files[0].name
    });
  });
  $dropZone.bind("fileuploadprogress", function (e, data) {
    var percent = parseInt(data.loaded / data.total * 100, 10);
    uploadProgress.displayProgress(percent);
  });
  $dropZone.bind("fileuploaddone", function (e, data) {
    dialog.handleUploadResponse(data.result);
  });
};
//noinspection JSCheckFunctionSignatures
MediaDialog.UploadStep.prototype = new MediaDialog.Step();
MediaDialog.UploadStep.prototype.constructor = MediaDialog.UploadStep;
//noinspection JSUnusedLocalSymbols
MediaDialog.UploadStep.prototype.prepare = function (data) {
  this.$input.val("");
};

MediaDialog.ImageStep = function (dialog) {
  MediaDialog.Step.call(this, dialog);
  var $step = this.$step = dialog.$steps.filter(".image");

  this.$imageCt = $step.find("div.left");
  var $input = this.$input = $step.find("input:text");
  var $textarea = this.$textarea = $step.find("textarea");
  this.figureType = "embed";
  this.imageURL = null;
  this.originalURL = null;

  var tool = dialog.tool;
  var step = this;

  var $selector = this.$selector = $step.find("div.head a");
  var $selectorOptions = this.$selectorOptions = $step.find("div.head ul li");
  $selector.click(function (e) {
    e.preventDefault();
    $selectorOptions.parent().toggleClass("opened");
    $selector.toggleClass("opened");
  });
  $selectorOptions.click(function () {
    var $this = $(this);
    if ($this.hasClass("selected")) {
      return;
    }
    step.figureType = $this.attr("class");
    $selectorOptions.filter(".selected").removeClass("selected");
    $this.addClass("selected");
    $selectorOptions.parent().removeClass("opened");
    $selector.removeClass("opened");
    $selector.text($this.text());
  });
  $step.find("a.submit").click(function (e) {
    e.preventDefault();
    var description = $.trim($textarea.val());
    var title = $.trim($input.val());

    oer.status_message.clear();

    if (step.figureType === "download" && title === "") {
      oer.status_message.error("Please specify the title of this image");
      return;
    }

    var $figure;

    if (step.figureType == "download") {
      //noinspection JSUnusedAssignment
      $figure = $("<figure></figure>").addClass("download").append(
              $("<a target='_blank'></a>").attr("href", step.originalURL).addClass("download").text("Download: ").append(
                      $("<strong></strong>").text(title)
              )
      );
    } else {
      if (description !== "") {
        title += ": ";
      }
      var $caption = $("<figcaption></figcaption>").text(description);
      if (title) {
        $caption.prepend($("<strong></strong>").text(title));
      }
      $figure = $("<figure></figure>").addClass("image").append($("<img>").attr("src", step.imageURL)).append($caption);
    }

    tool.saveState();
    if (tool.$focusBlock) {
      $figure.insertAfter(tool.$focusBlock);
    } else {
      tool.$area.append($figure);
    }
    tool.initFigure($figure);
    tool.ensureTextInput();
    dialog.hide();
  });

};
//noinspection JSCheckFunctionSignatures
MediaDialog.ImageStep.prototype = new MediaDialog.Step();
MediaDialog.ImageStep.prototype.constructor = MediaDialog.ImageStep;
MediaDialog.ImageStep.prototype.prepare = function (data) {
  oer.status_message.clear();
  this.$imageCt.empty();
  this.$input.val(data.name);
  this.$textarea.val("");
  //noinspection JSUnresolvedVariable
  var $image = $("<img>").attr("src", data.thumbnail);
  this.imageURL = data.url;
  //noinspection JSUnresolvedVariable
  this.originalURL = data.original_url;
  $image.appendTo(this.$imageCt);
  this.$selectorOptions.first().click();
};

MediaDialog.VideoStep = function (dialog) {
  MediaDialog.Step.call(this, dialog);

  var $step = this.$step = dialog.$steps.filter(".video");
  this.$imageCt = $step.find("div.left");
  var $input = this.$input = $step.find("input:text");
  var $textarea = this.$textarea = $step.find("textarea");

  var tool = dialog.tool;

  $step.find("a.submit").click(function (e) {
    e.preventDefault();
    oer.status_message.clear();
    tool.saveState();

    var description = $.trim($textarea.val());
    var title = $.trim($input.val());
    if (description !== "") {
      title += ": ";
    }
    var $caption = $("<figcaption></figcaption>").text(description);
    if (title) {
      $caption.prepend($("<strong></strong>").text(title));
    }

    var $figure = $('<figure>').addClass("embed video").attr("data-url", $step.data("url")).append($caption);

    if (tool.$focusBlock) {
      $figure.insertAfter(tool.$focusBlock);
    } else {
      tool.$area.append($figure);
    }
    tool.loadEmbed($figure);
    tool.initFigure($figure);
    tool.ensureTextInput();
    dialog.hide();
  });
};
//noinspection JSCheckFunctionSignatures
MediaDialog.VideoStep.prototype = new MediaDialog.Step();
MediaDialog.VideoStep.prototype.constructor = MediaDialog.VideoStep;
MediaDialog.VideoStep.prototype.prepare = function (data) {
  this.$step.data("url", data.url);
  this.$imageCt.empty();
  //noinspection JSUnresolvedVariable
  var $image = $("<img>").attr("src", data.thumbnail);
  $image.appendTo(this.$imageCt);
  this.$input.val(data.title);
  this.$textarea.val("");
};

MediaDialog.DocumentStep = function (dialog) {
  MediaDialog.Step.call(this, dialog);

  var $step = this.$step = dialog.$steps.filter(".document");
  var $input = this.$input = $step.find("input:text");
  var $selector = this.$selector = $step.find("input:radio");

  var tool = dialog.tool;

  $step.find("a.submit").click(function (e) {
    e.preventDefault();
    oer.status_message.clear();

    var type = $selector.val();
    var caption = $.trim($input.val());
    if (caption === "") {
      oer.status_message.error("Please enter the title of this document.");
      return;
    }
    tool.saveState();
    var $figure = $("<figure></figure>").addClass("download").text("Download: ");
    $figure.append($('<a target="_blank"></a>').attr("href", $step.data("url")).append("<strong></strong>").text(caption));
    if (type === "link") {
      if (tool.$focusBlock && tool.range) {
        if (this.$focusBlock.is("p")) {
          tool.range.collapse(false);
          tool.range.insertNode($figure.get(0));
          tool.trackSelection();
        } else {
          $("<p></p>").append($figure).insertAfter(this.$focusBlock);
        }
      } else {
        $("<p></p>").append($figure).appendTo(tool.$area);
      }
    } else {
      if (tool.$focusBlock) {
        $figure.insertAfter(tool.$focusBlock);
      } else {
        tool.$area.append($figure);
      }
    }
    tool.initFigure($figure);
    tool.ensureTextInput();
    dialog.hide();
  });
};
//noinspection JSCheckFunctionSignatures
MediaDialog.DocumentStep.prototype = new MediaDialog.Step();
MediaDialog.DocumentStep.prototype.constructor = MediaDialog.DocumentStep;
MediaDialog.DocumentStep.prototype.prepare = function (data) {
  this.$selector.val("button");
  this.$input.val(data.name);
};
