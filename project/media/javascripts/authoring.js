oer.authoring = {};

oer.authoring.Editor = function () {
  var $editor = $("#editor");
  var $toolbar = $editor.find(".toolbar");
  var $area = $editor.find(".editor-area");

  $area.find("figure").attr("contenteditable", "false");

  // Ensure that we always have a text block at the end of editor area
  function ensureTextInput() {
    if (!$area.children().last().is("p,div,h1,h2,h3,h4,ul,ol,blockquote")) {
      $("<p><br/></p>").appendTo($area);
    }
  }

  ensureTextInput();

  // Make sure we have a text input block after user hit Backspace or Delete key.
  $area.keyup(function (e) {
    if (e.which === 8 || e.which === 46) {
      ensureTextInput();
    }
  });

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

  // Find current block
  $toolbar.mousedown(function () {
    // Find the currently active block in editable area when user clicks on
    // any of toolbar buttons. We use mousedown here because IE looses the focus
    // when mouse button is released so it becomes impossible to find the active
    // block.
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

  // Change block type
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

  // Insert list
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
      default:
        break;
    }

  });

  // Link UI
  (function () {
    var $dialog = $("#edit-link-dialog");
    var $input = $dialog.find("input[name='url']");

    $dialog.delegate("a", "click", function (e) {
      // TODO: use form with URL validation here.
      e.preventDefault();
      var href = $(e.target).attr("href");
      var $link = $dialog.data("link");
      switch (href) {
        case "#save":
          $dialog.data("link").attr("href", $input.val());
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
      $dialog.hide();
    });

    $area.delegate("a", "click", function (e) {
      e.preventDefault();
      var $link = $(e.target);
      if ($link.parents("figure.document").length) {
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

  })();

  // Media UI
  (function () {
    var $dialog = $("#media-dialog");
    var $steps = $dialog.find("div.step");

    var $uploadStep = $steps.filter(".upload");
    var $uploadStepInput = $uploadStep.find(":text");

    $toolbar.find("a.button.media").click(function (e) {
      e.preventDefault();
      $steps.not($uploadStep).hide();
      $uploadStepInput.val("");
      $uploadStep.show();
      $dialog.fadeIn();
    });

    var $uploadProgressStep = $steps.filter(".upload-progress");
    var $uploadProgressFilename = $uploadProgressStep.find("h2 strong");
    var $uploadProgressFill = $uploadProgressStep.find("div.fill");
    var $uploadProgressLegend = $uploadProgressStep.find("div.legend");

    // Upload step
    $uploadStep.find("div.actions a").click(function (e) {
      e.preventDefault();
      var href = $(this).attr("href");
      switch (href) {
        case "#cancel":
          $dialog.hide();
          // TODO: re-enable editor and toolbar buttons here
          break;
        case "#ok":
          // TODO: display loading indicator
          oer.status_message.clear();
          $.post($uploadStep.data("url"), {url: $uploadStepInput.val()}, handleUploadResponse, "text");
          break;
        default:
          break;
      }
    });

    function handleUploadResponse(response) {
      var result = $.parseJSON(response);
      if (result.status === "error") {
        oer.status_message.error(result.message);
        $uploadProgressStep.hide();
        $uploadStep.show();
      } else if (result.type === "image") {
        imageStep.display(result);
      } else if (result.type === "document") {
        documentStep.display(result);
      } else if (result.type === "link") {
        $dialog.hide();
        execCommand("createLink", "#new-link");
        var $link = $area.find("a[href='#new-link']");
        $link.attr("href", result.url);
        $link.data("new", true);
        if ($link.text() === "#new-link") {
          $link.text("Link");
        }
        $link.click();
      }
    }


    var $dropZone = $dialog.find("div.drop-zone");
    $dropZone.fileupload({
      url: $uploadStep.data("url"),
      dropZone: $dropZone
    }).bind("fileuploadsend",
            function (e, data) {
              $uploadProgressFilename.text(data.files[0].name);
              $uploadProgressFill.css({width: "0%"});
              $uploadProgressLegend.text("0%");
              $uploadStep.hide();
              $uploadProgressStep.show();
              oer.status_message.clear();
            }).bind("fileuploadprogress",
            function (e, data) {
              var percent = parseInt(data.loaded / data.total * 100, 10) + "%";
              $uploadProgressFill.css({width: percent});
              $uploadProgressLegend.text(percent);
            }).bind("fileuploaddone", function (e, data) {
              handleUploadResponse(data.result);
            });

    // Image step
    var imageStep = new (function() {
      var $step = $steps.filter(".image");
      var $nameCt = $step.find("h2 strong");
      var $imageCt = $step.find("div.left");
      var $textarea = $step.find("textarea");

      this.display = function(data) {
        $imageCt.empty();
        $nameCt.text(data.name);
        $textarea.val("");
        var $image = $("<img>").attr("src", data.thumbnail).data("url", data.url);
        $image.appendTo($imageCt);
        $steps.not($step).hide();
        $step.show();
      };

      $step.find("div.actions a").click(function (e) {
        e.preventDefault();
        var href = $(this).attr("href");
        switch (href) {
          case "#cancel":
            $dialog.hide();
            // TODO: send request to remove the uploaded image
            break;
          case "#ok":
            var caption = $.trim($textarea.val());
            var $figure = $('<figure class="image" contenteditable="false">' +
                    '<img src="' + $imageCt.find("img").data("url") + '">' +
                    '<figcaption>' + caption + '</figcaption>' +
                    '</figure>');
            if ($currentBlock) {
              $figure.insertAfter($currentBlock);
            } else {
              $area.append($figure);
            }
            initImageDND($figure.find("img"));
            ensureTextInput();
            $dialog.hide();
            break;
          default:
            break;
        }
      });
    })();

    // Document step
    var documentStep = new (function() {
      var $step = $steps.filter(".document");
      var $nameCt = $step.find("h2 strong");
      var $input = $step.find("input:text");

      this.display = function(data) {
        $nameCt.text(data.name);
        $input.val("");
        $steps.not($step).hide();
        $step.data("url", data.url);
        $step.show();
      };

      $step.find("div.actions a").click(function (e) {
        e.preventDefault();
        var href = $(this).attr("href");
        switch (href) {
          case "#cancel":
            $dialog.hide();
            // TODO: send request to remove the uploaded document
            break;
          case "#ok":
            oer.status_message.clear();
            var caption = $.trim($input.val() || $nameCt.text());
            if (caption === "") {
              oer.status_message.error("Please enter the name of this document.")
              break;
            }
            var $figure = $('<figure class="document" contenteditable="false">' +
                    '<a target="_blank" href="' + $step.data("url") + '">Download <span>' + caption + '</span></a>' +
                    '</figure>');
            if ($currentBlock) {
              $figure.insertAfter($currentBlock);
            } else {
              $area.append($figure);
            }
            ensureTextInput();
            $dialog.hide();
            break;
          default:
            break;
        }
      });
    })();

    // Image DND
    // TODO: картинки склеиваются при перетаскивании
    function initImageDND($el) {
      $el.draggable({
        helper: "clone",
        opacity: 0.3,
        appendTo: "body",
        addClasses: false,
        cursor: "move"
      }).bind("dragstart",
              function () {
                var $image = $(this);
                var $figure = $image.parent();
                var $blocks = $area.children();
                $blocks.not($figure).not($figure.prev()).droppable({
                  addClasses: false,
                  tolerance: "pointer"
                }).bind("dropover",
                        function () {
                          var $this = $(this);
                          $this.stop(true).animate({
                            "margin-bottom": "70px"
                          });
                        }).bind("dropout",
                        function () {
                          var $this = $(this);
                          $this.stop(true).animate({
                            "margin-bottom": "1em"
                          });
                        }).bind("drop", function () {
                          $figure.detach().insertAfter($(this));
                          $area.children().stop(true).css({
                            "margin-bottom": ""
                          });
                          ensureTextInput();
                        });
              }).bind("dragstop", function () {
                $area.children().droppable("destroy");
              });
    }

    $area.find("figure.image img").each(function (i, el) {
      initImageDND($(el));
    });

  })();

  var $form = $("#edit-authored-material");

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
    var $preview = $editor.find("div.preview");
    var $actions = $("div.actions a");
    $actions.click(function (e) {
      e.preventDefault();
      var $this = $(this);
      var href = $this.attr("href");
      switch (href) {
        case "#save":
          $input.val($area.html());
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
  })();

};
