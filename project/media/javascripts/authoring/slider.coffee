
class Slider

  constructor: (@slider) ->
    @slides = @slider.children(".slide")
    @slides.css({
      float: "left",
      overflow: "hidden"
    })
    @slider.wrap($("<div></div>"))
    @wrapper = @slider.parent()
    @wrapper.css(
      position: "relative",
      overflow: "hidden"
    )
    @slider.css(
      position: "absolute",
      top: "0px",
      left: "0px"
    )
    @current = 0
    @editorArea = $("#editor-area")
    @.updateSizes()
    $(window).resize(=>
      @.updateSizes()
    )
    @buttons = $("div.authoring-head div.step-icons a")
    @buttons.click((e)=>
      e.preventDefault()
      button = $(e.target)
      if button.hasClass("active")
        return
      @slideTo(button.attr("href"))
    )
    return

  updateSizes: ->
    doc = $(document)
    viewport = @.viewport()
    @width = viewport.width
    @height = viewport.height - @slider.offset().top
    @slider.css(
      width: @width * @slides.length + "px",
      height: @height + "px"
    )
    @slides.css(
      width: @width + "px",
      height: @height + "px"
    )
    @wrapper.css(
      width: @width + "px",
      height: @height + "px"
    )
    @slider.css(
      left: "-" + (@current * @width) + "px"
    )
    @editorArea.css(
      height: @height - 180 + "px"
    )
    return

  slideTo: (to) ->
    slide = @slides.filter(to)
    if not slide.length
      return
    index = @slides.index(slide)
    delta = (@current - index)
    if delta == 0
      return
    if delta > 0
      prefix = "+="
    else
      delta = -delta
      prefix = "-="


    button = @buttons.filter("[href='#{to}']")
    button.addClass("active")
    @slider.animate(
      left: prefix + (delta * @width)
    =>
      @buttons.not(button).removeClass("active")
    )

    @current = index

  viewport: ->
    if 'innerWidth' in window
      e = window
      a = 'inner'
    else
      e = document.documentElement || document.body
      a = 'client'
    viewport =
      width: e["#{a}Width"],
      height: e["#{a}Height"]
    return viewport

(($)->

  $.fn.authoringToolSlider = (action, arg)->
    @.each(->
      $this = $(@)
      slider = $this.data("authoring-tool-slider")
      if not slider
        slider = new Slider($this)
        $this.data("authoring-tool-slider", slider)
      if action
        slider[action](arg)
    )

)(jQuery)
