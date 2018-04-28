function showVal(val) {
	if (val==0) {
		$("#distance_span").text("any distance");
	}else{
		$("#distance_span").text(val+" km");
	}
    
}

// d3.select("#home_button")
// .on("click",function() {
	
// });

// d3.select("#about_button")
// .on("click",function() {
// 	console.log("hi");
// 	d3.select("#home_search_form").style("display","none");
// 	d3.select("#about").style("display","block");
// });

function show_about() {
	d3.select("#home_search_form").style("display","none");
	$("#home_button").removeClass("active");
	d3.select("#about").style("display","block");
	$("#about_button").addClass("active");
}

function show_home() {

	d3.select("#home_search_form").style("display","block");
	$("#home_button").addClass("active");
	d3.select("#about").style("display","none");
	$("#about_button").removeClass("active");
}