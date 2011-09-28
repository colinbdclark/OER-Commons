oer.rubrics_manage = {};

oer.rubrics_manage.link_formatter = function(url_field) {
  return function(value, rowData) {
    return '<a href="' + rowData[url_field] + '">' + value + '</a>';
  };
};

oer.rubrics_manage.init_index = function() {
  var $grid = $("#grid");

  $grid.datagrid({
    url: $grid.data("url"),
    pagination: true,
    fitColumns: true,
    pageSize: 20,
    toolbar: "#toolbar",
    columns: [
      [
        {field: "title", title: "Resource Name", width: 70, sortable: true, formatter: oer.rubrics_manage.link_formatter("manage_resource_url")},
        {field: "url", title: "Resource URL", width: 70, sortable: true},
        {field: "institution__name", title: "Institution", width: 70, sortable: true},
        {field: "hostname", title: "Host", width: 50, sortable: true},
        {field: "last_evaluated", title: "Last Evaluated", width: 50, sortable: true, formatter: oer.rubrics_manage.link_formatter("manage_user_url")},
        {field: "evaluator", title: "Latest Evaluator", width: 30, sortable: true, formatter: oer.rubrics_manage.link_formatter("manage_user_url")},
        {field: "ip", title: "IP Address", width: 20, sortable: true},
        {field: "total_evaluations", title: "Total Ev.", width: 20, sortable: true, align: "center", formatter: oer.rubrics_manage.link_formatter("manage_resource_url")},
        {field: "r1", title: "R1", width: 10, sortable: true, align: "center"},
        {field: "r2", title: "R2", width: 10, sortable: true, align: "center"},
        {field: "r3", title: "R3", width: 10, sortable: true, align: "center"},
        {field: "r4", title: "R4", width: 10, sortable: true, align: "center"},
        {field: "r5", title: "R5", width: 10, sortable: true, align: "center"},
        {field: "r6", title: "R6", width: 10, sortable: true, align: "center"},
        {field: "r7", title: "R7", width: 10, sortable: true, align: "center"}
      ]
    ]
  });

  var $search = $("input[name='search']");
  var $rubric = $("select[name='rubric']");
  var $grade_level = $("select[name='grade_level']");
  var $general_subject = $("select[name='general_subject']");


  var reload_grid = function() {
    var $from_date = $("input[name='from_date']");
    var $until_date = $("input[name='until_date']");

    var params = {};
    var search = $.trim($search.val());
    if (search !== "") {
      params.search = search;
    }
    var from_date = $.trim($from_date.val());
    if (from_date !== "") {
      params.from_date = from_date;
    }
    var until_date = $.trim($until_date.val());
    if (until_date !== "") {
      params.until_date = until_date;
    }

    var rubric = $rubric.val();
    if (rubric !== "") {
      params.rubric = rubric;
    }

    var grade_level = $grade_level.val();
    if (grade_level !== "") {
      params.grade_level = grade_level;
    }

    var general_subject = $general_subject.val();
    if (general_subject !== "") {
      params.general_subject = general_subject;
    }

    $grid.datagrid("load", params);
  };

  $search.keypress(function(e) {
    if (e.which == 13) {
      reload_grid();
    }
  });

  $("#toolbar input.date").datebox({
    onSelect: reload_grid
  });

  $rubric.change(reload_grid);
  $grade_level.change(reload_grid);
  $general_subject.change(reload_grid);

};

oer.rubrics_manage.init_resource = function() {
  var $grid = $("#grid");

  $grid.datagrid({
    url: $grid.data("url"),
    pagination: true,
    fitColumns: true,
    pageSize: 20,
    columns: [
      [
        {field: "hostname", title: "Host", width: 70, sortable: true},
        {field: "timestamp", title: "Evaluation Date", width: 70, sortable: true},
        {field: "user__username", title: "Evaluator", width: 70, sortable: true, formatter: oer.rubrics_manage.link_formatter("manage_user_url")},
        {field: "ip", title: "IP Address", width: 50, sortable: true},
        {field: "r1", title: "R1", width: 10, sortable: true, align: "center"},
        {field: "r2", title: "R2", width: 10, sortable: true, align: "center"},
        {field: "r3", title: "R3", width: 10, sortable: true, align: "center"},
        {field: "r4", title: "R4", width: 10, sortable: true, align: "center"},
        {field: "r5", title: "R5", width: 10, sortable: true, align: "center"},
        {field: "r6", title: "R6", width: 10, sortable: true, align: "center"},
        {field: "r7", title: "R7", width: 10, sortable: true, align: "center"},
        {field: "average", title: "Average Score", width: 30, sortable: true, align: "center"}
      ]
    ]
  });
};


oer.rubrics_manage.init_user = function() {
  var $grid = $("#grid");

  $grid.datagrid({
    url: $grid.data("url"),
    pagination: true,
    fitColumns: true,
    pageSize: 20,
    columns: [
      [
        {field: "hostname", title: "Host", width: 70, sortable: true},
        {field: "timestamp", title: "Evaluation Date", width: 70, sortable: true},
        {field: "ip", title: "IP Address", width: 50, sortable: true},
        {field: "title", title: "Resource Name", width: 70, sortable: true, formatter: oer.rubrics_manage.link_formatter("manage_resource_url")},
        {field: "url", title: "Resource URL", width: 70, sortable: true},
        {field: "institution__name", title: "Institution", width: 70, sortable: true},
        {field: "r1", title: "R1", width: 10, sortable: true, align: "center"},
        {field: "r2", title: "R2", width: 10, sortable: true, align: "center"},
        {field: "r3", title: "R3", width: 10, sortable: true, align: "center"},
        {field: "r4", title: "R4", width: 10, sortable: true, align: "center"},
        {field: "r5", title: "R5", width: 10, sortable: true, align: "center"},
        {field: "r6", title: "R6", width: 10, sortable: true, align: "center"},
        {field: "r7", title: "R7", width: 10, sortable: true, align: "center"},
        {field: "average", title: "Average Score", width: 30, sortable: true, align: "center"}
      ]
    ]
  });
};
