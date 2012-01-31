$.blockUI.defaults.css = {
  color: "#fff",
  fontSize: "20px"
};
$.blockUI.defaults.message = "Please wait...";

oer.authoring = {};

var AuthoringTool = function () {
  var tool = this;

  this.ALLOWED_TOP_LEVEL_TAGS = "p,div,h1,h2,h3,h4,ul,ol,blockquote,table,figure";
  this.TOP_LEVEL_TEXT_TAGS = "p,div,h1,h2,h3,h4,ul,ol,blockquote";
  this.ALLOWED_CLASSES = ["embed", "image", "video", "document", "download", "button"];
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

  this.$form = $("#authoring-form");
  this.$editor = $("#editor");
  this.$toolbar = this.$editor.find(".toolbar");
  this.$area = this.$editor.find(".editor-area");
  this.$outline = $("#outline");
  this.$textStyleIndicator = this.$toolbar.find(".text-style > a span");

  this.selection = null;
  this.range = null;
  this.$anchorNode = null; // Element at the beginning of text selection
  this.$anchorBlock = null; // Top level element at the beginning of text selection
  this.$focusNode = null; // Element at the end of text selection
  this.$focusBlock = null; // Top level element at the end of text selection

  this.shouldSaveState = true; // Flag to define if we should save current state in undo history

  this.$area.find("figure").attr("contenteditable", "false");

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
  this.initListButtons();
  this.initLinkUI();
  this.initOutline();

  new MediaDialog(this);

  this.$area.find("figure").each(function () {
    tool.initFigure($(this));
  });
  this.$area.find("figure.embed").each(function () {
    tool.loadEmbed($(this));
  });
  this.$area.find("h2,h3").each(function () {
    tool.initDND($(this));
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

  // Update selected nodes when user is about to click on toolbar button.
  this.$toolbar.mousedown(function () {
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

  // Save, Cancel, Done actions
  (function () {
    var $input = $("#id_text");
    var $preview = tool.$editor.find("div.preview");
    var $actions = $("div.actions a");
    $actions.click(function (e) {
      e.preventDefault();
      var $this = $(this);
      var href = $this.attr("href");
      switch (href) {
        case "#save":
          tool.cleanHTML();
          $input.val(tool.$area.html());
          oer.status_message.clear();
          $.post(tool.$form.attr("action"), tool.$form.serialize(), function (response) {
            if (response.status === "success") {
              oer.status_message.success(response.message, true);
            } else {
              oer.status_message.success(response.message, false);
            }
          });
          break;
        case "#preview":
          $preview.html(tool.$area.html());
          tool.$toolbar.hide();
          tool.$area.hide();
          $preview.show();
          $actions.filter(".edit").removeClass("hidden");
          $this.addClass("hidden");
          break;
        case "#edit":
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
};

AuthoringTool.prototype.cleanHTML = function () {
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

// Ensure that we always have a text block at the end of editor area
AuthoringTool.prototype.ensureTextInput = function () {
  var $area = this.$area;
  if (!$area.children().last().is(this.TOP_LEVEL_TEXT_TAGS)) {
    var $p = $("<p><br/></p>").appendTo($area);
    if ($area.children().length == 1) {
      this.focusOnNode($p);
    }
  }
};

AuthoringTool.prototype.execCommand = function (command) {
  if (arguments.length == 2) {
    document.execCommand(command, false, arguments[1]);
  } else {
    document.execCommand(command, false, null);
  }
};

AuthoringTool.prototype.focusOnNode = function ($node) {
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
};

AuthoringTool.prototype.trackSelection = function () {
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
      $anchorBlock = $anchorNode.parentsUntil(this.$area).slice(0, 1);
    }
  } else {
    $anchorNode = null;
  }

  if ($focusNode.length && !$focusNode.is(this.$area) && $focusNode.closest(this.$area).length) {
    if ($focusNode.parent().is(this.$area)) {
      $focusBlock = $focusNode;
    } else {
      $focusBlock = $focusNode.parentsUntil(this.$area).slice(0, 1);
    }
  } else {
    $focusNode = null;
  }

  this.$anchorNode = $anchorNode;
  this.$anchorBlock = $anchorBlock;
  this.$focusNode = $focusNode;
  this.$focusBlock = $focusBlock;

  // Update text style menu
  if ($focusBlock) {
    this.updateTextStyleIndicator($focusBlock.get(0).tagName.toLowerCase());
  }
};

AuthoringTool.prototype.changeBlockType = function (newType) {
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
  this.updateTextStyleIndicator(newType);
  if ($newBlock.is("h2,h3")) {
    this.initDND($newBlock);
  }
};

AuthoringTool.prototype.updateTextStyleIndicator = function (tag) {
  if (tag == "h2") {
    this.$textStyleIndicator.text("Header");
  } else if (tag == "h3") {
    this.$textStyleIndicator.text("Sub-Header");
  } else if (tag == "blockquote") {
    this.$textStyleIndicator.text("Long Quote");
  } else if (tag == "p" || tag == "div") {
    this.$textStyleIndicator.text("Paragraph");
  } else {
    this.$textStyleIndicator.text("Text style...");
  }
};

AuthoringTool.prototype.insertList = function (listType) {
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

AuthoringTool.prototype.initUndoButtons = function () {
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

AuthoringTool.prototype.initTextStyleMenu = function () {
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

AuthoringTool.prototype.initFormattingButtons = function () {
  var tool = this;
  this.$toolbar.find("a.button.bold").click(function (e) {
    e.preventDefault();
    tool.saveState();
    tool.execCommand("bold");
  });
  this.$toolbar.find("a.button.italic").click(function (e) {
    e.preventDefault();
    tool.saveState();
    tool.execCommand("italic");
  });
  this.$toolbar.find("a.button.underline").click(function (e) {
    e.preventDefault();
    tool.saveState();
    tool.execCommand("underline");
  });
};

AuthoringTool.prototype.initListButtons = function () {
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

AuthoringTool.prototype.insertLink = function () {
  var args = {};
  if (arguments.length) {
    args = arguments[0]
  }

  this.saveState();
  this.execCommand("createLink", "#new-link");
  var $link = this.$area.find("a[href='#new-link']");
  var new_ = true;
  if (args.url) {
    $link.attr("href", args.url);
    new_ = false;
  } else {
    $link.attr("href", "http://");
  }
  if (args.text) {
    $link.html(args.text);
  } else {
    $link.text("Link");
  }
  if (args["class"]) {
    $link.addClass(args["class"]);
  }
  if (args["container"]) {
    $link.detach().appendTo(args["container"])
  }
  if (new_) {
    $link.data("new", true);
    $link.click();
  }
};

AuthoringTool.prototype.initLinkUI = function () {
  var tool = this;

  this.$toolbar.find("a.button.link").click(function (e) {
    e.preventDefault();
    if (tool.$focusNode.is("a") || tool.$focusNode.parentsUntil(tool.$area, "a").length) {
      // We are inside <a> element. Do nothing.
      return;
    }
    tool.insertLink();
  });

  var $dialog = $("#edit-link-dialog");
  var $input = $dialog.find("input[name='url']");

  $dialog.delegate("a", "click", function (e) {
    // TODO: use form with URL validation here.
    e.preventDefault();
    var href = $(e.target).attr("href");
    var $link = $dialog.data("link");
    switch (href) {
      case "#save":
        if (!$link.data("new")) {
          tool.saveState();
        }
        $dialog.data("link").attr("href", $input.val());
        $link.data("new", false);
        break;
      case "#remove":
        tool.saveState();
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
    $dialog.hide();
  });

  this.$area.delegate("a", "click", function (e) {
    e.preventDefault();
    var $link = $(e.currentTarget);
    if ($link.hasClass("download")) {
      return;
    }
    $dialog.data("link", $link);
    $input.val($link.attr("href"));
    var offset = $link.offset();
    $dialog.css({
      left: offset.left + 10 + "px",
      top: offset.top + 16 + "px"
    });
    $dialog.show();
    $input.focus();
  });
};

AuthoringTool.prototype.initFigure = function ($figure) {
  $figure.attr("contenteditable", "false");

  if (!$figure.hasClass("inline")) {
    this.initDND($figure);
    this.initDND($figure);
  }
};

AuthoringTool.prototype.initDND = function ($block) {
  // TODO: картинки склеиваются при перетаскивании
  if (!$block.draggable("option", "disabled")) {
    console.log("Draggabled already enabled for", $block);
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

AuthoringTool.prototype.loadEmbed = function ($figure) {
  var url = $figure.data("url");
  $figure.hide();
  if (url) {
    $.post(this.$area.data("load-embed-url"), {url: url}, function (response) {
      var $caption = $figure.find("figcaption").detach();
      $figure.html(response.html).append($caption).fadeIn();
    });
  }
};

AuthoringTool.prototype.newOutlineItemMessage = function (level) {
  var text = "click to add new ";
  if (level == 0) {
    text += "header";
  } else if (level == 1) {
    text += "sub-header";
  }
  return "<span>" + text + "</span>";
};

AuthoringTool.prototype.updateOutline = function () {
  var tool = this;
  var prevLevel = 0;
  var $list = $("<ul></ul>").data("level", 0);
  var levels = [];
  this.$area.find("h2,h3").each(function () {
    var level = tool.HEADER_LEVELS[this.tagName.toLowerCase()];
    if (level > prevLevel) {
      //noinspection JSDuplicatedDeclaration
      for (var i = 0; i < (level - prevLevel); i++) {
        $list = $("<ul></ul>").data("level", level).appendTo($list);
      }
    } else if (level < prevLevel) {
      //noinspection JSDuplicatedDeclaration
      for (var i = 0; i < (prevLevel - level); i++) {
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
    return $(this).next("ul").length == 0;
  });
  $list.after(function () {
    var level = $(this).parent().data("level") + 1;
    return $("<ul></ul>").data("level", level).append($("<li></li>").addClass("new").html(tool.newOutlineItemMessage(level)));
  });

  this.$outline.data("levels", levels);
  this.$outline.children("ul").remove();
  this.$outline.append($list);
};

AuthoringTool.prototype.initOutline = function () {
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
        if (level == 0) {
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
        tool.initDND($header);
      }
    });
    $input.blur(reset).focus();
  });

};

AuthoringTool.prototype.removeSelectionMarkers = function () {
  this.$area.find("span.rangySelectionBoundary").remove();
};

AuthoringTool.prototype.saveState = function () {
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

AuthoringTool.prototype.undo = function () {
  var historyLength = this.undoHistory.length;
  if (this.undoDisabled || this.undoDepth >= historyLength) {
    return;
  }
  if (this.undoDepth == 0) {
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
};

AuthoringTool.prototype.redo = function () {
  var historyLength = this.undoHistory.length;
  if (this.redoDisabled || this.undoDepth == 0) {
    return;
  }
  this.undoDepth -= 1;
  var undoStep = null;
  if (this.undoDepth == 0 && this.lastState) {
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
  if (this.undoDepth == 0) {
    this.disableRedo();
  }
  this.enableUndo();
  this.updateOutline();
};

AuthoringTool.prototype.disableUndo = function () {
  this.disableButton("undo");
  this.undoDisabled = true;
};

AuthoringTool.prototype.enableUndo = function () {
  this.enableButton("undo");
  this.undoDisabled = false;
};

AuthoringTool.prototype.disableRedo = function () {
  this.disableButton("redo");
  this.redoDisabled = true;
};

AuthoringTool.prototype.enableRedo = function () {
  this.enableButton("redo");
  this.redoDisabled = false;
};

AuthoringTool.prototype.disableButton = function (button) {
  this.$toolbar.find("." + button).addClass("disabled");
};

AuthoringTool.prototype.enableButton = function (button) {
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
  this.$filename.text(data["name"]);
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

  var step = this;

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

  $dropZone.fileupload({
    url: $step.data("url"),
    dropZone: $dropZone,
    paramName: "file",
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

  var $imageCt = this.$imageCt = $step.find("div.left");
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

    var $figure = null;

    if (step.figureType == "download") {
      $figure = $("<figure></figure>").addClass("download").append(
              $("<a target='_blank'></a>").attr("href", step.originalURL).addClass("download").text("Download: ").append(
                      $("<strong></strong>").text(title)
              )
      );
    } else {
      if (description !== "") {
        title += ": "
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
  var $image = $("<img>").attr("src", data["thumbnail"]);
  this.imageURL = data["url"];
  this.originalURL = data["original_url"];
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
      title += ": "
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
  var $image = $("<img>").attr("src", data["thumbnail"]);
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
          tool.range.collapse();
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
