$(function() {
  
  $form = $("form[name='index-filters']");
  
  $(".action-panel.materials select[name='batch_size']").change(function() {
    $this = $(this);
    $form.find("input[name='batch_size']").val($this.val());
    $form.submit();
  });
  
  $(".action-panel.materials select[name='sort_by']").change(function() {
    $this = $(this);
    $form.find("input[name='sort_by']").val($this.val());
    $form.submit();
  });
  
  $("form[name='index-filters'] .search input[type='submit']").click(function() {
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

  $(".top-keywords .see-more").click(function() {
    $(this).hide();
    $(".top-keywords .top").hide();
    $(".top-keywords .all").show();
    return false;
  });

  $(".materials-index h3 a.item-link").click(function() {
    $form.attr("action", $(this).attr("href")).attr("method", "post");
    $form.find("input[name='index_path']").attr("disabled", false);
    $form.submit();
    return false;
  });

});
