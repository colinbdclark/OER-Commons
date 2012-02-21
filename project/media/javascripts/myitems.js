oer.myitems = {};
oer.myitems.index = {};

oer.myitems.init = function() {
    $.template("folder", '<li><a href="/my/folder/${slug}">${name} (${number})</a> <a href="#" class="delete" data-folder-id="${id}">Delete</a></li>');
    $.template("item-folder", '<li data-folder-id="${id}">${name}</li>');

    oer.myitems.init_folder_form();
    oer.myitems.index.init();

    var addItemURL = "/my/folder-add-item/";

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
    var $inputs = $("article ul.folder-list li.last input");
    $inputs.autocomplete({
        source: getFolders
    });



    var getFolderByName = function(name) {
        var $items = $("#folder-create-form li.folder span.name");
        for(var i = 0; i < $items.length; i++) {
            var $item = $items.eq(i);
            if ($.trim($item.text()) === name) {
                return $item.parent();
            }
        }
    };

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

                $.post(addItemURL, request, function(response) {
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
                            $.tmpl("folder", context).insertBefore($folderLast);
                        }
                        else {
                            var $folder = getFolderByName(value);
                            context = {
                                name: value,
                                id: $folder.data("identifier")
                            };
                            var $number = $folder.find("span.number");
                            $number.text($number.text()-0+1);
                        }
                        $this.parent().before($.tmpl("item-folder", context));
                    }
                });
            }
            $this.autocomplete("close");
        }
    });
};

oer.myitems.init_folder_form = function() {
    var $form = $("#folder-create-form");
    var $button = $("#folder-create-button");
    var $submit = $("#folder-create-submit");
    var $folderInput= $form.find("input");
    var $folderList = $form.find("ul");
    var $folderLast = $folderList.find("li.last");
    var deleteUrl = $folderList.data("delete-url");

    var addConfirmation = function () {
        $folderList.find("a.delete").inlineConfirmation({
            confirmCallback: function(action) {
                var $parent = action.parent();
                var folderId = action.data("folder-id");
                var $itemFolders = $("article li[data-folder-id='"+folderId+"']");
                $.post(deleteUrl, {id: folderId}, function(response) {
                    if (response.status === "success") {
                        $parent.remove();
                        $itemFolders.remove();
                    } else {
                        $parent.show();
                    }
                });
                $parent.fadeOut();
                $itemFolders.fadeOut();
            }
        });
    };
    addConfirmation();

    var onFolderCreation = function(response) {
        if (response["status"] === "success") {
            response["number"] = 0;
            var $item = $.tmpl("folder", response);

            $item.hide();
            $item.insertBefore($folderLast);
            addConfirmation();
            $item.fadeIn();
        }
    };

    $button.click(function(e) {
        $folderInput.fadeIn();
        $submit.show();
        $button.hide();
        e.preventDefault();
    });
    $submit.click(function(e) {
        $.post($form.attr("action"), $form.serialize(), onFolderCreation);
        $folderInput.fadeOut();
        $submit.hide();
        $button.show();
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

