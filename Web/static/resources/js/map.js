d3.queue()
	.defer(d3.json, config.lga_url)
	.defer(d3.json, config.scenario_url)
	.await(makeMap);

function makeMap(error, lga, scenario) {
	if (error == null) {
		makeMap1(lga, scenario);
	}
}

var categories = ['Low', 'Medium', 'High'];


function makeMap1(lga, scenario) {

	var p = preprocess(scenario, false, true); // see preprocess.js
	columns = p.columns;
	data = p.data

	var default_c = Object.keys(columns)[0];  // use on first call to legend.update(default_c) and radio button with this id is checked by default
	var curr_groups_str = columns[default_c].groups_str;
	var curr_getter = columns[default_c].getter;

	// needed to get a column value by LGA code
	var lga_code_dimension = data.dimension(function (d) { return d.lga_code; });

	// create crossfilter from the numeric data as well to show the percentage of happy, neutral and unhappy
	data_numeric = crossfilter(scenario.rows);
	var lga_code_dimension_numeric = data_numeric.dimension(function (d) { return d.lga_code; });


	// differentiate tweet data and aurin data
	// bad design, should not hard code here
	tweet_data = []
	if (arg.which_scenario == 1) {
		tweet_data = Object.keys(config.label_to_emoji_png);
		tweet_data.push('average_sentiment')
	} else if (arg.which_scenario == 2) {
		tweet_data = ['fast_food']
	}


	// i is the index of the color
	function getColor(i) {
		if (i == -1) {
			return config.null_color;
		}
		return config.group_color[i];
	}

	function fillColor(lga_code) {
		var row = lga_code_dimension.filter(lga_code).top(1)[0];
		lga_code_dimension.filterAll();
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

			// TODO
			// want to print tweet data first
			//for (var i=0; i<tweet_data.length; i++) {
				//this.div


			// aurin data
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
	var legend = L.control({position: 'bottomleft'});
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
	var label_to_icon = {}
	if (arg.which_scenario == 1) {
		// put emojis on map :)

		for (var l in config.label_to_emoji_png) {
			label_to_icon[l] = new EmojiIcon({iconUrl: config.label_to_emoji_png[l]});
		}

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
					popup_msg += '<td>' + numberToStr(row[l]) + '%</td>';
					popup_msg += '</tr>'
				}
				popup_msg += '</table>';

				var centroid = lga.features[f].properties.centroid;
				L.marker([centroid[1], centroid[0]], {icon: label_to_icon[label]}).bindPopup(popup_msg).addTo(my_map);
			}
		}
	}

	else if (arg.which_scenario == 2) {
		// label the percentage of food tweets

		// create an icon for each label
		var groups = columns.fast_food.groups_str;
		for (var i=0; i<groups.length; i++) {
			label_to_icon[groups[i]] = new EmojiIcon({iconUrl: config.icon_png[i]});
		}

		for (var f=0; f<lga.features.length; f++) {
			var lga_code = lga.features[f].properties.lga_code;
			if (!lga_code) {
				// skip unincorporated areas
				continue;
			}

			// get which group the area belongs to
			var row = lga_code_dimension.filter(lga_code).top(1)[0];
			lga_code_dimension.filterAll(); // clear filter
			var value_group = row.fast_food;

			// get the numeric value
			row = lga_code_dimension_numeric.filter(lga_code).top(1)[0];
			lga_code_dimension_numeric.filterAll();
			var value_numeric = row.fast_food

			if (value_group) {
				// construct popup message string
				var popup_msg = 'Percentage of fast food related tweets: ' + value_numeric + '%';

				var centroid = lga.features[f].properties.centroid;
				L.marker([centroid[1], centroid[0]], {icon: label_to_icon[value_group]}).bindPopup(popup_msg).addTo(my_map);
			}
		}
	}


	// icon box
	var icon_box = L.control({position: 'bottomleft'});

	// called on control.addTo(map)
	icon_box.onAdd = function (map) {
		var div = L.DomUtil.create('div', 'icon-box'); // create a div

		var i = 0
		for (label in label_to_icon) {
			div.innerHTML += '<img src="' + label_to_icon[label].options.iconUrl + '">'
			if (arg.which_scenario == 1) {
				div.innerHTML += label + '<br>';
			} else if (arg.which_scenario == 2) {
				fast_food_categories = ['Lowest Fast Food Tweets', 'Moderate Fast Food Tweets', 'Highest Fast Food Tweets']
				div.innerHTML += fast_food_categories[i] + '<br>';
				i += 1;
			}
		}

		return div;
	};
	icon_box.addTo(my_map);
	
}

// returns the majority of label in a particular area
// tie is broken based on which label is first in the loop
function getMajority(row) {
	var max_value = 0.0;
	var max_label = null;
	for (var label in config.label_to_emoji_png) {
		if (row[label] && row[label] > max_value) {
			max_value = row[label];
			max_label = label;
		}
	}
	return max_label;
}

function updateDescription(curr_col) {
	var div = document.getElementById('description');

	// want to skip tweet data
	if (tweet_data.indexOf(curr_col) > -1) {
		div.innerHTML = '';
		return;
	}

	var dim=0;
	if (arg.which_scenario == 1) {
		dim = data_numeric.dimension(columns[curr_col].getter);
	} else if (arg.which_scenario == 2) {
		dim = data.dimension(columns[curr_col].getter);
	}

	var top_10 = dim.top(10);
	var bot_10 = dim.bottom(10);

	var num_top = 0;
	var num_bot = 0;

	if (arg.which_scenario == 1) {
		for (var i=0; i<top_10.length; i++) {
			if (getMajority(top_10[i]) == 'happy') {
				num_top += 1;
			}
		}
		//for (var i=0; i<bot_10.length; i++) {
			//if (getMajority(bot_10[i]) == 'happy') {
				//num_bot += 1;
			//}
		//}
		div.innerHTML = 'Accuracy of twitter sentiment analysis w.r.t. to top 10 Victoria LGAs from Aurin data: ' +  (num_top/10)*100 + '%<br>'
		//div.innerHTML += 'Accuracy of twitter sentiment analysis w.r.t. to bottom 10 Victoria LGAs from Aurin data: ' +  (num_bot/10)*100 + '%'

	} else if (arg.which_scenario == 2) {
		for (var i=0; i<top_10.length; i++) {
			if (columns.fast_food.groups_str.indexOf(top_10[i].fast_food) == 2) {
				num_top += 1;
			}
			if (columns.fast_food.groups_str.indexOf(bot_10[i].fast_food) == 2) {
				num_bot += 1;
			}
		}
		div.innerHTML = 'Accuracy of fast food analysis w.r.t. to top 10 Victoria LGAs from Aurin data: ' + (num_top/10)*100 + '%<br>';
		//div.innerHTML += (num_bot/10)*100 + '%'
	}

}
