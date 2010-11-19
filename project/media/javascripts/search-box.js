$( function() {
    var searchbox = $(".search-box input[name='f.search']");
    searchbox.focus( function() {
        if (this.value == "Enter Search")
            this.value = "";
    });
    searchbox.blur( function() {
        if (this.value == "")
            this.value = "Enter Search";
    });
    $(".search-box form").submit( function() {
        if (searchbox.attr("value") == "" || searchbox.attr("value") == "Enter Search")
            return false;
        return true;
    });
});
