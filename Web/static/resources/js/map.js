var config = {
	lga_url : '/data/vic-lga',
	scenario_1_url: '/data/scenario-1',
	melb_coordinates : [-37.8136, 144.9631],
	vic_coordinates : [-37.4713, 144.7852],
	// group_color: ['#fff7f3', '#fde0dd', '#fcc5c0', '#fa9fb5', '#f768a1', '#dd3497', '#ae017e', '#7a0177'],
	group_color: ['#fde0dd', '#fa9fb5', '#c51b8a'],
	null_color: '#737373'
}


d3.queue()
	.defer(d3.json, config.lga_url)
	.defer(d3.json, config.scenario_1_url)
	.await(makeMapAndGraphs);

function makeMapAndGraphs(error, lga, scenario_1) {
	makeMap(lga, scenario_1);
	//makeGraphs(lga);
}


function makeMap(lga, scenario_1) {
	function internet_getter(row) { return row.internet_access.internet_tt_3_percent_6_11_6_11; }
	function sitting_getter(row) { return row.sitting_hours.significance; }

	var aurin_data = crossfilter(scenario_1.rows);

	// create crossfilter dimensions
	var lga_code_dimension = aurin_data.dimension(function (d) { return d.lga_code; });
	var internet_dimension = aurin_data.dimension(internet_getter);
	var sitting_dimension = aurin_data.dimension(sitting_getter);

	// create crossfilter groups
	var internet_group = internet_dimension.group();
	var sitting_group = sitting_dimension.group();

	function getKeys(l) {
		result = new Array;
		for (var o in l) {
			result.push(l[o].key);
		}
		return result
	}

	internet_categories = getKeys(internet_group.all()).sort();
	sitting_categories = ['low', 'medium', 'high'];

	// i is the index of the color
	function getColor(i) {
		if (i == -1) {
			return config.null_color;
		}
		return config.group_color[i];
	}

	var curr_categories = internet_categories;
	var curr_getter = internet_getter;


	function fill_color(lga_code) {
		var row = lga_code_dimension.filter(lga_code).top(1)[0];
		var i = -1;
		if (row) i = curr_categories.indexOf(curr_getter(row));
		return getColor(i);
	}

	function style(feature) {
		return {
			fillColor: fill_color(feature.properties.lga_code),
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
		// TODO make more general
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
		if (properties) this._div.innerHTML += '<h5>' + properties.lga_name + '</h5><p>info here</p>';
	};
	info.addTo(my_map);


	// column selection
	var column_selection = L.control({position: 'topleft'});

	// called on control.addTo(map)
	column_selection.onAdd = function (map) {
		var div = L.DomUtil.create('div', 'column-selection'); // create a div
		
		div.innerHTML = '<form name="cf">';
		div.innerHTML += '<input type="radio" name="column_selection_radio" value="internet" checked="checked" />Internet Access<br>';
		div.innerHTML += '<input type="radio" name="column_selection_radio" value="sitting" />Sitting<br>'
		div.innerHTML += '</form>';
		return div;
	};
	column_selection.addTo(my_map);

	function column_selection_handler() {
		if (this.value == 'internet') {
			curr_getter = internet_getter;
			curr_categories = internet_categories;
		} else {
			curr_getter = sitting_getter;
			curr_categories = sitting_categories;
		}
		geojson.setStyle(style); // change overlay layer
		legend.update(); // change legend
	}

	var radios = document.getElementsByName('column_selection_radio');
	for(var i = 0, max = radios.length; i < max; i++) {
		radios[i].onclick = column_selection_handler;
	}


	// adapted from http://leafletjs.com/examples/choropleth/
	var legend = L.control({position: 'bottomright'});
	legend.onAdd = function (map) {
		this._div = L.DomUtil.create('div', 'area-info legend');
		this.update();
		return this._div;
	};

	legend.update = function () {
		this._div.innerHTML = '<h4>TODO title <br></h4>' // TODO
		for (var i = 0; i < curr_categories.length; i++) {
			this._div.innerHTML += '<i style="background:' + getColor(i) + '"></i> ';
			this._div.innerHTML += curr_categories[i] + '<br>';
		}
	}

	legend.addTo(my_map);

}
