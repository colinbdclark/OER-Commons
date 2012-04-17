window.initGlobalHeader = ->
  header = $("header.global")
  dropdown = header.find("li.dropdown")
  dropdown.find("b.caret").click((e)->
    e.preventDefault()
    e.stopPropagation()
    dropdown = $(e.target).closest("li.dropdown")
    dropdown.toggleClass("active")
    return
  )
  dropdown.find("ul.dropdown-menu").click((e)->
    e.stopPropagation()
    return
  )
  $(document).click((e)->
    dropdown.removeClass("active")
    return
  )

  searchBox = $("#global-search-box")
  searchBoxInput = searchBox.find("input[type='text']")
  searchBox.find("form").submit((e)->
    value = $.trim(searchBoxInput.val())
    if value == ""
      e.preventDefault()
    return
  )

  return
