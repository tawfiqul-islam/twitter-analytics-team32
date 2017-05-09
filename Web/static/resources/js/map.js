d3.queue()
	.defer(d3.json, config.lga_url)
	.defer(d3.json, config.scenario_url)
	.await(makeMap);

function makeMap(error, lga, scenario) {
	if (error == null) {
		makeMap1(lga, scenario);
	} else {
		// TODO error handling
	}
}

var categories = ['Low', 'Medium', 'High'];


function makeMap1(lga, scenario) {

	var p = preprocess(scenario, false, true); // see preprocess.js
	columns = p.columns;
	var data = p.data

	var default_c = Object.keys(columns)[0];  // use on first call to legend.update(default_c) and radio button with this id is checked by default
	var curr_groups_str = columns[default_c].groups_str;
	var curr_getter = columns[default_c].getter;

	// needed to get a column value by LGA code
	var lga_code_dimension = data.dimension(function (d) { return d.lga_code; });

	// create crossfilter from the numeric data as well to show the percentage of happy, neutral and unhappy
	data_numeric = crossfilter(scenario.rows);
	var lga_code_dimension_numeric = data_numeric.dimension(function (d) { return d.lga_code; });


	// i is the index of the color
	function getColor(i) {
		if (i == -1) {
			return config.null_color;
		}
		return config.group_color[i];
	}

	function fillColor(lga_code) {
		var row = lga_code_dimension.filter(lga_code).top(1)[0];
		var i = -1;
		if (row) i = curr_groups_str.indexOf(curr_getter(row));
		return getColor(i);
	}

	function style(feature) {
		return {
			fillColor: fillColor(feature.properties.lga_code),
			weight: 1,
			opacity: 1,
			color: '#34495e',
			//dashArray: '3',
			fillOpacity: 0.7
		};
	}


	// interaction on each polygon
	// adapted from http://leafletjs.com/examples/choropleth/
	function highlightFeature(e) {
		var layer = e.target;

		layer.setStyle({
			weight: 5,
			color: '#2C3E50',
			dashArray: '',
			fillOpacity: 0.7
		});

		if (!L.Browser.ie && !L.Browser.opera && !L.Browser.edge) {
			layer.bringToFront();
		}

		// update the information located at corner of the map
		info.update(layer.feature.properties);
	}

	function resetHighlight(e) {
		geojson.resetStyle(e.target);

		// reset information at corner of the map
		info.update();
	}

	// add listeners to layers
	function onEachFeature(feature, layer) {
		layer.on({
			mouseover: highlightFeature,
			mouseout: resetHighlight
			//click: zoomToFeature
		});
	}


	var my_map = L.map('mapid').setView(config.vic_coordinates, 8);

	// from https://leaflet-extras.github.io/leaflet-providers/preview/
	L.tileLayer('http://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
		maxZoom: 11,
		minZoom: 6,
		attribution: '&copy; <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a>'
	}).addTo(my_map);

	var geojson = L.geoJson(lga, {
		style: style,
		onEachFeature: onEachFeature
	}).addTo(my_map);


	// show information of a polygon on hover in the corner of the map
	var info = L.control({position: 'topright'});

	// called on control.addTo(map)
	info.onAdd = function (map) {
		this._div = L.DomUtil.create('div', 'area-info'); // create a div
		this.update();
		return this._div;
	};

	// method that we will use to update the control.
	// Arg is features.properties on mouseover (set in highlightFeature)
	// No arg on mouseout (set in resetHighlight)
	info.update = function (properties) {
		this._div.innerHTML = '<h4>Local Government Areas in Victoria</h4>';
		if (properties) {
			this._div.innerHTML += '<h5>' + properties.lga_name + '</h5>';
			var row = lga_code_dimension.filter(properties.lga_code).top(1)[0];
			if (!row) return; // skip area that dont have a row in scenario
			for (var col in row) {
				// skip 'lga_code' and 'lga_geojson_feature'
				if (!columns.hasOwnProperty(col)) continue;

				var i = -1;
				i = columns[col].groups_str.indexOf(columns[col].getter(row));
				this._div.innerHTML += '<i style="background:' + getColor(i) + '"></i> ';
				this._div.innerHTML += columns[col].title + '<br>';
			}
		}
	};
	info.addTo(my_map);


	// differentiate tweet data and aurin data
	var tweet_data = []
	if (arg.which_scenario == 1) {
		tweet_data = Object.keys(config.label_to_emoji_png);
	} else if (arg.which_scenario == 2) {
		tweet_data = ['fast_food']
	}


	// column selection
	var column_selection = L.control({position: 'bottomright'});

	// called on control.addTo(map)
	column_selection.onAdd = function (map) {
		var div = L.DomUtil.create('div', 'column-selection'); // create a div

		div.innerHTML = '<form name="cf"><h4> Tweet Sentiment </h4>';
		
		// want to print tweet options first
		for (var i=0; i<tweet_data.length; i++) {
			div.innerHTML += '<input type="radio" name="column_selection_radio" id="' + tweet_data[i] + '" value="' + tweet_data[i] + '" />' + columns[tweet_data[i]].title + '<br>';
		}
		div.innerHTML += '<hr><h5>Aurin</h5>'

		for (var c in columns) {
			if (tweet_data.indexOf(c) > -1) {
				// dont want to print tweet options twice
				continue;
			}
			div.innerHTML += '<input type="radio" name="column_selection_radio" id="' + c + '" value="' + c + '" />' + columns[c].title + '<br>';
		}
		div.innerHTML += '</form>';
		return div;
	};
	column_selection.addTo(my_map);

	function columnSelectionHandler() {
		curr_getter = columns[this.value].getter;
		curr_groups_str = columns[this.value].groups_str;

		updateDescription(this.value); // update text located below the graph

		geojson.setStyle(style); // change overlay layer
		legend.update(this.value); // change legend
	}

	var radios = document.getElementsByName('column_selection_radio');
	for(var i = 0, max = radios.length; i < max; i++) {
		radios[i].onclick = columnSelectionHandler;
	}

	// set which radio button is checked at the beginning
	document.getElementById(default_c).checked = true


	// legend
	// adapted from http://leafletjs.com/examples/choropleth/
	var legend = L.control({position: 'bottomright'});
	legend.onAdd = function (map) {
		this._div = L.DomUtil.create('div', 'area-info legend');
		this.update(default_c);
		return this._div;
	};

	legend.update = function (c) {
		this._div.innerHTML = '<h4>' + columns[c].detail + '</h4>'
		// currently, each column only have three groups, but this can be easily extended by changing the global variable 'categories'
		if (curr_groups_str.length != categories.length) { console.log("Warning, number of groups is more than three"); }
		for (var i = 0; i < curr_groups_str.length; i++) {
			this._div.innerHTML += '<i style="background:' + getColor(i) + '"></i> ';
			this._div.innerHTML += categories[i] + '<br>';
			//this._div.innerHTML += curr_groups_str[i] + '<br>';
		}
	}

	legend.addTo(my_map);


	// emoji
	// adapted from http://leafletjs.com/examples/custom-icons/example.html
	var EmojiIcon = L.Icon.extend({
		options: {
			iconSize:     [24, 24], // size of the icon
			iconAnchor:   [12, 12], // point of the icon which will correspond to marker's location
			popupAnchor:  [0, 0] // point from which the popup should open relative to the iconAnchor
		}
	});

	// create an icon for each label
	label_to_icon = {}
	for (var l in config.label_to_emoji_png) {
		label_to_icon[l] = new EmojiIcon({iconUrl: config.label_to_emoji_png[l]});
	}

	if (arg.which_scenario == 1) {
		// put emojis on map :)
		for (var f=0; f<lga.features.length; f++) {
			var lga_code = lga.features[f].properties.lga_code;
			if (!lga_code) {
				// skip unincorporated areas
				continue;
			}
			var row = lga_code_dimension_numeric.filter(lga_code).top(1)[0];
			lga_code_dimension_numeric.filterAll(); // clear filter
			var label = getMajority(row);

			if (label) {
				// construct popup message string
				var popup_msg = '<table class="emoji-popup">';
				for (var l in label_to_icon) {
					popup_msg += '<tr>';
					popup_msg += '<td>' + l + ': </td>';
					popup_msg += '<td>&nbsp;&nbsp;</td>'; // space between columns
					popup_msg += '<td>' + number_to_str(row[l]) + '%</td>';
					popup_msg += '</tr>'
				}
				popup_msg += '</table>';

				var centroid = lga.features[f].properties.centroid;
				L.marker([centroid[1], centroid[0]], {icon: label_to_icon[label]}).bindPopup(popup_msg).addTo(my_map);
			}
		}
	}
}

// returns the majority of label in a particular area
// tie is broken based on which label is first in the loop
function getMajority(row) {
	var max_value = 0.0;
	var max_label = null;
	for (var label in label_to_icon) {
		if (row[label] && row[label] > max_value) {
			max_value = row[label];
			max_label = label;
		}
	}
	return max_label;
}

function updateDescription(curr_col) {
	//d.top(3)
	var div = document.getElementById('description');

	var dim = data_numeric.dimension(columns[curr_col].getter)
	
	var top_10 = dim.top(10);
	var num_happy = 0;
	for (var i=0; i<top_10.length; i++) {
		if (getMajority(top_10[i]) == 'happy') {
			num_happy += 1;
		}
	}
	div.innerHTML = 'Accuracy of twitter analysis wrt to  Aurin data: ' +  (num_happy/10)*100 + '%'
}
