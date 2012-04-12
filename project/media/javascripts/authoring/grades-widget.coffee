PLUGIN_NAME = "gradesWidget"

class Widget
  constructor: (@widget)->
    @widget.data(PLUGIN_NAME, @)
    @fieldName = @widget.data("field-name")
    @select = @widget.find("select")
    @list = @widget.find("ul")

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
    name = option.text()
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
    return

  removeItem: (li)->
    li.remove()
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
