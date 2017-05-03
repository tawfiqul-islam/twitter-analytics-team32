
d3.queue()
	.defer(d3.json, config.scenario1_url)
	.await(makeGraphs);

function makeGraphs(error, scenario1) {
	makeGraphs1(scenario1);
}


function makeGraphs1(scenario) {
	curr_scenario = 1
	data = preprocess(scenario, true); // see preprocess.js
	columns = data.columns;
	aurin_data = data.aurin_data

	console.log('Draws ' + Object.keys(columns).length + ' graphs');

	//var internet_access_bar_chart = dc.rowChart('#scenario1_graph1');

	//var data = crossfilter(scenario1.rows);

	// create crossfilter dimensions
	//var internet_dimension = data.dimension(function (d) {return d.internet_access.internet_tt_3_percent_6_11_6_11;});

	// create crossfilter groups
	//var internet_group = internet_dimension.group().reduceCount();


	//internet_access_bar_chart
		//.width(300)
		//.height(200)
		////.margins({top: 10, right: 50, bottom: 30, left: 40})
		//.dimension(internet_dimension)
		//.group(internet_group)
		//.elasticX(true)
		//.on('filtered', function(chart, filter) {
			//// TODO delete			
			//console.log(chart);
			//console.log(filter);
		//});

	i = 1;
	for (var c in columns) {
		curr_div_id = 'scenario' + curr_scenario + '_graph' + i;
		document.getElementById(curr_div_id).innerHTML = columns[c].detail;

		dc.rowChart('#' + curr_div_id)
			.width(300)
			.height(200)
			.dimension(columns[c].dimension)
			.group(columns[c].group)
			.elasticX(true);


		i = i + 1;
	}

	dc.renderAll();
}
