oer.myitems = {};
oer.myitems.index = {};

oer.myitems.init = function() {
    oer.myitems.index.init();


    $.template("myitems:folder",
        '<li class="folder" data-folder-id="${id}"><a href="${url}"><span class="name">${name}</span> (<span class="number">${number}</span>)</a> <a href="#" class="delete">Delete</a></li>');
    $.template("myitems:item-folder", '<li data-folder-id="${id}">${name} <a href="#" class="delete">Delete</a></li>');

    var addItemUrl = django_js_utils.urls.resolve('myitems:folder_add_item');
    var deleteUrl = django_js_utils.urls.resolve('myitems:folder_delete');
    var deleteItemFolderUrl = django_js_utils.urls.resolve('myitems:folder_delete_item');

    var addFolderDeleteConfirmation = function ($addTo) {
        $addTo.inlineConfirmation({
            confirmCallback: function(action) {
                var $folder = action.parent();
                var folderId = $folder.data("folder-id");
                var $itemFolders = $("article ul.folder-list li[data-folder-id='"+folderId+"']");
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


    var addItemFolderDeleteConfirmation = function ($addTo) {
        $addTo.inlineConfirmation({
            confirmCallback: function(action) {
                var $itemFolder = action.parent();
                var folderId = $itemFolder.data("folder-id");
                var itemId = $itemFolder.closest("article").data("identifier");
                var request = { folder_id: folderId, item_id: itemId };
                console.log();
                var $number = getFolderById(folderId).find("span.number");
                $.post(deleteItemFolderUrl, request, function(response) {
                    if (response.status === "success") {
                        $itemFolder.remove();
                    } else {
                        $itemFolder.show();
                        $number.text($number.text()-0+1);
                    }
                });
                $itemFolder.fadeOut();
                $number.text($number.text()-0-1);
            }
        });
    };

    var folderElement = function(params) {
        params.url = django_js_utils.urls.resolve('myitems:folder', {slug: params.slug});
        var $item = $.tmpl("myitems:folder", params);
        addFolderDeleteConfirmation($item.find("a.delete"));
        return $item;
    };

    var itemFolderElement = function(params) {
        var $item = $.tmpl("myitems:item-folder", params);
        addItemFolderDeleteConfirmation($item.find("a.delete"));
        return $item;
    };

    var getFolders = function(request, callback) {
        var term = $.trim(request.term);
        var folders = [];
        $("#folder-create-form li.folder span.name").each(function() {
            var folder = $.trim($(this).text());
            if (folder.substring(0, term.length) === term) {
                folders.push(folder);
            }
        });
        callback(folders);
    };


    var $form = $("#folder-create-form");
    var $button = $("#folder-create-button");
    var $submit = $("#folder-create-submit");
    var $folderInput= $form.find("input");
    var $folderList = $form.find("ul");
    var $folderLast = $folderList.find("li.last");
    var $inputs = $("article ul.folder-list li.last input");

    var getFolderByName = function(name) {
        var $items = $folderList.find("li.folder span.name");
        for(var i = 0; i < $items.length; i++) {
            var $item = $items.eq(i);
            if ($.trim($item.text()) === name) {
                return $item.parent();
            }
        }
    };

    var getFolderById = function(id) {
        return $folderList.find("li.folder[data-folder-id='"+id+"']")
    };


    addFolderDeleteConfirmation($folderList.find("a.delete"));
    addItemFolderDeleteConfirmation($("article ul.folder-list li a.delete"));

    $inputs.autocomplete({
        source: getFolders
    });


    $inputs.keypress(function(e) {
        if (e.which == 13) {
            var $this = $(this);
            e.preventDefault();
            var value = $.trim($this.val());
            if (value !== "") {
                var identifier = $this.closest("article").data("identifier");

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
                            var $folderLast = $.find("#folder-create-form li.last");
                            var $item = folderElement(context);
                            $item.insertBefore($folderLast);
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
                        $this.parent().before(itemFolderElement(context));
                    }
                });
            }
            $this.autocomplete("close");
        }
    });

    var onFolderCreation = function(response) {
        if (response["status"] === "success") {
            response["number"] = 0;
            var $item = folderElement(response);
            $item.hide();
            $item.insertBefore($folderLast);
            $item.fadeIn();
        }
    };

    $button.click(function(e) {
        $folderInput.fadeIn();
        $submit.show();
        $button.hide();
        e.preventDefault();
    });
    $form.submit(function(e) {
        $.post($form.attr("action"), $form.serialize(), onFolderCreation);
        $folderInput.fadeOut();
        $submit.hide();
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

