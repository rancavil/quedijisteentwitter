google.load('visualization','1.0',{'packages':['corechart','table']});
google.setOnLoadCallback(drawChart);
google.setOnLoadCallback(drawTable);

var jsonData;
var chart;
var table;
var data;
var username;

$(document).on("ready",initDocument);

function initDocument() {
	$("#mensajes").hide();
	$("#usertweet").hide();
	initMessage();
	chart = new google.visualization.ColumnChart(document.getElementById('chart'));
	table = new google.visualization.Table(document.getElementById('table'));
	$("#buscar").on("click",getdata);
	$("#cerrar").on("click",close);
}
function close(ev) {
	ev.preventDefault();
	$("#tweets").fadeOut("slow");
}
function loading() {
	$("#loading").hide();
}
function getdata(ev) {
	ev.preventDefault();
	username = $("input").val().replace("@","");
	if(username == undefined || username == "") {
		$("#chart").fadeOut("slow");
		$("#table").fadeOut("slow");
		$("#tweets").fadeOut("slow");
		$("#usertweet").fadeOut("slow",showMessage);
	} else {
		$("#mensajes").fadeOut("slow");
		jsonData = $.ajax({type:"GET",url:"topfive?username="+username,dataType:"json",async:false});
		$("#mensajes").fadeOut("slow");
		responseMsg = $.parseJSON(jsonData.responseText)
		dataResp    = responseMsg.response
		if(dataResp === 'error') {
			$("#chart").fadeOut("slow");
			$("#table").fadeOut("slow");
			$("#tweets").fadeOut("slow");
			$("#usertweet").fadeOut("slow",showError);
		} else {
			data = new google.visualization.DataTable(jsonData.responseText);
			$("#chart").fadeOut("slow");
			$("#table").fadeOut("slow");
			$("#tweets").fadeOut("slow");
			$("#chart").fadeIn("slow",drawChart);
			$("#table").fadeIn("slow",drawTable);
			$("#usertweet").html("<p><strong>Tweets de @"+username+"</strong></p>");
			$("#usertweet").fadeIn("slow");
		}
	}
	$("input").val("");
}
function initMessage() {
		$("#message").html("<p><strong>Hola, para usar esta aplicacion consulta por una cuenta de twitter</strong></p>");
		$("#mensajes").fadeIn("slow");	
}
function showError() {
		$("#message").html("<p><strong>Error al momento de generar las estadisticas</strong></p>");
		$("#mensajes").fadeIn("slow");
}
function showMessage() {
		$("#message").html("<p><strong>Debes indicar un usuario twitter</strong></p>");
		$("#mensajes").fadeIn("slow");
}
function drawChart() {
	if(data != undefined) {
		var options = {'title':'Grafico Fecha/Tweets','width':450,'height':300};
		chart.draw(data,options);
		google.visualization.events.addListener(chart,'select', selectBar);
	}
}
function drawTable() {
	if(data != undefined) {
		table.draw(data,{showRowNumber : false, sort : 'disable'});
		google.visualization.events.addListener(table,'select', selectRow);
	}
}
function selectBar() {
	var selection = chart.getSelection();
	table.setSelection(selection);
	showTweets(selection);
}
function selectRow() {
	var selection = table.getSelection();
	chart.setSelection(selection);
}
function showTweets(selection) {
	$("#tweets").css({opacity: 0.8,width: "30%"});
	$("#tweet").css({opacity: 0.8,width: "95%"});
	$("#tweets").fadeIn("slow");
	var item = selection;
	var date_text = '';
    for (var i = 0; i < selection.length; i++) {
      var item = selection[i];
      if (item.row != null && item.column != null) {
        var str = data.getFormattedValue(item.row, 0);
        date_text += str;
      }
    }
    if (date_text == '') {
      date_text = 'nothing';
    } else {
    	var jsonTweets = $.ajax({type:"GET",url:"tweets?username="+username+"&date_text="+date_text,
    							contentType: 'application/json; charset=utf-8',
    							dataType:"json",
    							async:false});
    	var tweets = eval('('+jsonTweets.responseText+')');
    	
    	var t = ""
    	for(var i = 0; i < tweets.tweets.length;i++) {
    		t += "<p><strong>"+tweets.tweets[i].hour+"</strong> "+tweets.tweets[i].text+"</p>";	
    	}
    	$("#titulo").html("<strong>Tweets :</strong> @"+username+" <strong>del </strong>"+date_text);
    	$("#tweet").html(t);
    }
}