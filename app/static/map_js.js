
var original_place_dots_color = '#5184AF';
var clicked_place_dots_color = 'f44262';

d3.select("#toggle_button")
.on("click",function() {
    var list_display = d3.select("#result_list").style("display");
    var map_display = d3.select("#svg_map").style("display");
    var toggle_text = document.getElementById("toggle_button");
    var toggle_text = d3.select("#toggle_button")

    //display the result list
    if (list_display=="none") {
        d3.select("#result_list").style("display","block");
        d3.select("#svg_map").style("display","none");
        toggle_text.attr("value","Result Map");
    }
    //display the result map
    else{
        d3.select("#svg_map").style("display","block");
        d3.select("#result_list").style("display","none");
        toggle_text.attr("value","Result List");
    }
});

$("body")
.on("click","#modal_more_detail",function(argument) {
    if (d3.select("#more_detail_div").style("display")=="none") {
        d3.select("#more_detail_div").style("display","block");
        $(".lnr-chevron-right").removeClass("lnr-chevron-right").addClass("lnr-chevron-down");
    }else{
        d3.select("#more_detail_div").style("display","none");
        $(".lnr-chevron-down").removeClass("lnr-chevron-down").addClass("lnr-chevron-right")
    }
    
});

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

if (map_geo) {
    var loc_to_display = results;

    console.log(loc_to_display);
    console.log(map_geo);
    var countries = topojson.feature(map_geo, map_geo.objects.countries);
    var projection = d3.geoMiller().scale(75);
    var pathGenerator = d3.geoPath().projection(projection);



    var svg_map = d3.select("#svg_map");

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

        //place labels text
        var place_labels = svg_map.append("g").selectAll(".place_labels")
        .data(loc_to_display);

        place_labels = place_labels.enter().append("text")
        .style("font-size","10px")
        .merge(place_labels);

        place_labels
        // .attr("x", function (d) {
        //     return projection([d[1][1],d[1][0]])[0]+10;
        // })
        // .attr("y", function (d) {
        //     return projection([d[1][1],d[1][0]])[1]+15;
        // })
        .attr("class", "place_labels")
        .attr("id",function (d,i) {
            return "place_label_"+i;
        })
        .text(function (d,i) {
            return i+1+". "+d[0];
        })
        .style("font-size","1em")
        // .style("text-anchor",function(d,i) {
        //     if (i%3==0) {return "start";}
        //     if (i%3==1) {return "middle";}
        //     if (i%3==2) {return "end";}
        // })
        .style("text-anchor","middle")
        .on("click", function (d,i) {
            d3.select("#info_modal")
            .style("display","block");
            d3.select("#modal_place_name_span")
            .html(d[0]+'<span class="score_span">score:<span class="blue_score_span">'+d[5]+'</span></span>');
            d3.select("#modal_description_span")
            .html(d[2]);

            for (var j = 0; j < d[3].length; j++) {
                if (version=="v1") {
                    $("div#info_modal").append('<h6 class="modal_temp indent" id="modal_recommendation_span_'+j+'">'+d[3][j][0]+': '+'</h6>');
                }else if (version=="v2") {
                    $("div#info_modal").append('<h6 class="modal_temp indent" id="modal_recommendation_span_'+j+'">'+d[3][j][0]+': '+'</h6>'+'<span class="modal_temp indent">'+d[3][j][2])+'</span>';
                }
                $("div#info_modal").append('<a class="indent modal_temp" target="_blank" href="'+d[3][j][1]+'" id="modal_recommendation_a_'+j+'">(link)</a>');
                
            }

            if (d[4]["When to Go"]) {
                $("div#info_modal").append('<h5 class="modal_temp">When to Go: </h5> <span id="modal_whentogo_span" class="modal_temp indent">'+d[4]["When to Go"]+'</span>');
            }
            if (d[4]["Events"]) {
                $("div#info_modal").append('<h5 class="modal_temp">Events: </h5> <span id="modal_events_span" class="modal_temp indent">'+d[4]["Events"]+'</span>');
            }

            if (Object.keys(d[4]).length>2) {
                $("div#info_modal").append('<h5 id="modal_more_detail" class="modal_temp">More details: <span class="lnr lnr-chevron-right"></span></h5>');
                $("div#info_modal").append('<div id="more_detail_div" class="modal_temp indent">');
                
                // d[4].forEach(function(description,index) {
                for (var index in d[4]){
                    var description = d[4][index];
                    if (index!="When to Go" && index!="Events") {
                        $("div#more_detail_div").append('<h5 class="modal_temp">'+index+': </h5> <span class="modal_temp indent">'+description+'</span>');
                    }
                }
                // });
                $("div#info_modal").append('</div>');
            }
            

            //make the place label and dashed line disappear when info box poped up
            // d3.select("#info_line_"+i)
            // .attr("display","none");
            // d3.select("#place_label_"+i)
            // .attr("display","none");
            //make the place circle a different color
            d3.select("#place_dot_"+i)
            .style("fill",clicked_place_dots_color);
        })
        .on("mouseover",function(d,i) {
            d3.select("#info_line_"+i)
            .style("stroke-width",2)
            .style("stroke","#213a4f");
            d3.select("#place_dot_"+i)
            .attr("r",6)
            .style("fill","#213a4f");
            d3.select(this)
            .style("text-decoration","underline black");
        })
        .on("mouseout",function(d,i) {
            d3.select("#info_line_"+i)
            .style("stroke-width",1)
            .style("stroke","#5184AF");
            d3.select("#place_dot_"+i)
            .attr("r",4)
            .style("fill","#5184AF");
            d3.select(this)
            .style("text-decoration","none");
        });

        //add collision forces
        var label_simulation = d3.forceSimulation(loc_to_display);
        label_simulation
        .velocityDecay(0.5)
        .force("x", d3.forceX(d => projection([d[1][1],d[1][0]])[0]+5).strength(0.5))
        .force("y", d3.forceY(d => projection([d[1][1],d[1][0]])[1]+5).strength(0.5))
        .force("collision", d3.forceCollide(35))
        .on("tick", label_updateDisplay);
        // Consult the docs: https://github.com/d3/d3-force


        // Tell the simulation about the nodes, attach a self-moving event.
        // label_simulation
        // .nodes(loc_to_display)
        

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
        .attr("x2", function (d,i) {
            var label_i_x = d3.select("#place_label_"+i).attr("x");
            return label_i_x;
        })
        .attr("y2", function (d,i) {
            var label_i_y = d3.select("#place_label_"+i).attr("y");
            return label_i_y-5;
        })
        .attr("class", "info_lines")
        .attr("id",function (d,i) {
            return "info_line_"+i;
        })
        .style("stroke-width","1")
        .style("stroke","#5184AF")
        .style("stroke-linecap","round")
        .style("stroke-dasharray","2, 2");
        

        // Move the label to their locations.
        // label_updateDisplay();

        function label_updateDisplay() {
            place_labels
            .attr("x", function(d) { return d.x; })
            .attr("y", function(d) { return d.y-10; });
            info_lines
            .attr("x2", function (d,i) {
                var label_i_x = d3.select("#place_label_"+i).attr("x");
                return label_i_x;
            })
            .attr("y2", function (d,i) {
                var label_i_y = d3.select("#place_label_"+i).attr("y");
                return label_i_y;
            }); 
        }

        
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
            d3.selectAll(".modal_temp")
            .remove();
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

}




    

    
// });