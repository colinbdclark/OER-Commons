// TODO: move these defaults elsewhere
$.blockUI.defaults.css = {
  color: "#fff",
  fontSize: "20px"
};
$.blockUI.defaults.message = "Please wait...";

jQuery.fn.outerHTML = function (s) {
  return (s) ? this.before(s).remove() : jQuery("<p></p>").append(this.eq(0).clone()).html();
};

var WriteStep = function (tool) {
  this.tool = tool;
  var editor = this;

  this.ALLOWED_TOP_LEVEL_TAGS = "p,div,h1,h2,h3,h4,ul,ol,blockquote,table,figure";
  this.TOP_LEVEL_TEXT_TAGS = "p,div,h1,h2,h3,h4,ul,ol,blockquote";
  this.ALLOWED_CLASSES = ["table", "embed", "image", "video", "document", "download", "reference", "button", "l1", "l2", "l3", "l4", "l5", "rangySelectionBoundary"];
  for (var i = 1; i < 6; i++) {
    this.ALLOWED_CLASSES.push("text-color-" + i);
    this.ALLOWED_CLASSES.push("bg-color-" + i);
  }

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

  this.$toolbar = $("#write-toolbar");
  this.$toolbarButtons = this.$toolbar.find("a.toolbar-button");
  this.$area = $("#editor-area");
  this.$textStyleIndicator = this.$toolbar.find(".text-style > a span");
  this.$footnotes = $("#footnotes");

  this.selection = null;
  this.range = null;
  this.$anchorNode = null; // Element at the beginning of text selection
  this.$anchorBlock = null; // Top level element at the beginning of text selection
  this.$focusNode = null; // Element at the end of text selection
  this.$focusBlock = null; // Top level element at the end of text selection

  this.shouldSaveState = true; // Flag to define if we should save current state in undo history

  this.$area.html(editor.cleanHTML(false));
  this.ensureTextInput();

  // Track when user presses and releases Ctrl or Cmd or Shift keys
  var $document = $(document);
  $document.keydown(function (e) {
    if ((e.ctrlKey || e.metaKey)) {
      if (e.which == 90) {
        // Ctrl/Cmd + Z: Undo
        editor.undo();
        e.preventDefault();
      } else if (e.which == 89) {
        // Ctrl/Cmd + Y: Redo
        editor.redo();
        e.preventDefault();
      } else if (e.which == 83) {
        // Ctrl/Cmd + S: Save
        editor.tool.save();
        e.preventDefault();
      }
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
  this.initTableButton();
  this.initColorButtons();
  this.initReferences();

  this.toc = new TableOfContents(this);
  new MediaDialog(this);


  this.$area.find("table").each(function() {
    editor.initTable($(this));
  });
  this.$area.find("figure:not(.table)").each(function () {
    editor.initFigure($(this));
  });
  this.$area.find("figure.embed").each(function () {
    editor.loadEmbed($(this));
  });
  this.$area.find("figure.image").each(function () {
    editor.initImage($(this));
  });
  this.initImageControls();

  this.initDND();

  // Clean up HTML on paste
  this.$area.bind("paste", function () {
    editor.saveState();
    setTimeout(function () {
      var selection = null;
      if ("saveSelection" in rangy) {
        editor.removeSelectionMarkers();
        selection = rangy.saveSelection();
      }
      editor.$area.html(editor.cleanHTML(false));
      if (selection) {
        rangy.restoreSelection(selection);
        rangy.removeMarkers(selection);
      }
      // Re-init DND
      editor.updateDND();
    }, 200);
  });

  // Track selection when user releases the mouse button.
  $document.mouseup(function () {
    editor.trackSelection();
  });

  // Track editor changes caused by pressing keys.
  editor.$area.keyup(function (e) {

    if ($.inArray(e.which, editor.SPECIAL_KEY_CODES) != -1) {
      return;
    }

    // Update the focused nodes if user moves the caret.
    if ($.inArray(e.which, editor.NAVIGATION_KEYS) != -1 || $.inArray(e.which, [editor.ENTER, editor.BACKSPACE, editor.DELETE]) != -1) {
      editor.trackSelection();
      if (e.which == editor.ENTER) {
        // If user presses Enter when he's inside a paragraph with styled text,
        // it adds a new paragraph with the same styling. This is not desired, so
        // we have to remove the formatting tags from new paragraph.
        if (editor.$focusBlock && editor.$focusBlock.is("p,div") && $.trim(editor.$focusBlock.text()) === "" && !editor.$focusNode.is(editor.$focusBlock)) {
          editor.$focusBlock.html("<br>");
          editor.focusOnNode(editor.$focusBlock);
        }
      }
      if ($.inArray(e.which, [editor.BACKSPACE, editor.DELETE]) == -1) {
        return;
      }
    }

    // Update the table of contents if current block is a header
    if (editor.$focusBlock && editor.$focusBlock.is("h1,h2,h3")) {
      var $header = editor.$focusBlock;
      var $tocHeader = $header.data("toc");
      if (!$tocHeader) {
        editor.toc.update();
        $tocHeader = $header.data("toc");
      }
      $tocHeader.find("div.text").text($header.text());
    }

  });

  var keydownTimeout = null;
  editor.$area.keydown(function (e) {
    var $button;
    if (e.ctrlKey || e.metaKey) {
      if (e.shiftKey) {
        if (e.which == 49) {
          // Ctrl/Cmd + Shift + 1: Heading
          editor.changeBlockType("h2");
        } else if (e.which == 50) {
          // Ctrl/Cmd + Shift + 2: Sub-Heading
          editor.changeBlockType("h3");
        } else if (e.which == 51) {
          // Ctrl/Cmd + Shift + 3: Paragraph
          editor.changeBlockType("p");
        } else if (e.which == 52) {
          // Ctrl/Cmd + Shift + 4: Bullet list
          editor.insertList("ul");
        } else if (e.which == 53) {
          // Ctrl/Cmd + Shift + 5: Number list
          editor.insertList("ol");
        }
      } else if (e.which == 66) { // bold
        $button = editor.$toolbarButtons.filter(".bold");
        if (!$button.hasClass("disabled")) {
          $button.click();
          e.preventDefault();
        }
      } else if (e.which == 73) { // italic
        $button = editor.$toolbarButtons.filter(".italic");
        if (!$button.hasClass("disabled")) {
          $button.click();
          e.preventDefault();
        }
      } else if (e.which == 85) { // underline
        $button = editor.$toolbarButtons.filter(".underline");
        if (!$button.hasClass("disabled")) {
          $button.click();
          e.preventDefault();
        }
      } else if (e.which == 75) {
        // Ctrl/Cmd + K: Link
        $button = editor.$toolbarButtons.filter(".link");
        if (!$button.hasClass("disabled")) {
          $button.click();
          e.preventDefault();
        }
      } else if (e.which == 219) {
        // Ctrl/Cmd + [: Decrease indent
        $button = editor.$toolbarButtons.filter(".outdent");
        if (!$button.hasClass("disabled")) {
          $button.click();
          e.preventDefault();
        }
      } else if (e.which == 221) {
        // Ctrl/Cmd + ]: Increase indent
        $button = editor.$toolbarButtons.filter(".indent");
        if (!$button.hasClass("disabled")) {
          $button.click();
          e.preventDefault();
        }
      }
      return;
    }

    // TAB key inside table cell move the focus the the next cell
    if (e.which === 9) {
      var $cell = editor.$focusNode.closest("td", editor.$area);
      if ($cell.length) {
        var $table = $cell.closest("table", editor.$area);
        var $cells = $table.find("tr").not(".ui-column-controls").find("td").not(".ui-row-controls");
        var idx = $cells.index($cell);
        if (idx !== -1) {
          if (idx < $cells.length - 1) {
            editor.focusOnNode($cells.eq(idx + 1));
            e.preventDefault();
            return;
          }
        }
      }
    }

    if ($.inArray(e.which, editor.SPECIAL_KEY_CODES) != -1 || $.inArray(e.which, editor.NAVIGATION_KEYS) != -1) {
      return;
    }
    // User is about to type something. Save current state.

    editor.saveState();
    editor.shouldSaveState = false;
    if (keydownTimeout) {
      clearTimeout(keydownTimeout);
    }
    keydownTimeout = setTimeout(function () {
      editor.shouldSaveState = true;
      keydownTimeout = null;
    }, 1000);
  });

  editor.$area.keyup(function (e) {
    if (e.which == editor.DELETE || e.which == editor.BACKSPACE) {
      editor.ensureTextInput();
    }
  });

};

WriteStep.prototype.cleanHTML = function (preSave) {
  var editor = this;
  var $area = this.$area;

  // Create a document and clear HTML comments
  var $document = $("<div></div>").html($area.html().replace(/<!--[\s\S]*?-->/g, ""));

  // Remove non-safe elements (scripts, styles, forms, inputs)
  $document.find("script,style,form,input,textarea,button").remove();

  // Unwrap <font>, <o:p> (comes from MS Word) and other crap
  $document.find("font,p[class^='Mso'],o\\:p").replaceWith(function () {
    return $(this).contents();
  });

  // Remove all 'styles' attributes
  $document.find("[style]").removeAttr("style");

  // Remove not allowed classes
  $document.find("[class]").each(function() {
    var $this = $(this);
    if ($this.closest("[class^='ui-']", $area).length) {
      return;
    }
    $this.removeClass(function (i, oldClasses) {
      oldClasses = oldClasses.split(" ");
      oldClasses.sort();
      var remove = [];
      for (i = 0; i < oldClasses.length; i++) {
        var cls = oldClasses[i];
        if ($.inArray(cls, editor.ALLOWED_CLASSES) === -1) {
          remove.push(cls);
        }
      }
      return remove.join(" ");
    });
  });

  // Remove class attribute from elements with empty class
  $document.find("[class='']").removeAttr("class");

  // Unwrap <span> without class
  $document.find("span:not([class])").replaceWith(function () {
    return $(this).contents();
  });

  // Remove all iframes, objects, embeds which are not inside <figure class="embed">
  $document.find("iframe,object,embed,param").each(function () {
    var $this = $(this);
    if ($this.closest("figure.embed", $area).length === 0) {
      $this.remove();
    }
  });

  // Remove/unwrap empty figures
  $document.find("figure").each(function() {
    var $figure = $(this);
    // Skip valid figures
    if ($figure.hasClass("table") && $figure.find("table").length) {
      return;
    }
    if ($figure.hasClass("embed") && $figure.data("url")) {
      return;
    }
    if ($figure.hasClass("image") && $figure.find("img")) {
      return;
    }
    if ($figure.hasClass("download") && $figure.find("a")) {
      return;
    }
    // TODO: skip audio figures when they're available

    if ($.trim($figure.text()) === "") {
      // Remove empty figure
      $figure.remove();
    } else if ($figure.hasClass("inline")) {
      // Unwrap inlive figure
      $figure.replaceWith(function() {
        return $(this).contents();
      })
    } else {
      // Replace block figure with <p>
      $figure.replaceWith(function() {
        return $("<p></p>").html($(this).html());
      })
    }
  });

  // Replace all <div>s with <p>s
  $document.find("div").replaceWith(function () {
    return $("<p></p>").html($(this).html());
  });

  // Unwrap nested <p>s
  $document.find("p > p").each(function () {
    var $parent = $(this).parent("p", $area);
    $parent.replaceWith(function () {
      return $(this).contents();
    });
  });

  // Wrap all top-level non-block elements in <p>s (including non-empty text nodes)
  $document.contents().not(this.ALLOWED_TOP_LEVEL_TAGS).filter(
          function () {
            if (this.nodeType === 3 && $.trim(this.text) !== "") {
              // Non-empty text node
              return true;
            }
            return this.tagName !== "p";
          }).wrap("<p></p>");

  // Remove empty paragraphs
  $document.html($document.html().replace(/<p[^>]*?>\s*?<\/\s*p>/gi, ""));

  // Replace <h1> with <h2> since this should be a top level header
  $document.find("h1").replaceWith(function () {
    return $("<h2></h2>").html($(this).html());
  });

  if (preSave) {
    $document.find("[class^='ui-wrap-']").replaceWith(function () {
      return $(this).contents();
    });
    $document.find("[class^='ui-']").remove();
    $document.find("[contenteditable]").removeAttr("contenteditable");
    $document.find("p,div").each(function () {
      var $this = $(this);
      if ($.trim($this.text()) === "") {
        $this.remove();
      }
    });
  }
  return $document.html();
};

WriteStep.prototype.preSave = function () {
  $("#id_text").val(this.cleanHTML(true));
};

// Ensure that we always have a text block at the end of editor area
// We also need to insert empty paragraphs around all figures
WriteStep.prototype.ensureTextInput = function () {
  var $area = this.$area;
  if (!$area.children().last().is(this.TOP_LEVEL_TEXT_TAGS)) {
    var $p = $("<p><br></p>").data("auto", true).appendTo($area);
    if ($area.children().length == 1) {
      this.focusOnNode($p);
    }
  }
  $area.find("figure:not(.inline)").each(function () {
    var $figure = $(this);
    if (!$figure.prev().is("p,div")) {
      $("<p><br></p>").data("auto", true).insertBefore($figure);
    }
    if (!$figure.next().is("p,div")) {
      $("<p><br></p>").text(" ").data("auto", true).insertBefore($figure);
    }
  });
  // Remove duplicate empty paragraphs
  $area.find("p + p").each(function () {
    var $p = $(this);
    if ($p.data("auto") && $.trim($p.text()) === "") {
      $p.remove();
    }
  });
};

WriteStep.prototype.execCommand = function (command) {
  if (arguments.length == 2) {
    document.execCommand(command, false, arguments[1]);
  } else {
    document.execCommand(command, false, null);
  }
};

WriteStep.prototype.focusOnNode = function ($node) {
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

WriteStep.prototype.trackSelection = function () {

  // Rangy is not initialized?
  if (!("getSelection" in rangy)) {
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

WriteStep.prototype.changeBlockType = function (newType) {
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

WriteStep.prototype.activateButton = function (button) {
  this.$toolbarButtons.filter("." + button).addClass("active");
};

WriteStep.prototype.updateToolbarState = function () {
  var $anchorNode = this.$anchorNode;
  var $anchorBlock = this.$anchorBlock;
  var $focusNode = this.$focusNode;
  var $focusBlock = this.$focusBlock;

  this.$toolbar.find("a.active:not(.media)").removeClass("active");
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

  var indentLevel = this.getIndentLevel($focusBlock);
  if ($focusBlock.is("h2")) {
    this.$textStyleIndicator.text("Header");
  } else if ($focusBlock.is("h3")) {
    this.$textStyleIndicator.text("Sub-Header");
  } else if ($focusBlock.is("blockquote")) {
    this.$textStyleIndicator.text("Long Quote");
    if (indentLevel < 5) {
      this.enableButton("indent");
    }
    this.enableButton("outdent");
  } else if ($focusBlock.is("p,div")) {
    this.$textStyleIndicator.text("Paragraph");
    if (indentLevel < 5) {
      this.enableButton("indent");
    }
    if (indentLevel) {
      this.enableButton("outdent");
    }
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

WriteStep.prototype.insertList = function (listType) {
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

WriteStep.prototype.initUndoButtons = function () {
  var editor = this;
  this.$toolbarButtons.filter(".undo").click(function (e) {
    e.preventDefault();
    editor.undo();
  });
  this.$toolbarButtons.filter(".redo").click(function (e) {
    e.preventDefault();
    editor.redo();
  });
};

WriteStep.prototype.initTextStyleMenu = function () {
  var editor = this;
  var $menu = this.$toolbar.find("div.text-style");
  $menu.find("a.select").click(function (e) {
    e.preventDefault();
    e.stopPropagation();
    if ($menu.hasClass("active")) {
      $menu.removeClass("active");
      $menu.find("a[data-tooltip]").qtip("enable");
    } else {
      $menu.addClass("active");
      $menu.find("a[data-tooltip]").qtip("hide").qtip("disable");
    }
  });
  $(document).click(function () {
    $menu.removeClass("active");
    $menu.find("a[data-tooltip]").qtip("enable");
  });
  $menu.delegate("ul a", "click", function (e) {
    e.preventDefault();
    var $target = $(this);
    var href = $target.attr("href");
    switch (href) {
      case "#header":
        editor.changeBlockType("h2");
        break;
      case "#sub-header":
        editor.changeBlockType("h3");
        break;
      case "#paragraph":
        editor.changeBlockType("p");
        break;
      case "#quote":
        editor.changeBlockType("blockquote");
        break;
      default:
        break;
    }
  });
};

WriteStep.prototype.initFormattingButtons = function () {
  var editor = this;
  this.$toolbarButtons.filter(".bold").click(function (e) {
    e.preventDefault();
    editor.saveState();
    editor.execCommand("bold");
    editor.trackSelection();
  });
  this.$toolbarButtons.filter(".italic").click(function (e) {
    e.preventDefault();
    editor.saveState();
    editor.execCommand("italic");
    editor.trackSelection();
  });
  this.$toolbarButtons.filter(".underline").click(function (e) {
    e.preventDefault();
    editor.saveState();
    editor.execCommand("underline");
    editor.trackSelection();
  });
};

WriteStep.prototype.initListButtons = function () {
  var editor = this;
  this.$toolbarButtons.filter(".bullet-list").click(function (e) {
    e.preventDefault();
    editor.insertList("ul");
  });
  this.$toolbarButtons.filter(".number-list").click(function (e) {
    e.preventDefault();
    editor.insertList("ol");
  });
};

WriteStep.prototype.getIndentLevel = function ($block) {
  var classes = {};
  var classNames = $block.attr("class");
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

WriteStep.prototype.initIndentButtons = function () {
  var editor = this;

  this.$toolbarButtons.filter(".indent").click(function (e) {
    e.preventDefault();
    var $anchorNode = editor.$anchorNode;
    var $anchorBlock = editor.$anchorBlock;
    var $focusBlock = editor.$focusBlock;
    var $focusNode = editor.$focusNode;
    if (!$focusBlock) {
      return;
    }

    if ($focusBlock.is("p,div,blockquote")) {
      var level = editor.getIndentLevel($focusBlock);
      if (level < 5) {
        editor.saveState();
        $focusBlock.removeClass().addClass("l" + (level + 1));
        editor.trackSelection();
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
        editor.saveState();
        var selection = rangy.saveSelection();
        $wrapper.insertBefore($anchorLi).append($indentedLis.detach());
        rangy.restoreSelection(selection);
        editor.trackSelection();
      }
    }
  });

  this.$toolbarButtons.filter(".outdent").click(function (e) {
    e.preventDefault();
    var $anchorNode = editor.$anchorNode;
    var $anchorBlock = editor.$anchorBlock;
    var $focusBlock = editor.$focusBlock;
    var $focusNode = editor.$focusNode;
    if (!$focusBlock) {
      return;
    }
    if ($focusBlock.is("p,div,blockquote")) {
      var level = editor.getIndentLevel($focusBlock);
      if (!level && $focusBlock.is("blockquote")) {
        editor.saveState();
        editor.changeBlockType("p");
        $focusBlock.removeClass();
      } else if (level < 2) {
        editor.saveState();
        $focusBlock.removeClass();
        editor.trackSelection();
      } else {
        editor.saveState();
        $focusBlock.removeClass().addClass("l" + (level - 1));
        editor.trackSelection();
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
        editor.saveState();
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
        editor.trackSelection();
      }
    }
  });
};

WriteStep.prototype.insertLink = function () {
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
  this.trackSelection();
};

WriteStep.prototype.initLinks = function () {
  var editor = this;

  this.$toolbarButtons.filter(".link").click(function (e) {
    e.preventDefault();
    var $link = null;
    if (editor.$focusNode) {
      $link = editor.$focusNode.closest("a", editor.$area);
    }
    if ($link && $link.length) {
      return;
    }
    if (editor.selection && editor.selection.isCollapsed) {
      editor.insertLink({text: ""});
    } else {
      editor.insertLink();
    }
  });

  var $dialog = $("#link-dialog");
  var $form = $dialog.find("form");
  $form.validate({
    rules: {
      "link_text": "required",
      "link_url": {
        required: true,
        url: true
      }
    },
    submitHandler: function() {
      var $link = $dialog.data("link");
      if (!$link.data("new")) {
        editor.saveState();
      }
      $link.text($textInput.val());
      $link.attr("href", $urlInput.val());
      $dialog.hide();
    }
  });
  $form.find("input[type='text']").keydown(function(e) {
    if (e.which === editor.ENTER) {
      e.preventDefault();
      $form.submit();
    }
  });

  var $urlInput = $dialog.find("input[name='link_url']");
  var $textInput = $dialog.find("input[name='link_text']");

  $dialog.find("a.button[href='#cancel']").click(function (e) {
    e.preventDefault();
    var $link = $dialog.data("link");
    if ($link.data("new")) {
      $link.replaceWith(function () {
        return $(this).html();
      });
      editor.trackSelection();
    }
    $dialog.hide();
  });

  $dialog.find("a.button[href='#save']").click(function (e) {
    e.preventDefault();
    $form.submit();
  });

  $dialog.find("a.remove").click(function (e) {
    e.preventDefault();
    var $link = $dialog.data("link");
    if (!$link.data("new")) {
      editor.saveState();
    }
    $link.remove();
    editor.trackSelection();
    $dialog.hide();
  });

  this.$area.delegate("a", "click", function (e) {
    var $link = $(e.currentTarget);
    if ($link.closest("figure.download", editor.$area).length) {
      return;
    }
    if ($link.closest("tr.ui-column-controls,td.ui-row-controls", editor.$area).length) {
      return;
    }
    if ($link.is("[class^='ui-']")) {
      return;
    }
    e.preventDefault();
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
    if ($textInput.val() === "") {
      $textInput.focus();
    } else {
      $urlInput.focus();
    }
  });

};

WriteStep.prototype.initColorButtons = function () {
  var editor = this;
  var $toolbar = this.$toolbar;
  var $selectors = $toolbar.find("div.color-selector");
  $selectors.find("a.toolbar-button").click(function (e) {
    e.preventDefault();
    e.stopPropagation();
    var $this = $(this);
    var $selector = $this.parent();
    if ($selector.hasClass("active")) {
      $selector.removeClass("active");
      $selector.find("a[data-tooltip]").qtip("enable");
    } else {
      var $lis = $selector.find("li").removeClass("selected");
      if (editor.$focusNode) {
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
      }
      $selector.addClass("active");
      $selector.find("a[data-tooltip]").qtip("hide").qtip("disable");
    }
  });
  $selectors.delegate("li", "mousedown", function (e) {
    e.stopPropagation();
    e.preventDefault();
    var $this = $(this);
    var i, applier;
    editor.saveState();

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

    // TODO: initialize and save CssclassAppliers on editor initialization and re-use them here

    var selection = rangy.saveSelection();

    // Remove existing colors
    for (i = 1; i < 6; i++) {
      applier = rangy.createCssClassApplier(prefix + "-color-" + i);
      applier.undoToSelection();
    }
    if (class_.indexOf("-remove") === -1) {
      applier = rangy.createCssClassApplier(class_);
      applier.applyToSelection();
    }

    rangy.restoreSelection(selection);
    editor.trackSelection();

  });

  $(document).click(function () {
    $selectors.removeClass("active");
    $selectors.find("a[data-tooltip]").qtip("enable");
  });
};

WriteStep.prototype.initFigure = function ($figure) {
  $figure.attr("contenteditable", "false");
};

WriteStep.prototype.initDND = function () {
  var editor = this;
  this.$area.sortable({
    handle: this.$area.find("figure:not(.inline):not(.table),table span.move"),
    distance: 15,
    containment: this.$area,
    cursor: "move",
    axis: "y",
    tolerance: "pointer",
    delay: 300,
    update: function () {
      editor.ensureTextInput();
    }
  });
};

WriteStep.prototype.updateDND = function () {
  this.$area.sortable("option", "handle", this.$area.find("figure:not(.inline):not(.table),table span.move"));
};

WriteStep.prototype.initImage = function($figure) {
  var $image = $figure.find("img");
  if (!$image.parent().is("span.ui-wrap-image")) {
    $image.wrap($('<span class="ui-wrap-image"></span>'));
    var $wrapper = $image.parent();
    $('<a href="#" class="ui-move"></a>').appendTo($wrapper);
    $('<a href="#" class="ui-delete"></a>').appendTo($wrapper);
  }
};

WriteStep.prototype.initImageControls = function() {
  var editor = this;
  this.$area.delegate("figure.image a.ui-move", "click", function(e) {
    e.preventDefault();
  });
  this.$area.delegate("figure.image a.ui-delete", "click", function(e) {
    e.preventDefault();
    editor.saveState();
    var $figure = $(e.currentTarget).closest("figure.image", editor.$area);
    $figure.remove();
    // TODO: remove image from server.
  });
};

//WriteStep.prototype.initImageResize = function($img) {
//  $img.load(function()
//    $(this).resizable({
//      aspectRatio: true,
//      autoHide: true,
//      maxWidth: 800,
//      minWidth: 100,
//      create: function() {
//        $(this).css({
//          "margin-left": "auto",
//          "margin-right": "auto"
//        });
//      }
//    });
//  });
//};

WriteStep.prototype.loadEmbed = function ($figure) {
  var url = $figure.data("url");
  $figure.hide();
  if (url) {
    $.post(this.$area.data("load-embed-url"), {url: url}, function (response) {
      var $caption = $figure.find("figcaption").detach();
      $figure.html(response.html).append($caption).fadeIn();
    });
  }
};

WriteStep.prototype.initReferences = function () {
  this.updateReferences();

  var editor = this;
  this.$toolbarButtons.filter(".reference").click(function (e) {
    e.preventDefault();
    var selection = editor.selection;
    if (!selection) {
      return;
    }
    if (!selection.isCollapsed) {
      selection.collapse(false);
      editor.trackSelection();
    }

    editor.saveState();

    editor.execCommand("createLink", "#new-reference");
    var $reference = editor.$area.find("a[href='#new-reference']");
    $reference.addClass("reference");
    $reference.attr("contenteditable", "false");
    $reference.attr("data-text", "");
    $reference.data("new", true);
    editor.updateReferences();
    $reference.click();
  });

  var $dialog = $("#reference-dialog");

  var $form = $dialog.find("form");
  $form.validate({
    rules: {
      "reference_text": "required"
    },
    submitHandler: function() {
      var $reference = $dialog.data("reference");
      var text = $.trim($dialog.find("textarea").val());
      if (text !== $reference.data("text")) {
        if (!$reference.data("new")) {
          editor.saveState();
        }
        $reference.attr("data-text", text);
        $reference.data("text", text);
        editor.updateReferences();
      }
      $reference.data("new", false);
      $dialog.hide();
    }
  });

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
    $form.submit();
  });

  $dialog.find("a.remove").click(function () {
    var $reference = $dialog.data("reference");
    if (!$reference.data("new")) {
      editor.saveState();
    }
    $reference.remove();
    editor.trackSelection();
    editor.updateReferences();
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

  this.$footnotes.delegate("a.ref", "click", function (e) {
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
    if (editor.$area.find("a.reference").length !== editor.$footnotes.children("div.footnote").length) {
      editor.updateReferences();
    }
    setTimeout(trackChanges, 1000);
  }
  setTimeout(trackChanges, 1000);
};

WriteStep.prototype.updateReferences = function () {
  var $footnotes = this.$footnotes.empty();
  this.$area.find("a.reference").each(function (i) {
    var $this = $(this);
    var refCount = i + 1;
    var name = "[" + refCount + "]";
    $this.text(name);
    $this.attr("href", "#footnote-" + refCount);
    $this.attr("id", "ref-" + refCount);
    var $footnote = $("<div></div>").attr("id", "footnote" + refCount).addClass("footnote").
            append($("<a></a>").addClass("ref").attr("href", "#").text(name)).
            append($("<div></div>").text($this.data("text")).linkify());
    $footnote.find("div a").each(function(i, el) {
      $(el).attr("target", "_blank");
    });
    $footnote.data("reference", $this);
    $footnotes.append($footnote);
  });
};

WriteStep.prototype.removeSelectionMarkers = function () {
  this.$area.find("span.rangySelectionBoundary").remove();
};

WriteStep.prototype.saveState = function () {
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

WriteStep.prototype.undo = function () {
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
  this.toc.update();
  this.updateReferences();
  this.trackSelection();

  this.updateDND();

};

WriteStep.prototype.redo = function () {
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
  this.toc.update();
  this.updateReferences();
  this.trackSelection();

  this.updateDND();

};

WriteStep.prototype.disableUndo = function () {
  this.disableButton("undo");
  this.undoDisabled = true;
};

WriteStep.prototype.enableUndo = function () {
  this.enableButton("undo");
  this.undoDisabled = false;
};

WriteStep.prototype.disableRedo = function () {
  this.disableButton("redo");
  this.redoDisabled = true;
};

WriteStep.prototype.enableRedo = function () {
  this.enableButton("redo");
  this.redoDisabled = false;
};

WriteStep.prototype.disableButton = function (button) {
  button = this.$toolbar.find("." + button).addClass("disabled");
  if (button.is("a[data-tooltip]")) {
    button.qtip("disable");
  } else {
    button.find("a[data-tooltip]").qtip("hide").qtip("disable");
  }
};

WriteStep.prototype.enableButton = function (button) {
  button = this.$toolbar.find("." + button).removeClass("disabled");
  if (button.is("a[data-tooltip]")) {
    button.qtip("enable");
  } else {
    button.find("a[data-tooltip]").qtip("enable");
  }
};

WriteStep.prototype.initTableButton = function() {
  var editor = this;
  var $tableTool = this.$toolbar.find("div.table-tool");
  var $rows = $tableTool.find("tr");
  var $cells = $tableTool.find("table a");
  var $rowInput = $tableTool.find("input.rows");
  var $colInput = $tableTool.find("input.cols");
  $tableTool.click(function(e) {
    e.stopPropagation();
  });
  $tableTool.find("a.toolbar-button").click(function(e) {
    e.preventDefault();
    if ($tableTool.hasClass("active")) {
      $tableTool.removeClass("active");
      $tableTool.find("a[data-tooltip]").qtip("enable");
    } else {
      $cells.removeClass("active").removeClass("hover");
      $rowInput.val("");
      $colInput.val("");
      $tableTool.addClass("active");
      $tableTool.find("a[data-tooltip]").qtip("hide").qtip("disable");
    }
  });
  function applyClassToCells(cls, row, col) {
    $rows.slice(0, row).each(function() {
      var $row = $(this);
      $row.find("a").slice(0, col).addClass(cls);
      $row.find("a").slice(col).removeClass(cls);
    });
    $rows.slice(row).find("a").removeClass(cls);
  }
  $cells.mouseover(function() {
    var $cell = $(this);
    applyClassToCells("hover", $cell.data("row"), $cell.data("col"));
  });
  $cells.click(function(e) {
    e.preventDefault();
    var $cell = $(this);
    $rowInput.val($cell.data("row"));
    $colInput.val($cell.data("col"));
    applyClassToCells("active", $cell.data("row"), $cell.data("col"));
  });
  $tableTool.find("table").mouseout(function() {
    $cells.removeClass("hover");
  });
  function getRowsAndCols() {
    var rows = parseInt($rowInput.val());
    var cols = parseInt($colInput.val());
    if (!isNaN(rows) && !isNaN(cols)) {
      return {rows:rows, cols:cols};
    }
    return null;
  }
  $rowInput.add($colInput).keyup(function() {
    var rowsCols = getRowsAndCols();
    if (rowsCols) {
      applyClassToCells("active", rowsCols.rows, rowsCols.cols);
    }
  });
  $(document).click(function() {
    $tableTool.removeClass("active");
    $tableTool.find("a[data-tooltip]").qtip("enable");
  });
  $tableTool.find("div.buttons a.cancel").click(function(e) {
    e.preventDefault();
    $tableTool.removeClass("active");
    $tableTool.find("a[data-tooltip]").qtip("enable");
  });
  $tableTool.find("div.buttons a.add").click(function(e) {
    e.preventDefault();
    var rowsCols = getRowsAndCols();
    if (!rowsCols) {
      return;
    }
    var html = "<table>\n";
    for (var i = 0; i < rowsCols.rows; i++) {
      html += "<tr>\n";
      for (var j = 0; j < rowsCols.cols; j++) {
        html += "<td>&nbsp;\n</td>\n"
      }
      html += "</tr>\n";
    }
    html += "</table>";
    var $table = $(html);
    editor.saveState();
    if (editor.$focusBlock) {
      if (editor.$focusBlock.is("p,div") && $.trim(editor.$focusBlock.text()) === "") {
        editor.$focusBlock.replaceWith($table);
      } else {
        $table.insertAfter(editor.$focusBlock);
      }
    } else {
      $table.appendTo(editor.$area);
    }
    editor.initTable($table);
    editor.updateDND();
    editor.focusOnNode($table.find("td").first());
    $tableTool.removeClass("active");
    $tableTool.find("a[data-tooltip]").qtip("enable");
  });

  editor.$area.delegate("table a.remove", "click", function(e) {
    e.preventDefault();
    var $btn = $(e.currentTarget);
    var $table = $btn.closest("table");
    editor.saveState();
    if ($btn.hasClass("remove-column")) {
      var $cells = $btn.closest("tr").find("td");
      var colIdx = $cells.index($btn.parent());
      $table.find("tr").each(function() {
        $(this).find("td").eq(colIdx).remove();
      });
    } else if ($btn.hasClass("remove-row")) {
      $btn.closest("tr").remove();
    }
    // Remove table if it's empty
    if ($table.find("tr").length < 2 || $table.find("tr").first().find("td").length < 2) {
      if ($table.parent().is("figure")) {
        $table.parent().remove();
      } else {
        $table.remove();
      }
      editor.ensureTextInput();
    }
  });

  editor.$area.delegate("table a.add", "click", function(e) {
    e.preventDefault();
    var $btn = $(e.currentTarget);
    var $table = $btn.closest("table");
    editor.saveState();
    if ($btn.hasClass("add-column")) {
      var $cells = $btn.closest("tr").find("td");
      var colIdx = $cells.index($btn.parent());
      $table.find("tr").each(function(i, row) {
        var $row = $(row);
        var $cell = $row.find("td").eq(1).clone();
        if (i > 0) {
          $cell.html("&nbsp;");
        }
        $cell.insertAfter($row.find("td").eq(colIdx));
      });
    } else if ($btn.hasClass("add-row")) {
      var $row = $table.find("tr").eq(1).clone();
      $row.find("td").slice(1).html("&nbsp;");
      $row.insertAfter($btn.closest("tr"));
    }
  });

};

WriteStep.prototype.initTable = function($table) {
  var i;
  if (!$table.parent().is("figure")) {
    $table.wrap($('<figure></figure>'));
  }
  $table.parent().addClass("table");
  var $firstRow = $table.find("tr").first();
  if (!$firstRow.hasClass("ui-column-controls")) {
    var $controls = $("<tr></tr>").addClass("ui-column-controls");
    var numCols = $firstRow.find("td").length;
    for (i = 0; i < numCols + 1; i++) {
      var $cell = $('<td contenteditable="false"></td>');
      if (i == 0) {
        $cell.addClass("first");
        $cell.append($('<span class="move"></span>'));
        $cell.append($('<a href="#" class="add add-row"></a>'));
      } else {
        $cell.append($('<a href="#" class="remove remove-column">&times;</a>'));
      }
      $cell.append($('<a href="#" class="add add-column"></a>'));
      $controls.append($cell);
    }
    $controls.insertBefore($firstRow);
  }
  $table.find("tr").slice(1).each(function() {
    var $row = $(this);
    var $firstCell = $row.find("td").first();
    if (!$firstCell.hasClass("ui-row-controls")) {
      var $cell = $('<td contenteditable="false"></td>').addClass("ui-row-controls");
      $cell.append($('<a href="#" class="remove remove-row">&times;</a>'));
      $cell.append($('<a href="#" class="add add-row"></a>'));
      $cell.insertBefore($firstCell);
    }
  });
  return $table;
};

function MediaDialog(editor) {
  this.editor = editor;
  this.displayed = false;
  this.$dialog = $("#media-dialog");
  this.$steps = this.$dialog.find("div.step");
  this.$button = editor.$toolbar.find("a.media");
  var uploadProgress = new MediaDialog.UploadProgressStep(this);
  this.steps = {
    uploadProgress: uploadProgress,
    upload: new MediaDialog.UploadStep(this, uploadProgress),
    image: new MediaDialog.ImageStep(this),
    video: new MediaDialog.VideoStep(this),
    document: new MediaDialog.DocumentStep(this)
  };

  var dialog = this;
  this.$button.click(function (e) {
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
  this.$button.addClass("active").qtip("hide").qtip("disable");
  this.$dialog.show();
  this.displayed = true;
  // TODO: insert placeholder here
};
MediaDialog.prototype.hide = function () {
  this.$button.removeClass("active").qtip("enable");
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
  } else {
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
  this.$step.find("input[type='text'],textarea").first().focus();
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
  this.xhr = null;
  var step = this;
  this.$step.find("a.cancel").click(function (e) {
    e.preventDefault();
    if (step.xhr) {
      step.xhr.abort();
    }
    dialog.openStep("upload");
  });
};
//noinspection JSCheckFunctionSignatures
MediaDialog.UploadProgressStep.prototype = new MediaDialog.Step();
MediaDialog.UploadProgressStep.prototype.constructor = MediaDialog.UploadProgressStep;
MediaDialog.UploadProgressStep.prototype.prepare = function (data) {
  this.xhr = data.xhr;
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
  var editor = this.dialog.editor;
  var $step = this.$step = this.dialog.$steps.filter(".upload");
  var $input = this.$input = $step.find("input:text");
  this.uploadProgress = uploadProgress;

  $step.find("a.hide").click(function (e) {
    e.preventDefault();
    dialog.hide();
  });

  $step.find("a.submit").click(function (e) {
    e.preventDefault();
    oer.status_message.clear();
    $step.block();
    $.post($step.data("url"), {url: $input.val()}, function (response) {
      dialog.handleUploadResponse(response);
      $step.unblock();
    }, "text");
  });

  $step.find("input[type='text']").keydown(function(e) {
    if (e.which === editor.ENTER) {
      $step.find("a.submit").trigger("click");
    }
  });

  var $dropZone = $step.find("div.drop-zone");

  $("#fileupload").fileupload({
    url: $step.data("url"),
    dropZone: $dropZone
  });
  $dropZone.bind("fileuploadsend", function (e, data) {
    dialog.openStep("uploadProgress", {
      name: data.files[0].name,
      xhr: data.xhr()
    });
  });
  $dropZone.bind("fileuploadprogress", function (e, data) {
    var percent = parseInt(data.loaded / data.total * 100, 10);
    uploadProgress.displayProgress(percent);
  });
  $dropZone.bind("fileuploaddone", function (e, data) {
    dialog.handleUploadResponse(data.result);
    uploadProgress.xhr = null;
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

  var editor = dialog.editor;
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
      $figure = $("<figure></figure>").addClass("image").append($("<img>").attr("src", step.imageURL).attr("alt", description)).append($caption);
    }

    editor.saveState();
    if (editor.$focusBlock) {
      $figure.insertAfter(editor.$focusBlock);
    } else {
      editor.$area.append($figure);
    }
    editor.initFigure($figure);
    editor.initImage($figure);
    editor.ensureTextInput();
    editor.updateDND();
    dialog.hide();
  });

  $step.find("input[type='text']").keydown(function(e) {
    if (e.which === editor.ENTER) {
      $step.find("a.submit").trigger("click");
    }
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

  var editor = dialog.editor;

  $step.find("a.submit").click(function (e) {
    e.preventDefault();
    oer.status_message.clear();
    editor.saveState();

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
    if ($step.data("uploaded-video-id")) {
      $figure.attr("data-uploaded-video-id", $step.data("uploaded-video-id"));
    }

    if (editor.$focusBlock) {
      $figure.insertAfter(editor.$focusBlock);
    } else {
      editor.$area.append($figure);
    }
    editor.loadEmbed($figure);
    editor.initFigure($figure);
    editor.ensureTextInput();
    editor.updateDND();
    dialog.hide();
  });

  $step.find("input[type='text']").keydown(function(e) {
    if (e.which === editor.ENTER) {
      $step.find("a.submit").trigger("click");
    }
  });
};

//noinspection JSCheckFunctionSignatures
MediaDialog.VideoStep.prototype = new MediaDialog.Step();
MediaDialog.VideoStep.prototype.constructor = MediaDialog.VideoStep;
MediaDialog.VideoStep.prototype.prepare = function (data) {
  this.$step.data("url", data.url);
  if ("uploaded_video_id" in data) {
    this.$step.data("uploaded-video-id", data["uploaded_video_id"]);
  } else {
    this.$step.data("uploaded-video-id", null);
  }
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

  var editor = dialog.editor;

  $step.find("a.submit").click(function (e) {
    e.preventDefault();
    oer.status_message.clear();

    var type = $selector.val();
    var caption = $.trim($input.val());
    if (caption === "") {
      oer.status_message.error("Please enter the title of this document.");
      return;
    }
    editor.saveState();
    var $figure = $("<figure></figure>").addClass("download").text("Download: ");
    $figure.append($('<a target="_blank"></a>').attr("href", $step.data("url")).append("<strong></strong>").text(caption));
    if (type === "link") {
      if (editor.$focusBlock && editor.range) {
        if (this.$focusBlock.is("p")) {
          editor.range.collapse(false);
          editor.range.insertNode($figure.get(0));
          editor.trackSelection();
        } else {
          $("<p></p>").append($figure).insertAfter(this.$focusBlock);
        }
      } else {
        $("<p></p>").append($figure).appendTo(editor.$area);
      }
    } else {
      if (editor.$focusBlock) {
        $figure.insertAfter(editor.$focusBlock);
      } else {
        editor.$area.append($figure);
      }
    }
    editor.initFigure($figure);
    editor.ensureTextInput();
    editor.updateDND();
    dialog.hide();
  });

  $step.find("input[type='text']").keydown(function(e) {
    if (e.which === editor.ENTER) {
      $step.find("a.submit").trigger("click");
    }
  });
};

//noinspection JSCheckFunctionSignatures
MediaDialog.DocumentStep.prototype = new MediaDialog.Step();
MediaDialog.DocumentStep.prototype.constructor = MediaDialog.DocumentStep;
MediaDialog.DocumentStep.prototype.prepare = function (data) {
  this.$selector.val("button");
  this.$input.val(data.name);
  this.$step.data("url", data.url);
};


function TableOfContents(editor) {
  var $toc = this.$toc = $("#toc > div");
  this.editor = editor;
  this.update();
  var toc = this;

  function trackChanges() {
    // Update only if the structure of headers has changed
    var areaLevels = [];
    editor.$area.find("h2,h3").each(function () {
      var $header = $(this);
      if ($header.is("h2")) {
        areaLevels.push(0);
      } else {
        areaLevels.push(1);
      }
    });
    var tocLevels = $toc.data("levels");
    if (areaLevels.length != tocLevels.length) {
      toc.update();
    } else {
      for (var i = 0; i < areaLevels.length; i++) {
        if (areaLevels[i] != tocLevels[i]) {
          toc.update();
          break;
        }
      }
    }
    setTimeout(trackChanges, 1000);
  }
  setTimeout(trackChanges, 1000);

  $toc.delegate("div.new a", "click", function(e) {
    e.preventDefault();
    editor.saveState();
    var $new = $(e.currentTarget).parent();
    var $areaHeader;
    if ($new.hasClass("level-0")) {
      $areaHeader = $("<h2></h2>");
    } else {
      $areaHeader = $("<h3></h3>");
    }
    var $next = $new.next("div.header");
    if ($next.length) {
      $areaHeader.insertBefore($next.data("header"));
    } else {
      $areaHeader.appendTo(editor.$area);
    }
    var $header = toc.createHeader($areaHeader);
    $header.insertBefore($new);
    $header.find("div.text").focus();
    toc.updateLevels();
  });

  $toc.delegate("div.header a.delete", "click", function(e) {
    e.preventDefault();
    editor.saveState();
    var $header = $(e.currentTarget).parent();
    $header.data("header").remove();
    $header.remove();
    toc.updateLevels();
    toc.updateNewLinks();
  });
  $toc.delegate("div.header a.delete", "mouseover", function(e) {
    $(e.currentTarget).parent().addClass("highlight");
  });
  $toc.delegate("div.header a.delete", "mouseout", function(e) {
    $(e.currentTarget).parent().removeClass("highlight");
  });
}

TableOfContents.prototype.createHeader = function($areaHeader) {
  var text = $.trim($areaHeader.text());
  var $header = $("<div></div>").addClass("header");
  $header.append($("<div></div>").addClass("handle"));
  $header.append($('<a href="#" class="delete">&times;</a>'));
  var $text = $("<div></div>").addClass("text").text(text).attr("contenteditable", "true");
  $text.keyup(function(e) {
    var $t = $(e.target);
    $t.parent().data("header").text($t.text());
  });
  $header.append($text);
  if ($areaHeader.is("h2")) {
    $header.addClass("level-0");
  } else {
    $header.addClass("level-1");
  }
  $header.data("header", $areaHeader);
  $areaHeader.data("toc", $header);
  return $header;
};

TableOfContents.prototype.updateLevels = function() {
  var levels = [];
  this.$toc.find("div.header").each(function() {
    if ($(this).hasClass("level-0")) {
      levels.push(0);
    } else {
      levels.push(1);
    }
  });
  this.$toc.data("levels", levels);
};

TableOfContents.prototype.updateNewLinks = function() {
  var $toc = this.$toc;
  var $new;
  $toc.find("div.new").remove();
  $toc.find("div.header").filter(function() {
    return !$(this).next().is("div.header.level-1");
  }).each(function() {
    var $header = $(this);
    $new = $("<div></div>").addClass("new level-1");
    $new.append($('<a href="#">Add Subheading</a>'));
    $new.insertAfter($header);
  });
  $new = $("<div></div>").addClass("new level-0");
  $new.append($('<a href="#">Add Heading</a>'));
  $new.appendTo($toc);
};

TableOfContents.prototype.update = function() {
  var editor = this.editor;
  var $toc = this.$toc;
  var toc = this;

  $toc.sortable("destroy");
  $toc.find("div.header").remove();

  editor.$area.find("h2,h3").each(function () {
    $toc.append(toc.createHeader($(this)));
  });

  this.updateLevels();
  this.updateNewLinks();

  $toc.sortable({
    items: "div.header",
    handle: "div.handle",
    containment: "parent",
    placeholder: "ui-state-highlight",
    start: function(e, ui) {
      ui.item.addClass("highlight");
    },
    over: function(e, ui) {
      var offset = e.pageX - ui.offset.left;
      if (offset > 50) {
        $toc.addClass("subheader-drop");
      } else {
        $toc.removeClass("subheader-drop");
      }
    },
    stop: function(e, ui) {
      var item = ui.item;
      item.removeClass("highlight");
      editor.saveState();
      if ($toc.hasClass("subheader-drop")) {
        $toc.removeClass("subheader-drop");
        item.removeClass("level-0").addClass("level-1");
      } else {
        item.removeClass("level-1").addClass("level-0");
      }
      var $header = item.data("header");
      if (item.hasClass("level-0") && $header.is("h3")) {
        $header = $("<h2></h2>").html($header.html()).insertAfter($header);
        $header.prev().remove();
        item.data("header", $header);
      } else if (ui.item.hasClass("level-1") && $header.is("h2")) {
        $header = $("<h3></h3>").html($header.html()).insertAfter($header);
        $header.prev().remove();
        item.data("header", $header);
      }
      var $section = $header.add($header.nextUntil("h2,h3"));
      var $next = item.nextAll("div.header").first();
      if ($next.length) {
        $section.detach().insertBefore($next.data("header"));
      } else {
        $section.detach().appendTo(editor.$area);
      }
      toc.updateLevels();
      toc.updateNewLinks();
      editor.updateReferences();
    }
  });
};
