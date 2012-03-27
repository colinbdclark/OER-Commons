(function() {
  var Slider, Tool, UserMenu,
    __indexOf = Array.prototype.indexOf || function(item) { for (var i = 0, l = this.length; i < l; i++) { if (i in this && this[i] === item) return i; } return -1; };

  Slider = (function() {

    function Slider() {
      var _this = this;
      this.slider = $("#slider");
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

    Slider.prototype.slideTo = function(to, animate) {
      var button, delta, index, prefix, slide,
        _this = this;
      if (animate == null) animate = true;
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
      if (animate) {
        button.addClass("active");
        this.slider.animate({
          left: prefix + (delta * this.width)
        }, function() {
          return _this.buttons.not(button).removeClass("active");
        });
      } else {
        this.buttons.removeClass("active");
        button.addClass("active");
        this.slider.css({
          left: prefix + (delta * this.width)
        });
      }
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

  UserMenu = (function() {

    function UserMenu() {
      var _this = this;
      this.menu = $("#user-menu");
      this.toggle = this.menu.find("a.toggle");
      this.toggle.click(function(e) {
        e.preventDefault();
        e.stopPropagation();
        return _this.menu.toggleClass("opened");
      });
      $(document).click(function() {
        return _this.menu.removeClass("opened");
      });
    }

    return UserMenu;

  })();

  Tool = (function() {

    function Tool(hideSubmitStep) {
      var actions, errorSlide, errors, previewBtn, saveBtn,
        _this = this;
      this.hideSubmitStep = hideSubmitStep;
      this.form = $("form.authoring-form");
      this.slider = new Slider();
      this.userMenu = new UserMenu();
      this.writeStep = new WriteStep(this);
      this.describeStep = new DescribeStep(this);
      if (!this.hideSubmitStep) this.submitStep = new SubmitStep(this);
      this.title = $("#material-title");
      this.titleInput = $("#id_title");
      this.title.editable(function(value) {
        _this.titleInput.val(value);
        return value;
      }, {
        cssclass: "title-input",
        width: "none",
        height: "none",
        onblur: "submit",
        tooltip: "Click to edit title...",
        placeholder: "Click to edit title..."
      });
      actions = $("div.authoring-head div.actions a");
      saveBtn = actions.filter(".save");
      saveBtn.click(function(e) {
        e.preventDefault();
        _this.save();
      });
      previewBtn = actions.filter(".preview");
      previewBtn.click(function(e) {
        e.preventDefault();
        _this.writeStep.preSave();
        _this.form.attr("action", _this.form.attr("action") + "?preview");
        _this.form.submit();
      });
      this.form.find("div.slide div.slider-buttons a").click(function(e) {
        var btn;
        e.preventDefault();
        btn = $(e.currentTarget);
        if (btn.hasClass("publish")) {
          _this.publish();
        } else {
          _this.slider.slideTo(btn.attr("href"));
        }
      });
      errors = $("label.error");
      if (errors.length) {
        errorSlide = errors.first().closest("div.slide");
        this.slider.slideTo("#" + errorSlide.attr("id"), false);
      }
    }

    Tool.prototype.save = function() {
      var _this = this;
      this.writeStep.preSave();
      oer.status_message.clear();
      $.post(this.form.attr("action"), this.form.serialize(), function(response) {
        if (response.status === "success") {
          return oer.status_message.success(response.message, true);
        } else {
          return oer.status_message.error(response.message, false);
        }
      });
    };

    Tool.prototype.autosave = function() {
      var _this = this;
      return setTimeout(function() {
        _this.save();
        return _this.autosave();
      }, 30 * 1000);
    };

    Tool.prototype.publish = function() {
      this.writeStep.preSave();
      this.form.submit();
    };

    return Tool;

  })();

  window.AuthoringTool = Tool;

}).call(this);
