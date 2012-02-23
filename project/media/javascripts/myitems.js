oer.myitems = {};
oer.myitems.index = {};

oer.myitems.init = function() {
    oer.myitems.index.init();


    $.template("myitems:folder",
        '<li class="folder"><a href="${url}"><span class="name">${name}</span> (<span class="number">${number}</span>)</a> <a href="#" class="delete" data-folder-id="${id}">Delete</a></li>');
    $.template("myitems:item-folder", '<li data-folder-id="${id}">${name} <a href="#" class="delete">Delete</a></li>');

    var addItemUrl = django_js_utils.urls.resolve('myitems:folder_add_item');
    var deleteUrl = django_js_utils.urls.resolve('myitems:folder_delete');

    var folderElement = function(params) {
        params.url = django_js_utils.urls.resolve('myitems:folder', {slug: params.slug});
        return $.tmpl("myitems:folder", params);
    };

    var addConfirmation = function ($addTo) {
        $addTo.inlineConfirmation({
            confirmCallback: function(action) {
                var $folder = action.parent();
                var folderId = action.data("folder-id");
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


    var getFolderByName = function(name) {
        var $items = $("#folder-create-form li.folder span.name");
        for(var i = 0; i < $items.length; i++) {
            var $item = $items.eq(i);
            if ($.trim($item.text()) === name) {
                return $item.parent();
            }
        }
    };

    var $form = $("#folder-create-form");
    var $button = $("#folder-create-button");
    var $submit = $("#folder-create-submit");
    var $folderInput= $form.find("input");
    var $folderList = $form.find("ul");
    var $folderLast = $folderList.find("li.last");
    var $inputs = $("article ul.folder-list li.last input");


    addConfirmation($folderList.find("a.delete"));

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
                            addConfirmation($item.find("a.delete"));
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
                        $this.parent().before($.tmpl("myitems:item-folder", context));
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
            addConfirmation($item.find("a.delete"));
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

