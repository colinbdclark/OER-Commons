function initStepButtons() {
  var $form = $("form.authoring-form");
  var $next = $form.find(":hidden[name='next']");
  $form.find("div.authoring-head div.step-icons a").click(function (e) {
    e.preventDefault();
    var $this = $(this);
    if ($this.hasClass("active")) {
      return;
    }
    $next.val($this.attr("href"));
    $form.submit();
  });
  $form.find("div.buttons").find("a.prev,a.next").click(function(e) {
    e.preventDefault();
    var $this = $(this);
    $next.val($this.attr("href"));
    $form.submit();
  });
}
