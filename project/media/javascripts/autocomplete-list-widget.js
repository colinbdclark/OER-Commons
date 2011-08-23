oer.autocomplete_list_widget = {};

$.template("autocomplete-list-widget-item", '<li class="rc3"><span>${name}</span> <a href="#" class="delete">x</a></li>');

oer.autocomplete_list_widget.init = function() {

    function get_values($input) {
        var value = $input.val();
        var values = [];
        $.each(value.split(","), function(i, v) {
            v = $.trim(v);
            if (v !== "") {
                values.push(v);
            }
        });
        return $.unique(values);
    }

    var $widgets = $(".autocomplete-list-widget");
    $.each($widgets, function(i, widget) {
        var $widget = $(widget);
        var $input = $widget.find("input[type='hidden']");
        var $add_input = $widget.find("input[type='text']");
        var $items = $widget.find("ul");
        var autocomplete_url = $widget.data("url");

        function add_value(value) {
            var values = get_values($input);
            $add_input.val("");
            if ($.inArray(value, values) != -1) {
                $items.find("span:econtains('" + value + "')").closest("li").effect("pulsate", 200);
                return;
            }
            values.push(value);
            $input.val(values.join(","));
            var $item = $.tmpl("autocomplete-list-widget-item", {
                name : value
            }).appendTo($items);
            if (window.rocon != undefined) {
                rocon.update($item.get(0));
            }
        }

        $add_input.autocomplete({
        minLength : 2,
        source : autocomplete_url,
        select: function(e, ui) {
            e.preventDefault();
            add_value(ui.item.value);
        }  
        });

        $add_input.keypress(function(e) {
            if (e.which == 13) {
                e.preventDefault();
                var value = $.trim($add_input.val());
                if (value !== "") {
                    $.each(get_values($add_input), function(i, v) {
                        add_value(v);
                    });
                }
                $add_input.autocomplete("close");
            }
        });
        
        $add_input.focusout(function(e) {
            var value = $.trim($add_input.val());
            if (value !== "") {
                $.each(get_values($add_input), function(i, v) {
                    add_value(v);
                });
            }
            $add_input.autocomplete("close");
        });
        
        $items.delegate("a.delete", "click", function(e) {
            e.preventDefault();
            var $this = $(this);
            var $li = $this.closest("li");
            var value = $.trim($li.find("span").text());
            var values = get_values($input);
            var i = $.inArray(value, values); 
            if (i != -1) {
                values.splice(i, 1);
                $input.val(values.join(","));
                $li.fadeOut(250, function() {
                    $(this).detach();
                });
            }
        });
        
    });

};
