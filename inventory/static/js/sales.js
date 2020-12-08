$(document).ready(function () {
  var counter = 0;

  $("#addrow").on("click", function (e) {
    var newRow = $("<tr>");
    var cols = "";

    var product = $("#add_product").val();
    var quantity = $("#add_quantity").val();

    cols +=
      '<td><input type="text" class="form-control" value="' +
      product +
      '" name="product' +
      counter +
      '" />' +
      "</td>";

    cols +=
      '<td><input type="number" class="form-control" value="' +
      quantity +
      '" name="quantity' +
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
