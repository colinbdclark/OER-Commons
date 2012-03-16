class Slider

  constructor: ->
    @slider = $("#slider")
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

  slideTo: (to, animate=true) ->
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
    if animate
      button.addClass("active")
      @slider.animate(
        left: prefix + (delta * @width)
      =>
        @buttons.not(button).removeClass("active")
      )
    else
      @buttons.removeClass("active")
      button.addClass("active")
      @slider.css(
        left: prefix + (delta * @width)
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


# TODO: user bootstrap dropdown for this
class UserMenu

  constructor: ->
    @menu = $("#user-menu")
    @toggle = @menu.find("a.toggle")
    @toggle.click((e)=>
      e.preventDefault()
      e.stopPropagation()
      @menu.toggleClass("opened")
    )
    $(document).click(=>
      @menu.removeClass("opened")
    )


class Tool
  constructor: (@updatePublished)->
    @form = $("form.authoring-form")
    @slider = new Slider()
    @userMenu = new UserMenu()
    @writeStep = new WriteStep(@)
    @describeStep = new DescribeStep(@)
    if not @updatePublished
      @submitStep = new SubmitStep(@)

    @title = $("#material-title")
    @titleInput = $("#id_title")

    @title.editable(
      (value)=>
        @titleInput.val(value)
        return value
      cssclass: "title-input",
      width: "none",
      height: "none",
      onblur: "submit",
      tooltip: "Click to edit title...",
      placeholder: "Click to edit title..."
    )

    actions = $("div.authoring-head div.actions a")
    saveBtn = actions.filter(".save")
    saveBtn.click((e)=>
      e.preventDefault()
      @.save()
      return
    )

    previewBtn = actions.filter(".preview")
    previewBtn.click((e)=>
      e.preventDefault()
      @writeStep.preSave()
      @form.attr("action", @form.attr("action") + "?preview")
      @form.submit()
      return
    )

    @form.find("div.slide div.slider-buttons a").click((e)=>
      e.preventDefault()
      btn = $(e.currentTarget)
      if btn.hasClass("publish")
        @.publish()
      else
        @slider.slideTo(btn.attr("href"))
      return
    )

    errors =  $("label.error")
    if errors.length
      errorSlide = errors.first().closest("div.slide")
      @slider.slideTo("#" + errorSlide.attr("id"), false)

  save:->
    @writeStep.preSave()
    oer.status_message.clear()
    $.post(@form.attr("action"), @form.serialize(), (response)=>
      if response.status == "success"
        oer.status_message.success(response.message, true)
      else
        oer.status_message.error(response.message, false)
    )
    return

  publish:->
    @writeStep.preSave()
    @form.submit()
    return


window.AuthoringTool = Tool
