(function() {
  var PLUGIN_NAME, Widget;

  PLUGIN_NAME = "learningGoalsWidget";

  Widget = (function() {

    function Widget(widget) {
      this.widget = widget;
      this.widget.data(PLUGIN_NAME, this);
      this.widget.delegate("span", "click", function() {
        var input, label;
        label = $(this);
        input = label.next();
        label.hide();
        input.show().focus();
      });
      this.widget.delegate("a.delete", "click", function(e) {
        var parent;
        e.preventDefault();
        parent = $(this).parent();
        parent.fadeOut(function() {
          parent.remove();
        });
      });
      this.widget.delegate("li.new input", "keyup", function(e) {
        var clone, input, parent;
        input = $(e.target);
        if (e.which !== 13) return;
        parent = input.parent();
        clone = parent.clone();
        clone.find("input").val("");
        clone.insertAfter(parent);
        input.hide();
        input.prev().text(input.val()).show();
        parent.removeClass("new");
        parent.next().find("input").focus();
      });
      this.widget.delegate("li:not(.new) input", "keyup", function(e) {
        var input, parent;
        input = $(e.target);
        if (e.which !== 13) return;
        parent = input.parent();
        parent.find("span").text(input.val()).show();
        input.hide();
      });
    }

    return Widget;

  })();

  (function($) {
    return $.fn.learningGoalsWidget = function(action, arg) {
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
