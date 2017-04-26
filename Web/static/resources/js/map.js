var config = {
	lga_url : '/data/vic-lga',
	melb_coordinates : [-37.8136, 144.9631],
	vic_coordinates : [-37.4713, 144.7852]
}


d3.queue()
	.defer(d3.json, config.lga_url)
	.await(makeMapAndGraphs);

function makeMapAndGraphs(error, lga) {
	makeMap(lga);
	//makeGraphs(lga);
}


function makeMap(lga) {
	var my_map = L.map('mapid').setView(config.melb_coordinates, 8);

	// from https://leaflet-extras.github.io/leaflet-providers/preview/
	L.tileLayer('http://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
		maxZoom: 19,
		attribution: '&copy; <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a>'
	}).addTo(my_map);

	var geojson;


	// color based on area of polygon
	group_area = [3];
	for (var i = 0; i < 6; i++) {
		group_area.push(group_area[i] * group_area[i]);
	}
	// TODO move to config
	group_color = ['#fff7f3', '#fde0dd', '#fcc5c0', '#fa9fb5', '#f768a1', '#dd3497', '#ae017e', '#7a0177']
	function getColor(d) {
		var i;
		for (i = group_area.length-1; i >= 0; i--){
			if (d > group_area[i]) return group_color[group_area.length-1-i];
		}
		return group_color[group_color.length-1];
	}

	function style(feature) {
		return {
			fillColor: getColor(feature.properties.AREASQKM16),
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

	geojson = L.geoJson(lga, {
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

	// TODO legend

	info.addTo(my_map);
}
