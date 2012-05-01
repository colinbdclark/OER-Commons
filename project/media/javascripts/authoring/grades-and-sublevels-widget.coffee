PLUGIN_NAME = "gradesAndSubLevelsWidget"

class Widget
  constructor: (@widget)->
    @widget.data(PLUGIN_NAME, @)
    @fieldName = @widget.data("field-name")
    @select = @widget.find("select")
    @list = @widget.find("ul")

    @restrictOptions()

    @select.change((e)=>
      val = @select.val()
      if val == ""
        return
      @addItem(@select.children("[value='#{val}']").first())
      @select.children().first().attr("selected", "selected")
      return
    )

    @list.delegate("a.delete", "click", (e)=>
      e.preventDefault()
      @removeItem($(e.currentTarget).closest("li", @list))
      return
    )
    return

  addItem: (option)->
    value = option.attr("value")
    name = $.trim(option.text())
    existing = @list.find("input[value='#{value}']")
    if existing.length
      existing.closest("li", @list).effect("bounce")
      return
    li = $("""<li>
      <span>#{name}</span>
      <input type="hidden" name="#{@fieldName}" value="#{value}">
      <a href="#" class="delete ui-icon ui-icon-close">Delete</a>
    </li>""")
    li.appendTo(@list)
    @restrictOptions()
    return

  removeItem: (li)->
    li.remove()
    @restrictOptions()
    return

  restrictOptions: ->
    @select.children("[disabled]").removeAttr("disabled")
    @list.children().each((i, li)=>
      li = $(li)
      value = li.find("input").val()
      option = @select.children("[value='#{value}']").attr("disabled", "disabled")
      if value.match(/sublevel\.\d+/)
        option.nextUntil("[value^='sublevel']").attr("disabled", "disabled").each((i, option)=>
          option = $(option)
          value = option.attr("value")
          @list.find("input[value='#{value}']").each((i, input)=>
            $(input).closest("li", @list).remove()
            return
          )
          return
        )
      return
    )
    return

(($)->

  $.fn[PLUGIN_NAME] = (action, arg)->
    @.each(->
      $this = $(@)
      widget = $this.data(PLUGIN_NAME)
      if not widget
        widget = new Widget($this)
      if action
        widget[action](arg)
    )
)(jQuery)
