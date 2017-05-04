
d3.queue()
	.defer(d3.json, config.scenario3_url)
	.await(makeGraphs);

function makeGraphs(error, scenario3) {
	makeGraphs1(scenario3);
}


function makeGraphs1(scenario) {
	curr_scenario = 1
	data = preprocess(scenario, true); // see preprocess.js
	columns = data.columns;
	aurin_data = data.aurin_data

	console.log('Draws ' + Object.keys(columns).length + ' graphs');

	i = 1;
	for (var c in columns) {
		curr_div_id = 'scenario' + curr_scenario + '_graph' + i;
		document.getElementById(curr_div_id).innerHTML = columns[c].detail;

		dc.rowChart('#' + curr_div_id)
			.width(300)
			.height(200)
			.dimension(columns[c].dimension)
			.group(columns[c].group)
			//.elasticX(true);

		i = i + 1;
	}

	dc.renderAll();
}
