//slider value update
// var slider = document.getElementById("distance_slider");
// var output = document.getElementById("distance_span");
// output.innerHTML = slider.value;

// slider.oninput = function() {
//     if (this.value==0) {
//         output.innerHTML = "unrestricted distance";
//     }else{
//         output.innerHTML = this.value+" km";
//     }
  
// }
// $( "#distance_slider" ).slider({
//   change: function( event, ui ) {
//     console.log(ui.value);
//   }
// });
function showVal(val) {
	if (val==0) {
		$("#distance_span").text("any distance");
	}else{
		$("#distance_span").text(val+" km");
	}
    
}