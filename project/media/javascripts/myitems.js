oer.myitems = {};
oer.myitems.index = {};


oer.myitems._addFolderElement = function($folderLast, template, params) {
    var $item = $.tmpl(template, params);
    var setParams = function(params) {
        if (params.slug) {
            $item.find("a").attr("href", django_js_utils.urls.resolve('myitems:folder', { slug: params.slug }));
        }
        if (params.id) {
            $item.data("folder-id", params.id);
        }
    }
    $item.hide();
    $item.insertBefore($folderLast);
    $item.fadeIn();
    return {
        element: $item,
        setParams: setParams,
        remove: function() { $item.remove(); },
    }
};


oer.myitems._changeNumber = function($elements, delta) {
    for (var i = 0; i < $elements.length; i++) {
        var $element = $elements.eq(i);
        $element.text($element.text()-0+delta);
    }
};


oer.myitems.init_folder_form = function($folderList, template, additionalParams) {
    var $folderLast = $folderList.find("li.last");
    var $form = $folderLast.find(".folder-create-form");
    var $button = $form.find("#folder-create-button");
    var $submit = $form.find("#folder-create-submit");
    var $folderInput = $form.find("input");

    $button.click(function(e) {
        $folderInput.fadeIn();
        $submit.show();
        $button.hide();
        $folderInput.focus();
        e.preventDefault();
    });
    $form.submit(function(e) {
        var folder;
        var params = {
            'name': $folderInput.val(),
        }
        $.extend(params, additionalParams);

        $.post($form.attr("action"), getRequestParams($form), function(response) {
            if (response.status === "success") {
                folder.setParams(response);
            } else {
                folder.remove();
            }
        });
        folder = oer.myitems._addFolderElement($folderLast, template, {
            number: 0,
            name: $folderInput.val(),
        });
        $folderInput.hide();
        $submit.hide();
        $folderInput.val("");
        $button.fadeIn();
        e.preventDefault();
    });
    $submit.click(function(e) {
        $form.submit();
        e.preventDefault();
    });

};

oer.myitems.init = function() {
    oer.myitems.index.init();

    $.template("myitems:folder",
        '<li class="folder"><i class="folder-icon"></i> <a><span class="name">${name}</span> (<span class="number">${number}</span>)</a> <a href="#" class="delete">×</a></li>');
    $.template("myitems:item-folder", '<li data-folder-id="${id}"><div class="folder-deco"></div>${name} <a href="#" class="delete">×</a></li>');

    var $folderList = $(".my-items-views");
    var $folderLast = $folderList.find("li.last");
    var $itemFolderLists = $("article ul.folder-list");
    var $itemFolderAddButton = $itemFolderLists.find("li.last a");
    var $itemFolderForm = $('<li id="folder-item-form" class="hidden"><form><input type="text" /><a class="dashed" href="#">Submit</a></form></li>');
    var $itemFolderInput = $itemFolderForm.find("input");

    oer.myitems.init_folder_form($folderList, "myitems:folder", {});

    var addItemUrl = django_js_utils.urls.resolve('myitems:folder_add_item');
    var deleteUrl = django_js_utils.urls.resolve('myitems:folder_delete');
    var deleteItemFolderUrl = django_js_utils.urls.resolve('myitems:folder_delete_item');
    var deleteItemUrl = django_js_utils.urls.resolve('myitems:delete_item');

    var addFolderDeleteConfirmation = function () {
        $folderList.delegate("a.delete", "click", function(action) {
            $(action.target).parent().addClass("to-delete");
        });

        $folderList.find("a.delete").inlineConfirmation({
            confirm: "<a class='confirm rc3' href='#'>Confirm</a>",
            cancel: "<a class='cancel' href='#'>Cancel</a>",
            confirmCallback: function(action) {
                var $folder = action.parent();

                var folderId = $folder.data("folder-id");
                var $itemFolders = $itemFolderLists.find("li[data-folder-id='"+folderId+"']");
                $.post(deleteUrl, {id: folderId}, function(response) {
                    if (response.status === "success") {
                        $folder.remove();
                        $itemFolders.remove();
                    } else {
                        $folder.show();
                        $itemFolders.show();
                        $folder.removeClass("to-delete");
                    }
                });
                $folder.fadeOut();
                $itemFolders.fadeOut();
            },
            cancelCallback: function(action) {
                var $folder = action.parent();
                $folder.removeClass("to-delete");
            }
        });
    };


    var addItemFolderDelete = function () {
        $(".materials-index").delegate("article .folder-list .delete", "click", function(action) {
            action.preventDefault();
            var $itemFolder = $(action.target).parent();
            var folderId = $itemFolder.data("folder-id");
            var $article = $itemFolder.closest("article");
            var itemId = $article.attr("data-identifier");
            var request = { folder_id: folderId, item_id: itemId };
            var $folder = getFolderById(folderId);
            var $number = $folder.find("span.number");

            var $elementsToDelete = $itemFolder;
            if ($folder.filter(".selected").length) {
                $elementsToDelete = $elementsToDelete.add($article);
            }
            $.post(deleteItemFolderUrl, request, function(response) {
                if (response.status === "success") {
                    $elementsToDelete.remove();
                } else {
                    $elementsToDelete.show();
                    $number.text($number.text()-0+1);
                }
            });
            $elementsToDelete.fadeOut();
            $number.text($number.text()-0-1);
        });
    };


    var addItemDeleteConfirmation = function () {
        $("article div.delete a.delete").inlineConfirmation({
            confirmCallback: function(action) {
                var $article = action.closest("article");
                var $itemFolders = $article.find("ul.folder-list li");
                var itemId = $article.attr("data-identifier");
                var $numbers = $folderList.find("li.view.myitems span.number");

                if ($article.find("div.right.relation").text() === "SUBMITTED") {
                    $numbers = $numbers.add($folderList.find("li.view.submitted span.number"));
                }

                var $folders = $folderList.children("li.folder");
                for (var i = 0; i < $itemFolders.length-1; i++) {
                    var itemFolderId = $itemFolders.eq(i).data("folder-id");
                    for (var j = 0; j < $folders.length; j++) {
                        var $folder = $folders.eq(j);
                        if ($folder.data("folder-id") === itemFolderId) {
                            $numbers = $numbers.add($folder.find("span.number"));
                            break;
                        }
                    }
                }
                $.post(deleteItemUrl, {item_id: itemId}, function(response) {
                    if (response.status === "success") {
                        $article.remove();
                    } else {
                        $article.show();
                        oer.myitems._changeNumber($numbers, 1);
                    }
                });
                $article.fadeOut();
                oer.myitems._changeNumber($numbers, -1);
            }
        });
    };

    var itemFolderElement = function(params) {
        var $item = $.tmpl("myitems:item-folder", params);
        return $item;
    };

    var getFolders = function(request, callback) {
        var term = $.trim(request.term).toLowerCase();
        var folders = [];
        var $names = $folderList.find("li.folder span.name");
        for (var i = 0; i < $names.length; i++) {
            var folder = $.trim($names.eq(i).text());
            if (folder.substring(0, term.length).toLowerCase() === term) {
                folders.push(folder);
            }
        }
        callback(folders);
    };


    var getFolderByName = function(name) {
        var $items = $folderList.find("li.folder span.name");
        for(var i = 0; i < $items.length; i++) {
            var $item = $items.eq(i);
            if ($.trim($item.text()) === name) {
                return $item.closest("li");
            }
        }
    };

    var getFolderById = function(id) {
        return $folderList.find("li.folder[data-folder-id='"+id+"']")
    };

    $itemFolderAddButton.click(function(e) {
        $itemFolderInput.autocomplete("enable");
        $itemFolderForm.next().fadeIn();
        $itemFolderForm.detach();
        $($(e.target).parent()).hide();
        $itemFolderForm.insertBefore($(e.target).parent());
        $itemFolderForm.fadeIn();
        $itemFolderInput.focus();
        e.preventDefault();
    });
    $itemFolderForm.find("a").click(function(e) {
        $itemFolderForm.submit();
        e.preventDefault();
    });
    $itemFolderForm.submit(function(e) {
        $itemFolderInput.autocomplete("close");
        $itemFolderInput.autocomplete("disable");
        $itemFolderForm.next().fadeIn();
        $itemFolderForm.hide();
        var value = $.trim($itemFolderInput.val());
        if (value !== "") {
            $itemFolderInput.val("");
            var identifier = $itemFolderForm.closest("article").attr("data-identifier");

            var request = {
                folder_name: value,
                item_id: identifier
            };

            $.post(addItemUrl, request, function(response) {
                if (response.status === "success") {
                    var context;
                    if (response.id) {
                        context = {
                            name: value,
                            id: response.id,
                            slug: response.slug,
                            number: 1
                        };
                        var folder = oer.myitems._addFolderElement($folderLast, "myitems:folder", {
                            name: value,
                            number: 1,
                        });
                        folder.setParams(response);
                    }
                    else {
                        var $folder = getFolderByName(value);
                        context = {
                            name: value,
                            id: $folder.data("folder-id")
                        };
                        var $number = $folder.find("span.number");
                        $number.text($number.text()-0+1);
                    }
                    $itemFolderForm.closest("#folder-item-form").before(itemFolderElement(context));
                }
            });
        }
        e.preventDefault();
    });

    addFolderDeleteConfirmation();
    addItemFolderDelete();
    addItemDeleteConfirmation();

    $itemFolderInput.autocomplete({
        source: getFolders
    });
};

oer.myitems.index.init_action_panel = function() {
    var $form = $("div.action-panel form");
    $form.find("select[name='batch_size']").change(function() {
        $form.submit();
    });
    $form.find("select[name='sort_by']").change(function() {
        $form.submit();
    });
};

oer.myitems.index.init = function() {

    oer.myitems.index.init_action_panel();
    oer.materials.index.init_actions_menus();

};

oer.myitems.init_save_button = function() {
    $.template("myitems:button-folder",
        '<li class="folder selected"><i class="folder-icon"></i> <a href="${url}"><span class="name">${name}</span> (<span class="number">1</span>)</a></li>');

    var $myitemsSaveButton = $(".myitems-save-button");
    var $folderList = $myitemsSaveButton.find(".my-items-views");
    var identifier = $myitemsSaveButton.attr("data-identifier");
    oer.myitems.init_folder_form($folderList, "myitems:button-folder", { item_id: identifier });

    var saveUrl = django_js_utils.urls.resolve('saveditems:save_item');
    var unsaveUrl = django_js_utils.urls.resolve('myitems:delete_item');

    var $saveUnsaveButton = $myitemsSaveButton.find(".save-unsave-button");
    var $saveButton = $saveUnsaveButton.filter(".save");
    var $unsaveButton = $saveUnsaveButton.filter(".unsave");

    $myitemsSaveButton.delegate(".save", "click", function(e) {
        e.preventDefault();

        $saveButton.addClass("hidden");
        $unsaveButton.removeClass("hidden");
        $.post(saveUrl, { item_id: identifier }, function(response) {
            if (response.status !== "success") {
                $unsaveButton.addClass("hidden");
                $saveButton.removeClass("hidden");
            }
        });
    });

    $myitemsSaveButton.delegate(".unsave", "click", function(e) {
        e.preventDefault();

        $unsaveButton.addClass("hidden");
        $saveButton.removeClass("hidden");
        var $folders = $folderList.find(".folder.selected");
        $folders.removeClass("selected");
        oer.myitems._changeNumber($folders.find(".number"), -1);
        $.post(unsaveUrl, { identifier: identifier }, function(response) {
            if (response.status !== "success") {
                $saveButton.addClass("hidden");
                $unsaveButton.removeClass("hidden");
                $folders.addClass("selected");
                oer.myitems._changeNumber($folders.find(".number"), 1);
            }
        });
    });


    $folderList.delegate(".folder", "click", function() {
        var $this = $(this);
        var $number = $this.find(".number");
        var delta;
        var addItemUrl = django_js_utils.urls.resolve('myitems:folder_add_item');
        var deleteItemFolderUrl = django_js_utils.urls.resolve('myitems:folder_delete_item');
        var $form = $folderList.find(".last .folder-create-form");

        var params = {
            folder_name: $this.find(".name").text(),
            folder_id: $this.data("folder-id"),
            item_id: identifier,
        };
        var action = $this.hasClass("selected");
        var action_dicts = {
            true: {
                url: deleteItemFolderUrl,
                delta: -1,
                func: function() { $this.removeClass("selected") },
            },
            false: {
                url: addItemUrl,
                delta: 1,
                func: function() { $this.addClass("selected") },
            },
        }
        var modifyFolder = function(action_dict) {
            action_dict.func();
            oer.myitems._changeNumber($number, action_dict.delta);
        };
        var action_dict = action_dicts[action];
        modifyFolder(action_dict);
        $.post(action_dict.url, params, function(response) {
            if (response.status === "success") {
                var $unsave = $myitemsSaveButton.find(".save-unsave-button.unsave");
                if (!action && $unsave.hasClass("hidden")) {
                    $myitemsSaveButton.find(".save-unsave-button.save").addClass("hidden");
                    $unsave.removeClass("hidden")
                }
            }
            else {
                modifyFolder(action_dicts[!action]);
            }
        });
    });
    $folderList.delegate(".folder a", "click", function(e) {
        e.preventDefault();
    });
    $myitemsSaveButton.find(".folder-list-button").click(function(e) {
        e.preventDefault();
        e.stopPropagation();
        $folderList.slideToggle();
    });
    $myitemsSaveButton.click(function(e) {
        e.stopPropagation();
    });
    $("body").click(function(e) {
        $folderList.slideUp();
    });
};
