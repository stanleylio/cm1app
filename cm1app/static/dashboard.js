(function() {

	function keys(d) {
	// get the list of "keys" of a given "dictionary"
		var keys = [];
		for (var key in d) {
			if (d.hasOwnProperty(key)) {
				keys.push(key);
			}
		}
		return keys.sort();
	}

	function node_status(d) {
		// all sample fresh and within range (if defined) -> 'online'
		// some samples stale / out of range (if defined) -> 'bad_sensor'
		// all samples stale / out of range (if defined) -> 'offline'
		var vars = keys(d);
		//var bad_count = 0;	# default good vs. default bad... think about the implications.
		//var bad_count = vars.length;
		var now = new Date()/1000;
		var bad_count = vars.map(function(v,i,a) {
			//console.log(v);
			try {
				// range check
				//var valid = true;
				var val = d[v][1];
				var range = d[v][3];
				if (typeof range != 'undefined') {
					//console.log(val,range);
					if ((!(range[0] === null)) && (val < range[0])) {
//console.log(v,val,range);
						//valid = false;
						return 1;
					}
					else if ((!(range[1] === null)) && (val > range[1])) {
//console.log(v,val,range);
						//valid = false;
						return 1;
					}
				}
				
				// a reading is good if it is recent and within range
				//if (((now - d[v][0]) <= 30*60 && valid)) {
				//if (((now - d[v][0]) <= 60*60 && valid)) {
				if (((now - d[v][0]) <= 60*60)) {
					return 0;
				}
				else
				{
//console.log(v,now - d[v][0]);
				}
			} catch(e) {
				console.log(e.message);
			}
			return 1;
		//}).reduce((p,c) => p + c);	// Safari doesn't like the arrow.
		}).reduce(function(pv,cv,i,a) {
			return pv + cv;
		});
		
		if (0 === bad_count) {
			return 'online';
		} else if (bad_count < vars.length) {
			return 'bad_sensor';
		} else {
			return 'offline';
		}
	}

	function color_status(d,table_label) {
		var label = ['#',table_label,' ul'].join('');
		//$('#dashboard_poh ul').children().each(function(idx) {
		$(label).children().each(function(idx) {
			var node_id = $(this).data('node_id');
//console.log(node_id);
			var tmp = node_status(d[node_id]['latest_non_null']);
			if ('online' === tmp) {
				$(this).addClass('list-group-item-success');
				$(this).removeClass('list-group-item-warning');
				$(this).removeClass('list-group-item-danger');
			} else if ('bad_sensor' === tmp) {
				$(this).removeClass('list-group-item-success');
				$(this).addClass('list-group-item-warning');
				$(this).removeClass('list-group-item-danger');
			} else if ('offline' === tmp) {
				$(this).removeClass('list-group-item-success');
				$(this).removeClass('list-group-item-warning');
				$(this).addClass('list-group-item-danger');
			}
		});
	}
	
	function build_table(data) {
		//console.log(data.site);
		//console.log(data.data_src);
		//console.log(data.data_src_name);

		// determine whether to show site location and data source
		var title = $('<div></div>');
		if (! $('#dashboard_' + data.site).data('status-only')) {
			title = $('<h4><a href="' + data.gmap_link + '" target="_blank">' + data.location + '</a></h4><p>Data source: ' + data.data_src_name + '</p>');
		}
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
		
		// color the table
		color_status(data.nodes,'dashboard_' + data.site);
	}
	
	// build a table of nodes for PoH
	var l = '/poh/data/dashboard.json';
	$.getJSON(l,build_table);

	// build a table of nodes for Makai Pier
	var l = '/makaipier/data/dashboard.json';
	$.getJSON(l,build_table);

	// auto refresh color of nodes in the background
	window.setInterval(function() {
		var l = '/poh/data/dashboard.json';
		$.getJSON(l,function(data) {
			color_status(data.nodes,'dashboard_poh');
		});
		var l = '/makaipier/data/dashboard.json';
		$.getJSON(l,function(data) {
			color_status(data.nodes,'dashboard_makaipier');
		});
	},5*60*1000);
})();
