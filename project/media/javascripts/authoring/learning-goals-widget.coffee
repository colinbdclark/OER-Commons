PLUGIN_NAME = "learningGoalsWidget"

class Widget
  constructor: (@widget)->
    @widget.data(PLUGIN_NAME, @)
    @widget.delegate("span", "click", ->
      label = $(@)
      input = label.next()
      label.hide()
      input.show()
      return
    )
    @widget.delegate("a.delete", "click", (e)->
      e.preventDefault()
      parent = $(@).parent()
      parent.fadeOut(->
        parent.remove()
        return
      )
      return
    )
    @widget.delegate("li.new input", "keyup", (e)->
      input = $(e.target)
      if e.which != 13
        return
      parent = input.parent()
      clone = parent.clone()
      clone.find("input").val("")
      clone.insertAfter(parent)
      input.show()
      input.prev().hide()
      parent.removeClass("new")
      parent.next().find("input").focus()
      return
    )
    @widget.delegate("li:not(.new) input", "keyup", (e)->
      input = $(e.target)
      if e.which != 13
        return
      input.parent().next().find("input").focus()
      return
    )
(($)->

  $.fn.learningGoalsWidget = (action, arg)->
    @.each(->
      $this = $(@)
      widget = $this.data(PLUGIN_NAME)
      if not widget
        widget = new Widget($this)
      if action
        widget[action](arg)
    )
)(jQuery)
