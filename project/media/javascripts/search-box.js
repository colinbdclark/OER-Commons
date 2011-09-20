oer.search_box = {};

oer.search_box.init = function() {
  var $search_box = $("#global-search-box");
  var $input = $search_box.find("input[name='f.search']");
  $search_box.find("form").submit(function(e) {
    var value = $input.val().trim();
    if (value === "") {
      e.preventDefault();
    }
  });
};
