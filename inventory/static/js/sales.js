$(document).ready(function () {
  var counter = 1;

  $("#addrow").on("click", function () {
    var newRow = $("<tr>");
    var cols = "";

    cols +=
      '<td><input type="text" class="form-control" name="name' +
      counter +
      '"/></td>';
    cols +=
      '<td><input type="number" class="form-control" value="0" name="quantity' +
      counter +
      '"/></td>';

    cols +=
      '<td><button class="btnDel btn btn-danger"><i class="fa fa-times"></i></button></td>';
    newRow.append(cols);
    $("table.sales-list").append(newRow);
    counter++;
  });

  $("table.sales-list").on("click", ".btnDel", function (event) {
    $(this).closest("tr").remove();
    counter -= 1;
  });
});
