oer.rubrics_manage = {};

oer.rubrics_manage.link_formatter = function(url_field) {
  return function(value, rowData) {
    return '<a href="' + rowData[url_field] + '">' + value + '</a>';
  };
};

oer.rubrics_manage.format_resource_name = function(value, rowData) {
  var out = '<a href="' + rowData.manage_resource_url + '">' + value + '</a>';
  if (rowData.oer_url !== "") {
    out = '<a href="' + rowData.oer_url + '" class="oer-url" target="_blank"></a> ' + out;
  }
  return out;
};

oer.rubrics_manage.format_comment = function(value, rowData) {
  if (value) {
    return '<span class="has-comments"></span>';
  }
  return "";
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
        {field: "title", title: "Resource Name", width: 70, sortable: true, formatter: oer.rubrics_manage.format_resource_name},
        {field: "url", title: "Resource URL", width: 70, sortable: true},
        {field: "institution__name", title: "Institution", width: 70, sortable: true},
        {field: "hostname", title: "Host", width: 50, sortable: true},
        {field: "last_evaluated", title: "Last Evaluated", width: 50, sortable: true, formatter: oer.rubrics_manage.link_formatter("manage_user_url")},
        {field: "evaluator", title: "Latest Evaluator", width: 30, sortable: true, formatter: oer.rubrics_manage.link_formatter("manage_user_url")},
        {field: "r1", title: "R1", width: 10, sortable: true, align: "center"},
        {field: "r2", title: "R2", width: 10, sortable: true, align: "center"},
        {field: "r3", title: "R3", width: 10, sortable: true, align: "center"},
        {field: "r4", title: "R4", width: 10, sortable: true, align: "center"},
        {field: "r5", title: "R5", width: 10, sortable: true, align: "center"},
        {field: "r6", title: "R6", width: 10, sortable: true, align: "center"},
        {field: "r7", title: "R7", width: 10, sortable: true, align: "center"},
        {field: "comments", title: "Comments", width: 10, sortable: true, formatter: oer.rubrics_manage.format_comment}
      ]
    ]
  });

  var $search = $("input[name='search']");
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

  $grade_level.change(reload_grid);
  $general_subject.change(reload_grid);

};

oer.rubrics_manage.update_grid_actions = function($grid) {
  var rowcount = $grid.datagrid('getRows').length;
  for (var i = 0; i < rowcount; i++) {
    $grid.datagrid('updateRow', {
      index: i,
      row: {action: ''}
    });
  }
};

oer.rubrics_manage.grid_actions_column = {
  field: 'action', title: 'Action', width: 30, align: 'center',
  formatter: function(value, row, index) {
    if (row.editing) {
      var s = '<a href="#" class="save" data-id="' + row.id + '" data-index="' + index + '">Save</a> ';
      var c = '<a href="#" class="cancel" data-index="' + index + '">Cancel</a>';
      return s + c;
    } else {
      var e = '<a href="#" class="edit" data-index="' + index + '">Edit</a> ';
      var d = '<a href="#" class="delete" data-id="' + row.id + '" data-index="' + index + '">Delete</a>';
      return e + d;
    }
  }
};

oer.rubrics_manage.grid_score_editor = {
  type: "numberbox",
  options: {
    min: 0,
    max: 3
  }
};

oer.rubrics_manage.init_grid_actions = function($grid) {
  var $panel = $grid.datagrid("getPanel");

  $panel.delegate("a.edit", "click", function(e) {
    e.preventDefault();
    $grid.datagrid("beginEdit", $(this).data("index"));
  });

  $panel.delegate("a.cancel", "click", function(e) {
    e.preventDefault();
    $grid.datagrid("cancelEdit", $(this).data("index"));
  });

  $panel.delegate("a.delete", "click", function(e) {
    e.preventDefault();
    var $this = $(this);
    var index = $this.data("index");
    var id = $this.data("id");
    $.messager.confirm('Confirm', 'Are you sure?', function(r) {
      if (r) {
        $grid.datagrid("deleteRow", index);
        $.post($grid.data("delete-url"), {id: id});
      }
    });
  });

  $panel.delegate("a.save", "click", function(e) {
    e.preventDefault();
    var $this = $(this);
    var index = $this.data("index");
    $grid.datagrid("endEdit", index);
  });
};

oer.rubrics_manage.init_resource = function() {
  var $grid = $("#grid");

  $grid.datagrid({
    url: $grid.data("url"),
    pagination: true,
    fitColumns: true,
    pageSize: 20,
    idField: "id",
    columns: [
      [
        {field: "hostname", title: "Host", width: 70, sortable: true},
        {field: "timestamp", title: "Evaluation Date", width: 70, sortable: true},
        {field: "evaluator", title: "Evaluator", width: 70, sortable: true, formatter: oer.rubrics_manage.link_formatter("manage_user_url")},
        {field: "ip", title: "IP Address", width: 50, sortable: true},
        {field: "r1", title: "R1", width: 10, sortable: true, align: "center"},
        {field: "r2", title: "R2", width: 10, sortable: true, align: "center", editor: oer.rubrics_manage.grid_score_editor},
        {field: "r3", title: "R3", width: 10, sortable: true, align: "center", editor: oer.rubrics_manage.grid_score_editor},
        {field: "r4", title: "R4", width: 10, sortable: true, align: "center", editor: oer.rubrics_manage.grid_score_editor},
        {field: "r5", title: "R5", width: 10, sortable: true, align: "center", editor: oer.rubrics_manage.grid_score_editor},
        {field: "r6", title: "R6", width: 10, sortable: true, align: "center", editor: oer.rubrics_manage.grid_score_editor},
        {field: "r7", title: "R7", width: 10, sortable: true, align: "center", editor: oer.rubrics_manage.grid_score_editor},
        {field: "average", title: "Average Score", width: 30, sortable: true, align: "center"},
        oer.rubrics_manage.grid_actions_column
      ]
    ],
    onBeforeEdit: function(index, row) {
      row.editing = true;
      oer.rubrics_manage.update_grid_actions($grid);
    },
    onAfterEdit: function(index, row, changes) {
      row.editing = false;
      oer.rubrics_manage.update_grid_actions($grid);
      if (!$.isEmptyObject(changes)) {
        var data = {id: row.id};
        $.extend(data, changes);
        $.post($grid.data("edit-url"), data);
      }
    },
    onCancelEdit: function(index, row) {
      row.editing = false;
      oer.rubrics_manage.update_grid_actions($grid);
    }
  });

  oer.rubrics_manage.init_grid_actions($grid);
};

oer.rubrics_manage.init_user = function() {
  var $grid = $("#grid");

  $grid.datagrid({
    url: $grid.data("url"),
    pagination: true,
    fitColumns: true,
    pageSize: 20,
    idField: "id",
    columns: [
      [
        {field: "hostname", title: "Host", width: 70, sortable: true},
        {field: "timestamp", title: "Evaluation Date", width: 70, sortable: true},
        {field: "ip", title: "IP Address", width: 50, sortable: true},
        {field: "title", title: "Resource Name", width: 70, sortable: true, formatter: oer.rubrics_manage.link_formatter("manage_resource_url")},
        {field: "url", title: "Resource URL", width: 70, sortable: true},
        {field: "institution__name", title: "Institution", width: 70, sortable: true},
        {field: "r1", title: "R1", width: 10, sortable: true, align: "center"},
        {field: "r2", title: "R2", width: 10, sortable: true, align: "center", editor: oer.rubrics_manage.grid_score_editor},
        {field: "r3", title: "R3", width: 10, sortable: true, align: "center", editor: oer.rubrics_manage.grid_score_editor},
        {field: "r4", title: "R4", width: 10, sortable: true, align: "center", editor: oer.rubrics_manage.grid_score_editor},
        {field: "r5", title: "R5", width: 10, sortable: true, align: "center", editor: oer.rubrics_manage.grid_score_editor},
        {field: "r6", title: "R6", width: 10, sortable: true, align: "center", editor: oer.rubrics_manage.grid_score_editor},
        {field: "r7", title: "R7", width: 10, sortable: true, align: "center", editor: oer.rubrics_manage.grid_score_editor},
        {field: "average", title: "Average Score", width: 30, sortable: true, align: "center"},
        oer.rubrics_manage.grid_actions_column
      ]
    ],
    onBeforeEdit: function(index, row) {
      row.editing = true;
      oer.rubrics_manage.update_grid_actions($grid);
    },
    onAfterEdit: function(index, row, changes) {
      row.editing = false;
      oer.rubrics_manage.update_grid_actions($grid);
      if (!$.isEmptyObject(changes)) {
        var data = {id: row.id};
        $.extend(data, changes);
        $.post($grid.data("edit-url"), data);
      }
    },
    onCancelEdit: function(index, row) {
      row.editing = false;
      oer.rubrics_manage.update_grid_actions($grid);
    }
  });

  oer.rubrics_manage.init_grid_actions($grid);
};
