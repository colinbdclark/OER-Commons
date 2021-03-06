class Slider

  constructor: ->
    @slider = $("#slider")
    @slides = @slider.children(".slide")
    @slides.css(
      float: "left",
      overflow: "hidden"
    )
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
    @desribeArea = $("#step-describe div.columns-wrapper")
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
    @desribeArea.css(
      height: @height - 125 + "px"
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

  AUTOSAVE_INTERVAL: 5 # 30 seconds

  constructor: (@resubmit)->
    @form = $("form.authoring-form")
    @slider = new Slider()
    @userMenu = new UserMenu()
    @writeStep = new WriteStep(@)
    @describeStep = new DescribeStep(@)
    @submitStep = new SubmitStep(@)

    @title = $("#material-title")
    @titleInput = $("#id_title")
    @offlineMessage = $("#offline-message")

    @checksum = @form.find("input[name='checksum']")
    @checksumMessage = @form.find("#checksum-message")
    @checksumMessage.find("a.force-save").click((e)=>
      e.preventDefault()
      @save(false, true)
    )

    @deleteForm = $("#delete-draft-form")
    @deleteConfirmation = @form.find("#delete-confirmation")
    @deleteConfirmation.find("a.cancel").click((e)=>
      e.preventDefault()
      @deleteConfirmation.addClass("hide")
    )
    @deleteConfirmation.find("a.confirm").click((e)=>
      e.preventDefault()
      @deleteForm.submit()
    )

    @globalWarnings = $("div.global-warning")

    $("#user-menu a.delete-draft").click((e)=>
      @globalWarnings.not(@deleteConfirmation).addClass("hide")
      @deleteConfirmation.removeClass("hide")
    )

    @savedData = null

    @title.find("span.inner").editable(
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

    $(document).ajaxError((event, xhr, settings, error)=>
      if not xhr.status
        @globalWarnings.not(@offlineMessage).addClass("hide")
        @offlineMessage.removeClass("hide")
      else
        @offlineMessage.addClass("hide")
        oer.status_message.clear()
        oer.status_message.error("An error occured.")
    )

    $(document).ajaxSuccess((event, xhr, settings, error)=>
      @offlineMessage.addClass("hide")
    )

    $("a[data-tooltip]").qtip(
      content:
        attr: "data-tooltip"
      style:
        classes: "ui-tooltip-authoring"
        tip: false
      position:
        my: "top center"
        at: "bottom center"
        adjust:
          y: 5
    )
    $("a[data-tooltip]").filter(".disabled").qtip("disable")

    @autosave()

  save: (autosave=false,force=false)->
    @writeStep.preSave()
    data = @form.serialize()
    formData = data.replace(/checksum=.+?&/g, "")
    if force
      data += "&force_save=yes"

    if autosave and formData == @savedData
      return

    oer.status_message.clear()
    oer.status_message.message("Saving...", "")

    $.post(@form.attr("action"), data, (response)=>
      if response.status == "success"
        oer.status_message.clear()
        oer.status_message.success("All changes saved")
        @checksum.val(response.checksum)
        @checksumMessage.addClass("hide")
        @savedData = formData
      else
        oer.status_message.clear()
        oer.status_message.error(response.message)
        if response.reason == "checksum"
          @globalWarnings.not(@checksumMessage).addClass("hide")
          @checksumMessage.removeClass("hide")
        @savedData = null
    )
    return

  autosave:->
    setTimeout(=>
      @save(true)
      @autosave()
    , @AUTOSAVE_INTERVAL * 1000)

  publish:->
    @writeStep.preSave()
    @form.submit()
    return


window.AuthoringTool = Tool
