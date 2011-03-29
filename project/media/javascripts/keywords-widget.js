oer.keywords_widget = {};

$.template("keywords-widget-item", '<li><a href="#" class="delete">Delete</a> <span>${name}</span></li>');

oer.keywords_widget.init = function() {

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

    var $widgets = $(".keywords-widget");
    $.each($widgets, function(i, widget) {
        var $widget = $(widget);
        var $input = $widget.find("input[type='hidden']");
        var $add_input = $widget.find("input[type='text']");
        var $keywords = $widget.find("ul");

        function add_value() {
            var value = $add_input.val().split(",")[0];
            var values = get_values($input);
            $add_input.val("");
            if ($.inArray(value, values) != -1) {
                $keywords.find("span:contains('" + value + "')").closest("li").effect("bounce");
                return;
            }
            values.push(value);
            $input.val(values.join(","));
            $.tmpl("keywords-widget-item", {
                name : value
            }).appendTo($keywords);
        }

        $add_input.autocomplete({
        minLength : 2,
        source : "/autocomplete/materials/keyword/name"
        });

        $add_input.keydown(function(e) {
            if (e.keyCode == 13) {
                if ($add_input.autocomplete("opened")) {
                    e.preventDefault();
                    add_value();
                }
            }
        });
  
        $keywords.delegate("a.delete", "click", function(e) {
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