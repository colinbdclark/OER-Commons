oer.myitems = {};
oer.myitems.index = {};

oer.myitems.init = function() {
    oer.myitems.index.init();


    $.template("myitems:folder",
        '<li class="folder" data-folder-id="${id}"><a href="${url}"><span class="name">${name}</span> (<span class="number">${number}</span>)</a> <a href="#" class="delete">×</a></li>');
    $.template("myitems:item-folder", '<li data-folder-id="${id}"><div class="folder-deco"></div>${name} <a href="#" class="delete">×</a></li>');

    var addItemUrl = django_js_utils.urls.resolve('myitems:folder_add_item');
    var deleteUrl = django_js_utils.urls.resolve('myitems:folder_delete');
    var deleteItemFolderUrl = django_js_utils.urls.resolve('myitems:folder_delete_item');
    var deleteItemUrl = django_js_utils.urls.resolve('myitems:delete_item');

    var addFolderDeleteConfirmation = function () {
        $folderList.find("a.delete").inlineConfirmation({
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
                    }
                });
                $folder.fadeOut();
                $itemFolders.fadeOut();
            }
        });
    };


    var addItemFolderDeleteConfirmation = function () {
        $itemFolderLists.find("li a.delete").inlineConfirmation({
            confirmCallback: function(action) {
                var $itemFolder = action.parent();
                var folderId = $itemFolder.data("folder-id");
                var $article = $itemFolder.closest("article");
                var itemId = $article.data("identifier");
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
            }
        });
    };


    var changeNumber = function($elements, delta) {
        for (var i = 0; i < $elements.length; i++) {
            var $element = $elements.eq(i);
            $element.text($element.text()-0+delta);
        }
    };


    var addItemDeleteConfirmation = function () {
        $("article div.delete a.delete").inlineConfirmation({
            confirmCallback: function(action) {
                var $article = action.closest("article");
                var $itemFolders = $article.find("ul.folder-list li");
                var itemId = $article.data("identifier");
                var $numbers = $folderList.find("li.view.myitems span.number");

                if ($article.find("div.right.relation").text() === "CREATED") {
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
                        changeNumber($numbers, 1);
                    }
                });
                $article.fadeOut();
                changeNumber($numbers, -1);
            }
        });
    };

    var addFolderElement = function(params) {
        params.url = django_js_utils.urls.resolve('myitems:folder', {slug: params.slug});
        var $item = $.tmpl("myitems:folder", params);
        $item.hide();
        $item.insertBefore($folderLast);
        $item.fadeIn();
        return $item;
    };

    var itemFolderElement = function(params) {
        var $item = $.tmpl("myitems:item-folder", params);
        return $item;
    };

    var getFolders = function(request, callback) {
        var term = $.trim(request.term).toLowerCase();
        var folders = [];
        var $names = $("#folder-create-form li.folder span.name");
        for (var i = 0; i < $names.length; i++) {
            var folder = $.trim($names.eq(i).text());
            if (folder.substring(0, term.length).toLowerCase() === term) {
                folders.push(folder);
            }
        }
        callback(folders);
    };


    var $form = $("#folder-create-form");
    var $button = $("#folder-create-button");
    var $submit = $("#folder-create-submit");
    var $folderInput= $form.find("input");
    var $folderList = $form.find("ul");
    var $folderLast = $folderList.find("li.last");
    var $itemFolderLists = $("article ul.folder-list");
    var $itemFolderAddButton = $itemFolderLists.find("li.last a");
    var $itemFolderForm = $('<li id="folder-item-form" class="hidden"><form><input type="text" /><a class="dashed" href="#">Submit</a></form></li>');
    var $itemFolderInput = $itemFolderForm.find("input");

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
            var identifier = $itemFolderForm.closest("article").data("identifier");

            var request = {
                folder_name: value,
                item_id: identifier
            };

            $.post(addItemUrl, request, function(response) {
                if (response["status"] === "success") {
                    var context;
                    if (response["folder_id"]) {
                        context = {
                            name: value,
                            id: response["folder_id"],
                            slug: response["folder_slug"],
                            number: 1
                        };
                        addFolderElement(context);
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
    addItemFolderDeleteConfirmation();
    addItemDeleteConfirmation();

    $itemFolderInput.autocomplete({
        source: getFolders
    });

    var onFolderCreation = function(response) {
        if (response["status"] === "success") {
            response["number"] = 0;
            addFolderElement(response);
        }
    };

    $button.click(function(e) {
        $folderInput.fadeIn();
        $submit.show();
        $button.hide();
        $folderInput.focus();
        e.preventDefault();
    });
    $form.submit(function(e) {
        $.post($form.attr("action"), $form.serialize(), onFolderCreation);
        $folderInput.fadeOut();
        $submit.hide();
        $folderInput.val("");
        $button.show();
        e.preventDefault();
    });
    $submit.click(function(e) {
        $form.submit();
        e.preventDefault();
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

    oer.collapsibles.init($("#content"));

};

oer.myitems.index.init_saved_items = function() {
    var $confirmation = $("div.unsave-confirmation");

    $confirmation.find("a.cancel").click(function(e) {
        e.preventDefault();
        $confirmation.hide();
    });

    $confirmation.find("a.unsave").click(function(e) {
        e.preventDefault();
        var $item = $confirmation.closest("article.item");
        $confirmation.hide().detach();
        var url = $item.find("a.unsave-item").attr("href");
        $.post(url,
            function() {
                $item.fadeOut(500);
            });
    });

    $("#content").delegate("a.unsave-item", "click", function(e) {
        e.preventDefault();
        var $this = $(this);
        var $details = $this.closest("article.item").find("div.details");
        $confirmation.detach().appendTo($details).fadeIn(300);
    });
};

