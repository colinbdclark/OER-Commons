oer.myitems.index = {};

oer.myitems.index.init_action_panel = function() {
  var $form = $("div.action-panel form");
  $form.find("select[name='batch_size']").change(function() {
    $form.submit();
  });
  $form.find("select[name='sort_by']").change(function() {
    $form.submit();
  });
};

oer.myitems.index.init = function() {
  
  oer.myitems.index.init_action_panel();
  oer.materials.index.init_actions_menus();
  
  oer.collapsibles.init($("#content"));
  
}

oer.myitems.index.init_saved_items = function() {
  var $confirmation = $("div.unsave-confirmation");
  
  $confirmation.find("a.cancel").click(
    function() {
      $confirmation.hide();
      return false;
    }
  );

  $confirmation.find("a.unsave").click(
    function() {
      var $item = $confirmation.closest("div.item");
      $confirmation.hide().detach();
      var url = $item.find("a.unsave-item").attr("href")
      $.post(url,
        function() {
          $item.fadeOut(500);
        }, "application/json");
      return false;
    }
  );
  
  $("#content a.unsave-item").click(
    function() {
      var $this = $(this);
      $details = $this.closest("div.item").find("div.details");
      $confirmation.detach().appendTo($details).show();
      return false;
    }
  );
}
