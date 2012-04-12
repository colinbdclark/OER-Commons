(function() {
  var PLUGIN_NAME, Widget;

  PLUGIN_NAME = "gradesWidget";

  Widget = (function() {

    function Widget(widget) {
      var _this = this;
      this.widget = widget;
      this.widget.data(PLUGIN_NAME, this);
      this.fieldName = this.widget.data("field-name");
      this.select = this.widget.find("select");
      this.list = this.widget.find("ul");
      this.select.change(function(e) {
        var val;
        val = _this.select.val();
        if (val === "") return;
        _this.addItem(_this.select.children("[value='" + val + "']").first());
        _this.select.children().first().attr("selected", "selected");
      });
      this.list.delegate("a.delete", "click", function(e) {
        e.preventDefault();
        _this.removeItem($(e.currentTarget).closest("li", _this.list));
      });
      return;
    }

    Widget.prototype.addItem = function(option) {
      var existing, li, name, value;
      value = option.attr("value");
      name = option.text();
      existing = this.list.find("input[value='" + value + "']");
      if (existing.length) {
        existing.closest("li", this.list).effect("bounce");
        return;
      }
      li = $("<li>\n  <span>" + name + "</span>\n  <input type=\"hidden\" name=\"" + this.fieldName + "\" value=\"" + value + "\">\n  <a href=\"#\" class=\"delete ui-icon ui-icon-close\">Delete</a>\n</li>");
      li.appendTo(this.list);
    };

    Widget.prototype.removeItem = function(li) {
      li.remove();
    };

    return Widget;

  })();

  (function($) {
    return $.fn[PLUGIN_NAME] = function(action, arg) {
      return this.each(function() {
        var $this, widget;
        $this = $(this);
        widget = $this.data(PLUGIN_NAME);
        if (!widget) widget = new Widget($this);
        if (action) return widget[action](arg);
      });
    };
  })(jQuery);

}).call(this);
