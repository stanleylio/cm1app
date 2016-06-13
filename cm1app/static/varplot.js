(function() {
	//alert(site);
	//alert(node_id);
	//alert(variable);

	$('#option_7d').on('click',function() {
		gen_plot(site,node_id,variable,variable + ' of ' + node_id,60*24*7);
	});
	$('#option_12h').on('click',function() {
		gen_plot(site,node_id,variable,variable + ' of ' + node_id,60*12);
	});
	$('#option_1h').on('click',function() {
		gen_plot(site,node_id,variable,variable + ' of ' + node_id,60);
	});

	gen_plot(site,node_id,variable,variable + ' of ' + node_id,60*24*7);

	function tzcorrect(ts) {
		// convert POSIX timestamps to Date in local time zone
		var offset = (new Date).getTimezoneOffset()*60;
		for (var i = 0; i < ts.length; i++) {
			//ts[i] = (new Date(ts[i]*1000)).toISOString().replace('T',' ').replace('Z','');
			ts[i] = (new Date((ts[i] - offset)*1000)).toISOString().replace('T',' ').replace('Z','');
		}
		return ts;
	}
	
	function gen_plot(site,node,variable,linelabel,span) {
		var datapath = '/' + site + '/data/' + node + '/' + variable + '.json?minutes=' + span;
		console.log(datapath);
		$.getJSON(datapath,function(d) {
			var unit = d.unit;
			var description = d.description;
			var samples = d.samples;
			
			if (null === unit) {
				unit = '(unitless)';
			}
			
			var ts = samples.Timestamp;
			if ('ReceptionTime' in samples) {
				ts = samples.ReceptionTime;
			}
			ts = tzcorrect(ts);

			var x = samples[variable];
			
			var layout = {
				title: description + ' from ' + node_id,
				titlefont: {
					family: 'Helvetica, monospace',
					size: 20,
					color: '#7f7f7f'
				},
				autosize: false,
				width: 960,
				height: 500,
				xaxis: {
				title: new Date().toString().split(/(\(.*\))/)[1],
				titlefont: {
					family: 'Helvetica, monospace',
					size: 18,
					color: '#7f7f7f'
				}
				},
				yaxis: {
					title: variable + ', ' + unit,
					titlefont: {
					family: 'Helvetica, monospace',
					size: 18,
					color: '#7f7f7f'
				}
				},
				margin: { l:100, r:50, b:80, t:50, pad:4 },
			};
			
			var trace1 = { x: ts, y: x, name: linelabel, mode: "line+markers"};
			var traces = [trace1];
			
			$('#plot').empty();
			//Plotly.plot( $('#plot')[0],traces,layout);
			Plotly.newPlot( $('#plot')[0],traces,layout);
			
		}).fail(function(jqxhr,textStatus,error) {
			console.log('gen_plot() .getJSON() failed');
			console.log(textStatus);
			console.log(error);
		});
	}
})();
