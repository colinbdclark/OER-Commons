oer.materials.index = {};

oer.materials.index.init = function() {
  
  var $filters_portlet = $("div.portlet.index-filters");
  var $top_keywords_portlet = $("div.portlet.top-keywords");
  var $form = $filters_portlet.find("form[name='index-filters']");
  var $action_panel = $("div.action-panel");
  
  $action_panel.find("select[name='batch_size']").change(function() {
    $this = $(this);
    $form.find("input[name='batch_size']").val($this.val());
    $form.submit();
  });
  
  $action_panel.find("select[name='sort_by']").change(function() {
    $this = $(this);
    $form.find("input[name='sort_by']").val($this.val());
    $form.submit();
  });
  
  $form.find("div.search input[type='submit']").click(function() {
    if ($form.find("input[name='f.search']").val() != "") {
      $form.find("input[name='sort_by']").val("search");
    }
  });

  $form.submit(function() {
    $form = $(this);
    $form.find(".filter").each(function() {
      $filter = $(this);
      if ($filter.find("dd :checkbox").length == $filter.find("dd :checkbox[checked=true]").length) {
        $filter.find(":checkbox").attr("disabled", true);
      }
    });
    if ($form.find("input[name='f.search']").val() == "") {
      $form.find("input[name='f.search']").attr("disabled", true)
    }
  });

  $form.find(".filter dd :checkbox").click(function() {
    $checkbox = $(this);
    $filter = $checkbox.parents(".filter").first();
    if ($checkbox.attr("checked")) {
      if ($filter.find("dd :checkbox").length == $filter.find("dd :checkbox[checked=true]").length) {
        $filter.find("dt :checkbox").attr("checked", true);
      }
    } else {
      $filter.find("dt :checkbox").attr("checked", false);
    }
  });

  $form.find(".filter dt :checkbox").click(function() {
    $checkbox = $(this);
    $filter = $checkbox.parents(".filter").first();
    $filter.find(".collapsed").removeClass("collapsed").addClass("expanded");
    if ($checkbox.attr("checked")) {
      $filter.find("dd :checkbox").attr("checked", true);
    } else {
      $filter.find("dd :checkbox").attr("checked", false);
    }
  });

  $top_keywords_portlet.find("a.see-more").click(function() {
    $(this).hide();
    $top_keywords_portlet.find("div.top").hide();
    $top_keywords_portlet.find("div.all").show();
    return false;
  });

  $("#content div.materials-index h3 a.item-link").click(function() {
    $form.attr("action", $(this).attr("href")).attr("method", "post");
    $form.find("input[name='index_path']").attr("disabled", false);
    $form.submit();
    return false;
  });
  
  oer.collapsibles.init($("#content"));
  oer.collapsibles.init($filters_portlet);
  
  $filters_portlet.find("dl.cou a.tooltip-button").cluetip({local:true, arrows: true, width: 300});
  $filters_portlet.find("dl.grade-levels a.tooltip-button").cluetip({local:true, arrows: true, width: 200});
  
  $("#content dl.actions dt a").click(
    function() {
      var $menu = $(this).closest("dl.actions");
      $("#content dl.actions").not($menu).removeClass("active");
      if ($menu.hasClass("active")) {
        $menu.removeClass("active");
      } else {
        $menu.addClass("active");    
      }
      return false;
    }
  );
  
  $(document).click(
    function(event) {
      $("#content dl.actions").removeClass("active");
    }
  );
  
  $("#content dl.actions a.save-item").click(
    function() {
      var $this = $(this)
      $.post($this.attr("href"),
        function(data) {
          var $details = $this.closest("div.item").find("div.details");
          $details.find("div.message").remove();
          $("<div></div>").addClass("message").text(data).appendTo($details).delay(3000).fadeOut(1000, function() {$(this).remove();});
        }, "application/json");
      var $menu = $this.closest("dl.actions");
      $menu.removeClass("active");
      return false;
    }
  );
  

}
