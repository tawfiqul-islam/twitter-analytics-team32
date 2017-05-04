var config = { lga_url : '/data/vic-lga',
	scenario3_url: '/data/scenario3',
	melb_coordinates : [-37.8136, 144.9631],
	vic_coordinates : [-37.4713, 144.7852],
	// group_color: ['#fff7f3', '#fde0dd', '#fcc5c0', '#fa9fb5', '#f768a1', '#dd3497', '#ae017e', '#7a0177'],
	group_color: ['#fde0dd', '#fa9fb5', '#c51b8a'],
	null_color: '#737373',
	decimal_places: 2,
	number_str_size: 5  // length of the string representation of a number
}


// convert numerical values to categorical
function toCategorical(rows, column_infos) {
	result = [];

	function number_to_str(num) {
		x = Math.pow(10, config.decimal_places);
		
		// adapted from
		// http://stackoverflow.com/questions/6134039/format-number-to-always-show-2-decimal-places
		num = parseFloat(Math.round(num * x) / x).toFixed(config.decimal_places);
		
		// copied from
		// http://stackoverflow.com/questions/2998784/how-to-output-integers-with-leading-zeros-in-javascript
		var s = num+"";
		while (s.length < config.number_str_size) s = "0" + s;
		return s;
	}

	// create a string representation of each group
	for (var c in column_infos) {
		groups_str = [];
		groups = column_infos[c]['groups'];
		for (var i=0; i<groups.length; i++) {
			groups_str.push(number_to_str(groups[i][0]) + '-' + number_to_str(groups[i][1]));
		}
		column_infos[c]['groups_str'] = groups_str;
	}

	for (var i=0; i<rows.length; i++) {
		curr_row = {}
		for (var c in rows[i]) {
			if (!column_infos.hasOwnProperty(c)) {
				curr_row[c] = rows[i][c];
				continue;
			}

			var curr_value = rows[i][c].toFixed(config.decimal_places);
			var groups = column_infos[c]['groups']
			var curr_group = undefined;
			for (var j=0; j<groups.length; j++) {
				if (groups[j][0] <= curr_value && curr_value <= groups[j][1]) {
					curr_group = column_infos[c]['groups_str'][j];
					break;
				}
			}
			if (!curr_group) console.log('Error, A ' + c + ' value of ' + curr_value + ' does not belong to any of the groups ' + groups);
			curr_row[c] = curr_group;
		}
		result.push(curr_row);
	}
	return result;
}


function preprocess(scenario, need_dim_group) {
	// 'need_group_dim' is a flag to determine whether we need to add a crossfilter dimension and group into element in 'columns'

	// return all the properties in object 'l'
	function getKeys(l) {
		result = [];
		for (var o in l) {
			result.push(l[o].key);
		}
		return result
	}

	rows_categorical = toCategorical(scenario.rows, scenario.column_infos);

	var aurin_data = crossfilter(rows_categorical);

	// property: column name
	// value: an object with properties: getter, title, detail, groups, groups_str (and optionally, dimension and group)
	columns = {};
	for (var col in scenario.column_infos) {
		var curr = {
			getter: Function('row', 'return row["' + col + '"];'),
			title: scenario.column_infos[col].title,
			detail: scenario.column_infos[col].detail,
			groups: scenario.column_infos[col].groups,
			groups_str: scenario.column_infos[col].groups_str
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
		// TODO handle unhappy, neutral, happy

		columns[col] = curr;
	}
	return {columns: columns, aurin_data: aurin_data};
}
