function ajaxScript() {
   // var input = $("#input").val(); // akkor hagyom ki ha a web template korábbi js függvényéből máshonnak hozok át értéket
    $.ajax({
        type: "POST",
        url: "/",
        data: JSON.stringify({
            "name": input, "type" : measure, "measure": input_measure
        }),
        dataType: "json"
    })
        .done(function(jsonResponse) {
            $("#error").html(jsonResponse.message);
        document.getElementById("demo").innerHTML = jsonResponse.message;

        });
}

function ajaxScript1() {
   // var input = $("#input").val(); // akkor hagyom ki ha a web template korábbi js függvényéből máshonnak hozok át értéket
    $.ajax({
        type: "POST",
        url: "/",
        data: JSON.stringify({
            "name": input, "type" : measure
        }),
        dataType: "json"
    })
        .done(function(jsonResponse) {
            $("#error").html(jsonResponse.message);
        document.getElementById("demo").innerHTML = input;

        });
}

function ajaxScript2() {
    var input = document.getElementById("input").value;
    var data = JSON.stringify({
        "name": input
    });
    var xhr = new XMLHttpRequest();
    xhr.open("POST", "/", true);
    xhr.onreadystatechange = function() {
        if (xhr.readyState == 4 && xhr.status == 200) {
            var jsonResponse = JSON.parse(xhr.responseText);
            document.getElementById("error").innerHTML = jsonResponse.message;
        }
    };
    xhr.send(data);
}

function ajaxGetGroupname() {
    $.ajax({
        type: "POST",
        url: "/groupname",
        data: JSON.stringify({
            "groupname": groupname
        }),
        dataType: "json"
    })
        .done(function(jsonResponse) {
            document.getElementById("demo").innerHTML = jsonResponse.message;
        });
/*                alert("Kérlek minden szempontot értékelj");
*/

}
