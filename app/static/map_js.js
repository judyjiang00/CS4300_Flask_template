
var original_place_dots_color = '#5184AF';
var clicked_place_dots_color = 'f44262';
// var info_box_width = 250;
// var info_box_height = 60;
console.log(version);

function getRandomColor() {
  var letters = '0123456789ABCDEF';
  var color = '#';
  for (var i = 0; i < 6; i++) {
    color += letters[Math.floor(Math.random() * 16)];
  }
  return d3.interpolateGreens(Math.random());
}

function getRandomLocation(geo_data_input) {
    var geo_location_keys = Object.keys(geo_data_input);
    var output_loc_arr = [];
    for (var i = 0; i < 5; i++) {
        var randomLocationName = geo_location_keys[ Math.floor(Math.random()*geo_location_keys.length)];
        output_loc_arr.push(geo_data_input[randomLocationName]);
    }
    return output_loc_arr;
}

function get_tspan_html(x,y,line_height, text) {
    return "<tspan x="+x+" dy="+(y+line_height)+">"+text+"</tspan>";
}

// function update_box_position() {
//     var rects = [d3.select("#info_box_0"),d3.select("#info_box_1"),d3.select("#info_box_2"),d3.select("#info_box_3"),d3.select("#info_box_4")];
//     for (var i = 0; i < rects.length; i++) {
//         for (var j = i+1; j < rects.length; j++) {
//             var rect_i = rects[i];
//             var rect_j = rects[j];
//             console.log("i:");
//             console.log(rect_i);
//             console.log("j:");
//             console.log(rect_j);

//             var rect_i_left = parseInt(rect_i.attr('x'));
//             var rect_i_top = parseInt(rect_i.attr('y'));
//             var rect_i_right = rect_i_left+info_box_width;
//             var rect_i_bottom = rect_i_top+info_box_height;
//             // console.log("i left:");
//             // console.log(rect_i_left);
//             // console.log("i top:");
//             // console.log(rect_i_top);
//             // console.log("i right:");
//             // console.log(rect_i_right);
//             // console.log("i bottom:");
//             // console.log(rect_i_bottom);

//             var rect_j_left = parseInt(rect_j.attr('x'));
//             var rect_j_top = parseInt(rect_j.attr('y'));
//             var rect_j_right = rect_j_left+info_box_width;
//             var rect_j_bottom = rect_j_top+info_box_height;
//             // console.log("j left:");
//             // console.log(rect_j_left);
//             // console.log("j top:");
//             // console.log(rect_j_top);
//             // console.log("j right:");
//             // console.log(rect_j_right);
//             // console.log("j bottom:");
//             // console.log(rect_j_bottom);

//             var j_too_left = rect_i_right>rect_j_left && rect_i_left<rect_j_left;
//             var j_too_right = rect_i_left<rect_j_right && rect_i_right>rect_j_right;
//             var j_too_high = rect_i_bottom>rect_j_top && rect_i_top<rect_j_top;
//             var j_too_low = rect_i_top<rect_j_bottom && rect_i_bottom>rect_j_bottom;

//             console.log(j_too_left);
//             console.log(j_too_right);
//             console.log(j_too_high);
//             console.log(j_too_low);

//             if (j_too_left){
//                 rect_j
//                 .transition()
//                 .duration(1000)
//                 .attr('x',function (d) {
//                     return parseInt(d3.select(this).attr('x'))+(rect_i_right-rect_j_left)+5;
//                 });
//             }
//             if (j_too_right) {
//                 rect_j
//                 .transition()
//                 .duration(1000)
//                 .attr('x',function (d) {
//                     return parseInt(d3.select(this).attr('x'))-(rect_j_right-rect_i_left)-5;
//                 });
//             }
//             if (j_too_high) {
//                 rect_j
//                 .transition()
//                 .duration(1000)
//                 .attr('y',function (d) {
//                     return parseInt(d3.select(this).attr('y'))+(rect_j_bottom-rect_i_top)+5;
//                 });
//             }
//             if (j_too_low) {
//                 rect_j
//                 .transition()
//                 .duration(1000)
//                 .attr('y',function (d) {
//                     return parseInt(d3.select(this).attr('y'))-(rect_i_bottom-rect_j_top)+5;
//                 });
//             }
//         }
//     }

// }

if (map_geo) {
    var loc_to_display = results;

    console.log(loc_to_display);
    console.log(map_geo);
    var countries = topojson.feature(map_geo, map_geo.objects.countries);
    var projection = d3.geoMiller().scale(75);
    var pathGenerator = d3.geoPath().projection(projection);



    var svg_map = d3.select("#svg_map");
    // d3.select("#map_button")
    // .on("click",function () {
    //     if (svg_map.attr("height")==0) {
    //         svg_map
    //         .transition()
    //         .duration(500)
    //         .attr("height",700);
    //         setTimeout(draw_map,501);
    //     }
    //     else{
    //         svg_map
    //         .transition()
    //         .duration(500)
    //         .attr("height",0)
    //     }
    // });
    draw_map();

    

    function draw_map() {
        projection.fitExtent([[0,0], [svg_map.attr("width"), svg_map.attr("height")]], countries);
        var pathGenerator = d3.geoPath().projection(projection);

        var paths = svg_map.selectAll("path")
        .data(countries.features);

        paths = paths.enter().append("path").merge(paths);

        paths
        .attr("d",function (country) {
            return pathGenerator(country);
        })
        .attr("stroke", "grey")
        .attr("fill",d=>getRandomColor())
        .style("opacity","0.5")
        .attr("stroke-width","0.8px");

        //show circles on interested points
        var place_dots = svg_map.selectAll(".place_dots")
        .data(loc_to_display);

        place_dots = place_dots.enter().append("circle")
        .attr("r",4).merge(place_dots);

        place_dots
        .attr("cx", function (d) {
            return projection([d[1][1],d[1][0]])[0];
        })
        .attr("cy", function (d) {
            return projection([d[1][1],d[1][0]])[1];

        })
        .attr("class", "place_dots")
        .attr("id",function (d,i) {
            return "place_dot_"+i;
        })
        .attr("fill", original_place_dots_color)
        .style("opacity","0.7");

        //line connecting circle and text
        var info_lines = svg_map.selectAll(".info_lines")
        .data(loc_to_display);

        info_lines = info_lines.enter().append("line")
        .merge(info_lines);

        info_lines
        .attr("x1", function (d) {
            return projection([d[1][1],d[1][0]])[0];
        })
        .attr("y1", function (d) {
            return projection([d[1][1],d[1][0]])[1];
        })
        .attr("x2", function (d) {
            return projection([d[1][1],d[1][0]])[0]+10;
        })
        .attr("y2", function (d) {
            return projection([d[1][1],d[1][0]])[1]+10;
        })
        .attr("class", "info_lines")
        .attr("id",function (d,i) {
            return "info_line_"+i;
        })
        .style("stroke-width","1")
        .style("stroke","#5184AF")
        .style("stroke-linecap","round")
        .style("stroke-dasharray","2, 2");

        //pop-up box for each location
        // var info_boxes = svg_map.selectAll(".info_boxes")
        // .data(loc_to_display);

        // info_boxes = info_boxes.enter().append("rect")
        // .attr("width",0)
        // .attr("height",0)
        // .merge(info_boxes);

        // info_boxes
        // .attr("x", function (d) {
        //     return projection([d[1][1],d[1][0]])[0];
        // })
        // .attr("y", function (d) {
        //     return projection([d[1][1],d[1][0]])[1];
        // })
        // .attr("rx",15)
        // .attr("ry",15)
        // .attr("class", "info_boxes")
        // .attr("id",function (d,i) {
        //     return "info_box_"+i;
        // })
        // .style("opacity",0.75)
        // .style("z-index",20)
        // .on("click",function (d,i) {
        //     d3.select("#info_modal"+i)
        //     .style("display","block");
        // })
        // .on("mouseover",function (d,i) {
        //     d3.select(this)
        //     .style("stroke-width","5px");

        //     d3.select(this).style("display","block");

        // })
        // .on("mouseout", function (d,i) {
        //     // d3.select(this)
        //     // .transition()
        //     // .duration(200)
        //     // .attr("width", 0)
        //     // .attr("height",0);
        //     // // d3.select(this)
        //     // // .transition()
        //     // // .style("display", "none");

        //     // //make the place label and dashed line disappear when info box poped up
        //     // d3.select("#info_line_"+i)
        //     // .transition()
        //     // .delay(200)
        //     // .attr("display","block");
        //     // d3.select("#place_label_"+i)
        //     // .transition()
        //     // .delay(200)
        //     // .attr("display","block");
        //     // //make the place circle a different color
        //     // d3.select("#place_dot_"+i)
        //     // .transition()
        //     // .delay(200)
        //     // .style("fill",original_place_dots_color);
        // });

        //place labels text
        var place_labels = svg_map.selectAll(".place_labels")
        .data(loc_to_display);

        place_labels = place_labels.enter().append("text")
        .style("font-size","10px")
        .merge(place_labels);

        place_labels
        .attr("x", function (d) {
            return projection([d[1][1],d[1][0]])[0]+10;
        })
        .attr("y", function (d) {
            return projection([d[1][1],d[1][0]])[1]+15;
        })
        .attr("class", "place_labels")
        .attr("id",function (d,i) {
            return "place_label_"+i;
        })
        .text(function (d,i) {
            return i+1+". "+d[0];
        })
        .style("font-size","1em")
        .on("click", function (d,i) {
            // d3.select("#info_box_"+i)
            // .transition()
            // .duration(600)
            // .attr("width", info_box_width)
            // .attr("height",info_box_height);
            // d3.select("#info_text_"+i)
            // .transition()
            // .delay(600)
            // .style("display", "block");
            // d3.select("#exit_cross_"+i)
            // .transition()
            // .delay(600)
            // .style("display", "block");
            d3.select("#info_modal")
            .style("display","block");
            d3.select("#modal_place_name_span")
            .html(d[0]);
            d3.select("#modal_description_span")
            .html(d[2]);


            d3.select("#modal_recommendations_span")
            .html(d[3].map(e => e[0]).join(", "));

            //make the place label and dashed line disappear when info box poped up
            // d3.select("#info_line_"+i)
            // .attr("display","none");
            // d3.select("#place_label_"+i)
            // .attr("display","none");
            //make the place circle a different color
            d3.select("#place_dot_"+i)
            .style("fill",clicked_place_dots_color);

            // update_box_position();
        });

        //close modal when clicking exit cross
        d3.selectAll(".exit_crosses")
        .on('click',function () {
            d3.select("#info_modal")
            .style("display","none");
            //make the place label and dashed line disappear when info box poped up
            d3.selectAll(".info_lines")
            .attr("display","block");
            d3.selectAll(".place_labels")
            .attr("display","block");
            //make the place circle a different color
            d3.selectAll(".place_dots")
            .style("fill",original_place_dots_color);
        });
    }

    


    // //info texts in the info box
    // var info_texts = svg_map.selectAll(".info_texts")
    // .data(loc_to_display);

    // info_texts = info_texts.enter().append("text")
    // .style("font-size","10px")
    // .merge(info_texts);

    // info_texts
    // .attr("x", function (d,i) {
    //     var x = d3.select("#info_box_"+i).attr("x");
    //     return parseInt(x)+15;
    //     // return projection([d['results'][0]['geometry']['location']['lng'],d['results'][0]['geometry']['location']['lat']])[0]+15;
    // })
    // .attr("y", function (d,i) {
    //     var y = d3.select("#info_box_"+i).attr("y");
    //     return parseInt(y)+20;
    //     // return projection([d['results'][0]['geometry']['location']['lng'],d['results'][0]['geometry']['location']['lat']])[1]+25;
    // })
    // .attr("class", "info_texts")
    // .attr("id",function (d,i) {
    //     return "info_text_"+i;
    // })
    // .html(function (d,i) {
    //     var x = d3.select(this).attr("x");//get the x position of the text
    //     var y = d3.select(this).attr("dy");//get the y position of the text
    //     var info_line1 = 'Place Name: '+d[0];
    //     var info_line2 = 'Recommendations: ' ;
    //     var info_line3 = d[3].map(e => e[0]).join(",");
    //     return  info_line1+get_tspan_html(x,y,15,info_line2)+get_tspan_html(x,y,15,info_line3);
    // })
    // .style("font-size","1em")
    // .style("display","none")
    // .on("mouseover",function (d,i) {
    //     d3.select("#info_box_"+i)
    //     .style("stroke-width","5px");

    //     d3.select("#info_box_"+i).style("display","block");

    // });

    //info modal div
    // var info_modals = svg_map.selectAll(".info_modals")
    // .data(loc_to_display);

    // info_modals = info_modals.enter().append("div")
    // .merge(info_modals);

    // info_modals
    // .attr("id",function (d,i) {
    //     return "info_modal_"+i;
    // })
    // .attr("class","info_modals")
    // .html(function (d,i) {
    //     var line1 = "Place Name: "+d[0]+"<br>";
    //     var line2 = "Description: "+"<br>";
    //     var line3 = d[2]+"<br>";
    //     var line4 = "";
    //     for (var i=0; i<d[3].length; i++){
    //         line4_i = d[3][i].join(": ") + "<br>";
    //         line4 = line4+line4_i;
    //     }
    //     return line1+line2+line3+line4;
    // });

    //red cross to exit the info modal
    // var exit_crosses = svg_map.selectAll(".exit_crosses")
    // .data(loc_to_display);

    // exit_crosses = exit_crosses.enter().append("text")
    // .style("font-size","10px")
    // .merge(exit_crosses);

    // exit_crosses
    // // .attr("x", function (d,i) {
    // //     var x = d3.select("#info_box_"+i).attr("x");
    // //     return parseInt(x)+info_box_width;
    // //     // return projection([d['results'][0]['geometry']['location']['lng'],d['results'][0]['geometry']['location']['lat']])[0]+15;
    // // })
    // // .attr("y", function (d,i) {
    // //     var y = d3.select("#info_box_"+i).attr("y");
    // //     return parseInt(y)+5;
    // //     // return projection([d['results'][0]['geometry']['location']['lng'],d['results'][0]['geometry']['location']['lat']])[1]+25;
    // // })
    // .attr("class", "exit_crosses")
    // .attr("id",function (d,i) {
    //     return "exit_cross_"+i;
    // })
    // .text("X")
    // .style("font-size","1em")
    // .style("display","none")
    // .on("click", function (d,i) {
    //     d3.select("#info_modal_"+i)
    //     .attr("display","none");
    //     d3.select(this)
    //     .attr("display","none");
    // });

}



    

    
// });