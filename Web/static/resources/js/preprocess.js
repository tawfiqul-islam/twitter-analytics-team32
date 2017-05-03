var config = { lga_url : '/data/vic-lga',
	scenario1_url: '/data/scenario1',
	melb_coordinates : [-37.8136, 144.9631],
	vic_coordinates : [-37.4713, 144.7852],
	// group_color: ['#fff7f3', '#fde0dd', '#fcc5c0', '#fa9fb5', '#f768a1', '#dd3497', '#ae017e', '#7a0177'],
	group_color: ['#fde0dd', '#fa9fb5', '#c51b8a'],
	null_color: '#737373'
}


function preprocess(scenario, need_dim_group) {
	// 'need_group_dim' is a flag to determine whether we need to add a crossfilter dimension and group into element in 'columns'

	// return all the properties in object 'l'
	function getKeys(l) {
		result = new Array;
		for (var o in l) {
			result.push(l[o].key);
		}
		return result
	}

	var aurin_data = crossfilter(scenario.rows);

	// properties: column names in our AURIN data
	// value: an object with properties: file, col, getter, title, detail, categories (and optionally, dimension and group)
	columns = new Object();
	for (var file in scenario.column_titles) {
		for (var col in scenario.column_titles[file]) {
			var curr = {
				file: file,
				col: col,
				// getter: function (row) { return row[this.file][this.col]; }
				getter: Function('row', 'return row["' + file + '"]["' + col + '"];'),
				title: scenario.column_titles[file][col].title,
				detail: scenario.column_titles[file][col].detail
			}
			
			// determine list of categories
			var dimension = aurin_data.dimension(curr.getter);
			var group = dimension.group();
			if (need_dim_group) {
				curr.dimension = dimension;
				// we want the number of areas in each of the category
				// e.g. we want how many areas is in low, medium, high soft drink consumption
				curr.group = group.reduceCount();
			}
			curr['categories'] = getKeys(group.all()).sort();
			if (curr['categories'].indexOf('medium') > -1) {
				// we cannot simply sort
				curr['categories'] = ['low', 'medium', 'high'];
			}

			var key = file + '_' + col;
			columns[key] = curr; // add to our dict
		}
	}
	return {columns: columns, aurin_data: aurin_data};
}
