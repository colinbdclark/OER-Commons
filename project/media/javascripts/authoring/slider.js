(function() {
  var Slider,
    __indexOf = Array.prototype.indexOf || function(item) { for (var i = 0, l = this.length; i < l; i++) { if (i in this && this[i] === item) return i; } return -1; };

  Slider = (function() {

    function Slider(slider) {
      var _this = this;
      this.slider = slider;
      this.slides = this.slider.children(".slide");
      this.slides.css({
        float: "left",
        overflow: "hidden"
      });
      this.slider.wrap($("<div></div>"));
      this.wrapper = this.slider.parent();
      this.wrapper.css({
        position: "relative",
        overflow: "hidden"
      });
      this.slider.css({
        position: "absolute",
        top: "0px",
        left: "0px"
      });
      this.current = 0;
      this.editorArea = $("#editor-area");
      this.updateSizes();
      $(window).resize(function() {
        return _this.updateSizes();
      });
      this.buttons = $("div.authoring-head div.step-icons a");
      this.buttons.click(function(e) {
        var button;
        e.preventDefault();
        button = $(e.target);
        if (button.hasClass("active")) return;
        return _this.slideTo(button.attr("href"));
      });
      return;
    }

    Slider.prototype.updateSizes = function() {
      var doc, viewport;
      doc = $(document);
      viewport = this.viewport();
      this.width = viewport.width;
      this.height = viewport.height - this.slider.offset().top;
      this.slider.css({
        width: this.width * this.slides.length + "px",
        height: this.height + "px"
      });
      this.slides.css({
        width: this.width + "px",
        height: this.height + "px"
      });
      this.wrapper.css({
        width: this.width + "px",
        height: this.height + "px"
      });
      this.slider.css({
        left: "-" + (this.current * this.width) + "px"
      });
      this.editorArea.css({
        height: this.height - 180 + "px"
      });
    };

    Slider.prototype.slideTo = function(to) {
      var button, delta, index, prefix, slide,
        _this = this;
      slide = this.slides.filter(to);
      if (!slide.length) return;
      index = this.slides.index(slide);
      delta = this.current - index;
      if (delta === 0) return;
      if (delta > 0) {
        prefix = "+=";
      } else {
        delta = -delta;
        prefix = "-=";
      }
      button = this.buttons.filter("[href='" + to + "']");
      button.addClass("active");
      this.slider.animate({
        left: prefix + (delta * this.width)
      }, function() {
        return _this.buttons.not(button).removeClass("active");
      });
      return this.current = index;
    };

    Slider.prototype.viewport = function() {
      var a, e, viewport;
      if (__indexOf.call(window, 'innerWidth') >= 0) {
        e = window;
        a = 'inner';
      } else {
        e = document.documentElement || document.body;
        a = 'client';
      }
      viewport = {
        width: e["" + a + "Width"],
        height: e["" + a + "Height"]
      };
      return viewport;
    };

    return Slider;

  })();

  (function($) {
    return $.fn.authoringToolSlider = function(action, arg) {
      return this.each(function() {
        var $this, slider;
        $this = $(this);
        slider = $this.data("authoring-tool-slider");
        if (!slider) {
          slider = new Slider($this);
          $this.data("authoring-tool-slider", slider);
        }
        if (action) return slider[action](arg);
      });
    };
  })(jQuery);

}).call(this);
