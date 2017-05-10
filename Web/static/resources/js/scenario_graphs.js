
d3.queue()
	.defer(d3.json, config.scenario_url)
	.await(makeGraphs);

function makeGraphs(error, scenario) {
	if (arg.type == 'bar') {
		makeBarGraphs(scenario);
	} else if (arg.type == 'scatter') {
		makeScatterPlot(scenario);
	}
}


function makeGraphs1(scenario) {
	var data = preprocess(scenario, true); // see preprocess.js
	var columns = data.columns;
	var aurin_data = data.data

	console.log('Draws ' + Object.keys(columns).length + ' graphs');

	i = 1;
	for (var c in columns) {
		curr_div_id = 'scenario' + '_graph' + i;
		document.getElementById(curr_div_id).innerHTML = columns[c].detail;

		dc.rowChart('#' + curr_div_id)
			.width(500)
			.height(200)
			.dimension(columns[c].dimension)
			.group(columns[c].group)
			//.elasticX(true);

		i = i + 1;
	}

	dc.renderAll();
}


// adapted from
// https://github.com/dc-js/dc.js/wiki/FAQ#remove-empty-bins
function remove_empty_bins(source_group) {
    return {
        all:function () {
            return source_group.all().filter(function(d) {
                // dont want undefined as x or y values
				return (d.key[0] != undefined && d.key[1] != undefined);
            });
        }
    };
}

function drawScatterPlot() {
	// uses helper function similar to
	// https://github.com/dc-js/dc.js/blob/master/web/examples/splom.html
	function make_dimension(var1, var2) {
		return scatter_data.dimension(function(d) {
			return [d[var1], d[var2], d.lga_name]; // want area name to show on hover
		});
	}
	function key_part(i) {
		return function(kv) {
			return kv.key[i];
		};
	}

	function generateTitle(d) {
		// on mouse hover, display the third element in the key
		return d.key[2];
	}

	var dim = make_dimension(x_axis, y_axis);
	var group = remove_empty_bins(dim.group());

	scatter_plot
		.width(1000)
		.height(500)
		.x(d3.scale.linear())
		.brushOn(false)
		.symbolSize(8)
		.clipPadding(10)
		.elasticX(true)
		.elasticY(true)
		.xAxisLabel(scatter_column_infos[x_axis].detail)
		.yAxisLabel(scatter_column_infos[y_axis].detail)
		.dimension(dim)
		.group(group)
		.keyAccessor(key_part(0))
		.valueAccessor(key_part(1))
		.title(generateTitle)
		.renderTitle(true);

	// determine coefficient
	var xs = [];
	var ys = [];
	var coordinates = group.all();
	for (var i=0; i<coordinates.length; i++) {
		xs.push(coordinates[i].key[0]);
		ys.push(coordinates[i].key[1]);
	}
	updateDescription(jStat.corrcoeff(xs,ys));

	scatter_plot.render();
}

function updateDescription(corr) {
	var div = document.getElementById('description');
	div.innerHTML = 'Pearson correlation: ' + corr.toFixed(3);
}

function optionOnChangeScatter(y) {
	// if 'y' is 0, x axis is changed
	// if 'y' is 1, y axis is changed
	if (y == 0) {
		x_axis = document.getElementById('opt-scatter-' + y).value;
		drawScatterPlot();
	} else if (y == 1) {
		y_axis = document.getElementById('opt-scatter-' + y).value;
		drawScatterPlot();
	}
}

function makeScatterPlot(scenario) {
	scatter_plot = dc.scatterPlot("#scatter_graph"); // global

	scatter_data = crossfilter(scenario.rows); // global

	scatter_column_infos = scenario.column_infos; // global

	// global so that it can be accessed by 'generateTitle'
	dim = scatter_data.dimension(function(d) { return [d.internet_tt_3_percent_6_11_6_11, d.ppl_drink_sugar_sweetened_soft_drink_every_day_perc, d.lga_name]; });
	var group = dim.group();

	// global variables
	x_axis = Object.keys(scenario.column_infos)[0];
	y_axis = Object.keys(scenario.column_infos)[1];

	writeOptions(document.getElementById('opt-scatter-0'), scenario.column_infos, Object.keys(scenario.column_infos)[0]);
	writeOptions(document.getElementById('opt-scatter-1'), scenario.column_infos, Object.keys(scenario.column_infos)[1]);

	optionOnChangeScatter(0);
	optionOnChangeScatter(1);
}


// write the options
function writeOptions(select, columns, selected) {
	for (var c in columns) {
		if (c == selected) {
			select.innerHTML += '<option value="' + c + '" selected="selected">' + columns[c].detail
		} else {
			select.innerHTML += '<option value="' + c + '">' + columns[c].detail
		}
	}
}

function makeBarGraphs(scenario) {
	var p = preprocess(scenario); // get getter of each column
	var columns = p.columns;
	var data = p.data;

	lga_dim1 = data.dimension(function(d) { return d.lga_name; }); // global
	lga_dim2 = data.dimension(function(d) { return d.lga_name; }); // global, same as above so that the 2 graphs can filter each other

	// create a group for each column
	groups1 = {};
	groups2 = {};
	for (var c in columns) {
		groups1[c] = lga_dim1.group().reduceSum(columns[c].getter);
		groups2[c] = lga_dim2.group().reduceSum(columns[c].getter);
	}

	chart1 = dc.barChart('#bar-graph-1'); // global
	chart2 = dc.barChart('#bar-graph-2'); // global

	writeOptions(document.getElementById('opt-bar-graph-1'), columns, Object.keys(columns)[0]);
	writeOptions(document.getElementById('opt-bar-graph-2'), columns, Object.keys(columns)[1]);

	optionOnChange(1);
	optionOnChange(2);
}

function drawBarGraph(which_chart, c) {
	var chart = chart1;
	var groups = groups1;
	var lga_dim = lga_dim1;
	if (which_chart == 2) {
		chart = chart2;
		groups = groups2;
		lga_dim = lga_dim2;
	};
	chart
		.width(1250)
		.height(300)
		.x(d3.scale.ordinal())
		.xUnits(dc.units.ordinal)
		.brushOn(false)
		.xAxisLabel('', 80) // 80 is bottom margin
		.yAxisLabel('', 30)
		.dimension(lga_dim)
		.barPadding(0.1)
		.outerPadding(0.05)
		.elasticY(true)
		.group(groups[c]);
	//.ordering(function (d) { return -d.value; });

	chart.render();
}

function optionOnChange(n) {
	var selected = document.getElementById('opt-bar-graph-' + n).value;
	drawBarGraph(n, selected);
}


function makeGraphs3(scenario) {
	categorical_rows = toCategorical(scenario.rows, scenario.column_infos);

	data = [];
	for (var i=0; i<categorical_rows.length; i++) {
		for (var c in categorical_rows[i]) {
			if (c == 'lga_code' || c == 'lga_name') {
				continue;
			}
			curr = {};
			curr['column_name'] = c;
			var j = scenario.column_infos[c].groups_str.indexOf(categorical_rows[i][c]);
			// dirty hack
			// prefix is a string with ' ' of length j-1 (to maintain uniqueness in y axis while being able to display the same value)
			curr['value'] = Array(j+1).join(' ') + scenario.column_infos[c].title;
			curr['lga_code'] = categorical_rows[i]['lga_code'];
			curr['lga_num'] = i + 1;
			data.push(curr);
		}
	}
	var num_of_columns = Object.keys(scenario.column_infos).length; // used in drawing legend

	var y_labels = [];
	// dirty hack to have separator between low, medium, high in the y axis
	var curr_separator = ' '; // a hack to separate low, medium, high
	//y_labels.push(curr_separator);
	for (var i in config.index_to_category) {
		curr_separator += ' ';
		y_labels.push(curr_separator);
		for (var c in scenario.column_infos) {
			// dirty hack
			y_labels.push(Array(+i+1).join(' ') + scenario.column_infos[c].title);
		}
		y_labels.push(config.index_to_category[i]);
	}
	curr_separator += ' ';
	y_labels.push(curr_separator);

	var margin = {top: 20, right: 600, bottom: 30, left: 100},
		width = 2500 - margin.left - margin.right,
		height = 600 - margin.top - margin.bottom;

	// adapted from http://bl.ocks.org/weiglemc/6185069
	/* 
	 * value accessor - returns the value to encode for a given data object.
	 * scale - maps value to a visual display encoding, such as a pixel position.
	 * map function - maps from data value to display value
	 * axis - sets up axis
	 */ 

	// setup x 
	var xValue = function(d) { return d.lga_num;}, // data -> value
		xScale = d3.scale.linear().range([0, width]).domain([d3.min(data, xValue)-1, d3.max(data, xValue)+1]), // value -> display
		xMap = function(d) { return xScale(xValue(d));}, // data -> display
		xAxis = d3.svg.axis().scale(xScale).orient("bottom");

	// setup y
	var yValue = function(d) { return d.value;}, // data -> value
		//yScale = d3.scale.linear().range([height, 0]), // value -> display
		yScale = d3.scale.ordinal().domain(y_labels).rangePoints([height, 0]), // value -> display
		yMap = function(d) { return yScale(yValue(d));}, // data -> display
		yAxis = d3.svg.axis().scale(yScale).orient("left");

	// setup fill color
	var cValue = function(d) { return scenario.column_infos[d.column_name].detail;},
		color = d3.scale.category10();

	// add the graph canvas to the body of the webpage
	var svg = d3.select("body").append("svg")
		.attr("width", width + margin.left + margin.right)
		.attr("height", height + margin.top + margin.bottom)
		.append("g")
		.attr("transform", "translate(" + margin.left + "," + margin.top + ")");

	// add the tooltip area to the webpage
	var tooltip = d3.select("body").append("div")
		.attr("class", "tooltip")
		.style("opacity", 0);


	// x-axis
	svg.append("g")
		.attr("class", "x axis")
		.attr("transform", "translate(0," + height + ")")
		.call(xAxis)
		.append("text")
		.attr("class", "label")
		.attr("x", width)
		.attr("y", -6)
		.style("text-anchor", "end")
		.text("Area");

	// y-axis
	svg.append("g")
		.attr("class", "y axis")
		.call(yAxis)
		.append("text")
		.attr("class", "label")
		.attr("transform", "rotate(-90)")
		.attr("y", 6)
		.attr("dy", ".71em")
		.style("text-anchor", "end")
		//.text("Protein (g)");

	// draw dots
	svg.selectAll(".dot")
		.data(data)
		.enter().append("circle")
		.attr("class", "dot")
		.attr("r", 4)
		.attr("cx", xMap)
		.attr("cy", yMap)
		.style("fill", function(d) { return color(cValue(d));}) 
		.on("mouseover", function(d) {
			tooltip.transition()
				.duration(100)
				.style("opacity", .9);
			tooltip.html("TODO" + "<br/> (" + xValue(d) 
				+ ", " + yValue(d) + ")")
				.style("left", (d3.event.pageX + 5) + "px")
				.style("top", (d3.event.pageY - 28) + "px");
		})
		.on("mouseout", function(d) {
			tooltip.transition()
				.duration(800)
				.style("opacity", 0);
		});

	// draw legend
	var legend = svg.selectAll(".legend")
		.data(color.domain())
		.enter().append("g")
		.attr("class", "legend")
		.attr("transform", function(d, i) { return "translate(0," + (num_of_columns-i-1) * 20 + ")"; });

	// draw legend colored rectangles
	legend.append("rect")
		.attr("x", width - 20 + margin.right)
		//.attr("y", -margin.top)
		.attr("width", 18)
		.attr("height", 18)
		.style("fill", color);

	// draw legend text
	legend.append("text")
		.attr("x", width - 26 + margin.right)
		.attr("y", 9)
		.attr("dy", ".35em")
		.style("text-anchor", "end")
		.text(function(d) { return d;})
}

// messed up graph
function makeGraphs2(scenario) {

	values = [];
	for (var i=0; i<scenario.rows.length; i++) {
		for (var c in scenario.rows[i]) {
			if (c == 'lga_code' || c == 'lga_name') {
				continue;
			}
			curr = {};
			curr['column_name'] = c;
			curr['value'] = scenario.rows[i][c];
			curr['lga_code'] = scenario.rows[i]['lga_code'];
			values.push(curr);
		}
	}

	var aurin_data = crossfilter(values);
	var dim = aurin_data.dimension(function(d) {return [d.column_name, d.lga_code]; });
	var group = dim.group().reduceSum(function(d) { return +d.value; });

	var symbolScale = d3.scale.ordinal().range(d3.svg.symbolTypes);
	var symbolAccessor = function(d) { return symbolScale(d.key[0]); };
	var subChart = function(c) {
		return dc.scatterPlot(c)
			.symbol(symbolAccessor)
			.symbolSize(8)
			.highlightedSize(10)
	};

	var x = d3.scale.ordinal().domain(scenario.rows.map(function (d) {return d.lga_code; }));	

	var chart = dc.seriesChart("#scenario_graph1");
	chart
		.width(3600)
		.height(480)
		//.x(x)
		//.xUnits(dc.units.ordinal)
		.y(d3.scale.ordinal())
		.yUnits(dc.units.ordinal)
		.chart(subChart)
		.brushOn(false)
		.yAxisLabel("TODO")
		.xAxisLabel("TODO")
		.clipPadding(10)
		.elasticY(true)
		.dimension(dim)
		.group(group)
		//.mouseZoomable(true)
		.shareTitle(false) // allow default scatter title to work
		.seriesAccessor(function(d) {return d.key[0];})
		.keyAccessor(function(d) {return d.key[1];})
		.valueAccessor(function(d) {return d.value;})
		.legend(dc.legend().x(350).y(350).itemHeight(13).gap(5).horizontal(1).legendWidth(140).itemWidth(70))
		.renderlet(function (chart) {
			// rotate x-axis labels
			chart.selectAll('g.x text')
				.attr('transform', 'translate(-30,0) rotate(315)')});
	//chart.yAxis().tickFormat(function(d) {return d3.format(',d')(d+299500);});
	//chart.margins().left += 40;
	dc.renderAll();
}
