var config = { lga_url : '/data/vic-lga',
	scenario_url: '/data/scenario/' + arg['which_scenario'],
	melb_coordinates : [-37.8136, 144.9631],
	vic_coordinates : [-37.4713, 144.7852],
	group_color: ['#fde0dd', '#fa9fb5', '#c51b8a'],
	null_color: '#969696',
	decimal_places: 2,
	number_str_size: 5,  // length of the string representation of a number
	index_to_category: {0: 'Low', 1: 'Medium', 2: 'High'},
	label_to_emoji_png: {
		'happy': '../static/resources/data/emoji_happy.png',
		'neutral': '../static/resources/data/emoji_neutral.png',
		'unhappy': '../static/resources/data/emoji_unhappy.png',
	},
	icon_png: ['../static/resources/data/apple.png', '../static/resources/data/fries.png', '../static/resources/data/burger.png']
}


function numberToStr(num) {
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

function roundNum(num) {
	return +num.toFixed(config.decimal_places);
}

// convert numerical values to categorical
function toCategorical(rows, column_infos) {
	result = [];

	// create a string representation of each group
	for (var c in column_infos) {
		groups_str = [];
		groups = column_infos[c]['groups'];
		for (var i=0; i<groups.length; i++) {
			// convert to str
			groups_str.push(numberToStr(groups[i][0]) + '-' + numberToStr(groups[i][1]));

			// round to the correct decimal places so that we can group properly
			// otherwise, we might get an error
			// for example, we can't classify 0.29 
			// with groups: [0.1,0.28], [0.29000000000000004,0.44], [0.45,3.23]
			groups[i][0] = roundNum(groups[i][0]);
			groups[i][1] = roundNum(groups[i][1]);
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

			var curr_value = roundNum(rows[i][c]);
			var groups = column_infos[c]['groups']
			var curr_group = undefined;
			for (var j=0; j<groups.length; j++) {
				if (groups[j][0] <= curr_value && curr_value <= groups[j][1]) {
					curr_group = column_infos[c]['groups_str'][j];
					break;
				}
			}
			if (!curr_group) {
				console.log('Error, A ' + c + ' value of ' + curr_value + ' does not belong to any of the groups ' + groups);
			}
			curr_row[c] = curr_group;
		}
		result.push(curr_row);
	}
	return result;
}


function preprocess(scenario, need_dim_group, to_categorical) {
	// 'need_group_dim' is a flag to determine whether we need to add a crossfilter dimension and group into element in 'columns'

	// return all the properties in object 'l'
	function getKeys(l) {
		result = [];
		for (var o in l) {
			result.push(l[o].key);
		}
		return result
	}

	var rows = scenario.rows;
	if (to_categorical) { rows = toCategorical(scenario.rows, scenario.column_infos); }

	var data = crossfilter(rows);

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
		var dimension = data.dimension(curr.getter);
		var group = dimension.group();
		if (need_dim_group) {
			curr.dimension = dimension;
			// we want the number of areas in each of the category
			// e.g. we want how many areas is in low, medium, high soft drink consumption
			curr.group = group.reduceCount();
		}

		columns[col] = curr;
	}
	return {columns: columns, data: data};
}
