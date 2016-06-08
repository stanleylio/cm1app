(function() {

	function keys(d) {
	// get a list of "keys" of a "dictionary"
		var keys = [];
		for (var key in d) {
			if (d.hasOwnProperty(key)) {
				keys.push(key);
			}
		}
		return keys.sort();
	}

	function node_status(d) {
		// no sample stale -> 'online'
		// some samples stale -> 'bad_sensor'
		// all samples stale -> 'offline'
		var vars = keys(d);
		//var bad_count = 0;	# default good vs. default bad... think about the implications.
		//var bad_count = vars.length;
		var now = new Date()/1000;
		// given js' messy syntax I'm not sure this is any clearer than for(;;).
		var bad_count = vars.map(function(v,i,a) {
			try {
				// range check
				var valid = true;
				var val = d[v][1];
				var range = d[v][3];
				if (typeof range != 'undefined') {
					//console.log(val,range);
					if ((!(range[0] === null)) && (val < range[0])) {
						console.log(v,val,range);
						valid = false;
					}
					if ((!(range[1] === null)) && (val > range[1])) {
						console.log(v,val,range);
						valid = false;
					}
				}
				
				// a reading is good if it is recent and within range
				if (((now - d[v][0]) <= 30*60 && valid)) {
					return 0;
				}
			} catch(e) {
				console.log(e.message);
			}
			return 1;
		//}).reduce((p,c) => p + c);
		}).reduce(function(pv,cv,i,a) {
			return pv + cv;
		});
		
		/*var bad_count = vars.length;
		for (var i = 0; i < vars.length; i++) {	// js doesn't like dictionary...
			var v = vars[i];
			var valid = true;
			var val = d[v][1];
			var range = d[v][3];
			if (typeof range != 'undefined') {
				//console.log(val,range);
				if ((!(range[0] === null)) && (val < range[0])) {
					console.log(v,val,range);
					valid = false;
				}
				if ((!(range[1] === null)) && (val > range[1])) {
					console.log(v,val,range);
					valid = false;
				}
			}
			// a reading is good if it is recent and within range
			if (((now - d[v][0]) <= 30*60 && valid)) {
				bad_count--;
			}
		}*/
		if (0 === bad_count) {
			return 'online';
		} else if (bad_count < vars.length) {
			return 'bad_sensor';
		} else if (bad_count >= vars.length) {
			return 'offline';
		} else {
			console.log('huh?');
		}
	}

	function color_status(d,table_label) {
		var label = ['#',table_label,' ul'].join('');
		//$('#dashboard_poh ul').children().each(function(idx) {
		$(label).children().each(function(idx) {
			var node_id = $(this).data('node_id');
			var tmp = node_status(d[node_id]['latest_non_null']);
			if ('online' === tmp) {
				$(this).addClass('list-group-item-success');
			} else if ('bad_sensor' === tmp) {
				$(this).addClass('list-group-item-warning');
			} else if ('offline' === tmp) {
				$(this).addClass('list-group-item-danger');
			}
		});
	}
	
	function build_table(data) {
		//console.log(data.site);
		//console.log(data.data_src);
		//console.log(data.data_src_name);
		//var title = $('<h2>System Status</h2><h4>' + data.data_src_name + '</h4><p><a href="' + data.gmap_link + '">' + data.location + '</a></p>');
		var title = $('<h4>' + data.data_src_name + '</h4><p><a href="' + data.gmap_link + '" target="_blank">' + data.location + '</a></p>');
		var nodes = keys(data.nodes);
		//console.log(nodes);
		var ul = $('<ul class="list-group"></ul>');
		for (var i = 0; i < nodes.length; i++) {
			var node_id = nodes[i];
			var name = data.nodes[node_id]['name'];
			var loc = data.nodes[node_id]['location'];
			var li = $('<a/>',{
				href:'/' + data.site + '/nodepage/' + node_id,
				class:"list-group-item",
				'data-node_id':node_id,
				text:node_id + ' - ' + name});
			li.prop('title',loc);
			ul.append(li);
		}
		$('#dashboard_' + data.site).html(title.add(ul));
		
		// color the table of nodes
		color_status(data.nodes,'dashboard_' + data.site);
	}
	
// TODO: refactor this
	// build a table of nodes for PoH
	var l = '/poh/data/dashboard.json';
	$.getJSON(l,build_table);

	// build a table of nodes for Coconut Island
	var l = '/coconut/data/dashboard.json';
	$.getJSON(l,build_table);

	// auto refresh color of nodes in the background
	window.setInterval(function() {
		$.getJSON(l,function(data) {
			color_status(data.nodes,'dashboard_poh');
			color_status(data.nodes,'dashboard_coconut');
		});
	},5*60*1000);
})();
