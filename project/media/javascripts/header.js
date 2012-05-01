(function() {

  window.initGlobalHeader = function() {
    var dropdown, header, searchBox, searchBoxInput;
    header = $("header.global");
    dropdown = header.find("li.dropdown");
    dropdown.find("b.caret").click(function(e) {
      e.preventDefault();
      e.stopPropagation();
      dropdown = $(e.target).closest("li.dropdown");
      dropdown.toggleClass("active");
    });
    dropdown.find("ul.dropdown-menu").click(function(e) {
      e.stopPropagation();
    });
    $(document).click(function(e) {
      dropdown.removeClass("active");
    });
    searchBox = $("#global-search-box");
    searchBoxInput = searchBox.find("input[type='text']");
    searchBox.find("form").submit(function(e) {
      var value;
      value = $.trim(searchBoxInput.val());
      if (value === "") e.preventDefault();
    });
  };

}).call(this);
