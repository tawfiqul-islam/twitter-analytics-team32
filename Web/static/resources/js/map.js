d3.queue()
	.defer(d3.json, config.lga_url)
	.defer(d3.json, config.scenario3_url)
	.await(makeMap);

function makeMap(error, lga, scenario) {
	console.log(error);
	makeMap1(lga, scenario);
}


function makeMap1(lga, scenario) {

	data = preprocess(scenario); // see preprocess.js
	columns = data.columns;
	aurin_data = data.aurin_data

	var curr_groups_str = columns.internet_tt_3_percent_6_11_6_11.groups_str;
	var curr_getter = columns.internet_tt_3_percent_6_11_6_11.getter;
	var default_c = 'internet_tt_3_percent_6_11_6_11'; // use on first call to legend.update(default_c) and radio button with this id is checked by default

	// needed to get a column value by LGA code
	var lga_code_dimension = aurin_data.dimension(function (d) { return d.lga_code; });


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
			color: 'white',
			dashArray: '3',
			fillOpacity: 0.7
		};
	}


	// interaction on each polygon
	// adapted from http://leafletjs.com/examples/choropleth/
	function highlightFeature(e) {
		var layer = e.target;

		layer.setStyle({
			weight: 4,
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


	var my_map = L.map('mapid').setView(config.melb_coordinates, 8);

	// from https://leaflet-extras.github.io/leaflet-providers/preview/
	L.tileLayer('http://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
		maxZoom: 19,
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


	// column selection
	var column_selection = L.control({position: 'bottomleft'});

	// called on control.addTo(map)
	column_selection.onAdd = function (map) {
		var div = L.DomUtil.create('div', 'column-selection'); // create a div

		div.innerHTML = '<form name="cf">';
		for (var c in columns) {
			div.innerHTML += '<input type="radio" name="column_selection_radio" id="' + c + '" value="' + c + '" />' + columns[c].title + '<br>';
		}
		div.innerHTML += '</form>';
		return div;
	};
	column_selection.addTo(my_map);

	function columnSelectionHandler() {
		curr_getter = columns[this.value].getter;
		curr_groups_str = columns[this.value].groups_str;

		geojson.setStyle(style); // change overlay layer
		legend.update(this.value); // change legend
	}

	var radios = document.getElementsByName('column_selection_radio');
	for(var i = 0, max = radios.length; i < max; i++) {
		radios[i].onclick = columnSelectionHandler;
	}


	// adapted from http://leafletjs.com/examples/choropleth/
	var legend = L.control({position: 'bottomright'});
	legend.onAdd = function (map) {
		this._div = L.DomUtil.create('div', 'area-info legend');
		this.update(default_c);
		return this._div;
	};

	legend.update = function (c) {
		this._div.innerHTML = '<h4>' + columns[c].detail + '</h4>'
		for (var i = 0; i < curr_groups_str.length; i++) {
			this._div.innerHTML += '<i style="background:' + getColor(i) + '"></i> ';
			this._div.innerHTML += curr_groups_str[i] + '<br>';
		}
	}

	legend.addTo(my_map);

	// set which radio button is checked at the beginning
	document.getElementById(default_c).checked = true
}
