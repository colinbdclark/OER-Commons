oer.search_box = {};

oer.search_box.init = function() {
  var $search_box = $("#global-search-box");
  var $input = $search_box.find("input[name='f.search']");
  $input.focus(
    function() {
      if ($input.val() === "Enter Search") {
        $input.val("");
      }
    }
  ).blur(
    function() {
      if ($input.val() === "") {
        $input.val("Enter Search");
      }
    }
  );
  $search_box.find("form").submit(
    function(e) {
      var value = $input.val();
      if (value === "" || value === "Enter Search") {
        e.preventDefault();
      }
    }
  );
};
