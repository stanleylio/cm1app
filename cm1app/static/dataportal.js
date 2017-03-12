$(function () {
	var time_col = 'ReceptionTime';
	var minutes = 60*24*60;
	var jsondata = null;
	var chart;

	function update_stats() {
		var extremes = chart.xAxis[0].getExtremes();
		var data = [
			['Time of latest sample',moment(extremes.dataMax).format('MMM Do YYYY, hh:mm:ss') + ' (' + moment(extremes.dataMax).fromNow() + ')'],
			['Time span',((extremes.dataMax - extremes.dataMin)/3600/1e3/24).toFixed(1) + ' day(s)'],
			//['Number of samples',chart.series[0].data.length],
			// hack
			['Number of samples',jsondata['samples'][time_col].length],
			['Time of oldest sample',moment(extremes.dataMin).format('MMM Do YYYY, hh:mm:ss')],
		];
		
		var table = $('<table class="table table-striped table-hover table-condensed table-sm table-bordered"/>');
		var thead = $("<thead><tr><th>Stats</th><th>Value</th></tr></thead>");
		var tbody = $('<tbody/>');
		for (let row of data) {
			$('<tr/>')
				.append($('<td/>').append($('<strong/>',{text:row[0]})))
				.append($('<td/>',{text:row[1]}))
			.appendTo(tbody);
		}
		table.append(thead).append(tbody);
		$('#stats_table').html(table);
	}
	
	$.getJSON('/' + site + '/data/' + node + '/' + variable + '.json?minutes=' + minutes,function(data) {
		//console.log(data);
		//console.log(data['samples'][time_col]);

		jsondata = data;	// save a copy for later use
		
		// extract data into a list of (t,x), with t converted from s to ms, sorted by t
		data = _.sortBy(_.zip(_.map(data['samples'][time_col],function(t) {return 1000*t;}), data['samples'][variable]),function(x) { return x[0]; });
		
		chart = new Highcharts.StockChart({
			chart: {
				renderTo: 'container',
				zoomType: 'x',
				events: {
					//load:...,
					//redraw: , buggy. doesn't work.
				},
			},
            title: {
                text: jsondata.description + ' (' + site + ' > ' + node + ' > ' + variable + ')',
            },
			plotOptions: {
				series: {
					dataGrouping: {
						enabled: true,
						approximation: 'average',
						units: [['minute',[1, 2, 5, 10, 15, 30]],
								['hour',[1,6,12]],
								['day',[1]],
								['week',[1]],
								],
						groupPixelWidth: 5,
					}
				}
			},
			rangeSelector: {
				buttons: [{
						type:'hour',
						count: 1,
						text: '1h'
					},{
						type:'day',
						count: 1,
						text: '1d'
					},{
						type:'week',
						count: 1,
						text: '1w'
					},{
						type:'month',
						count: 1,
						text: '1m'
					/*},{
						type:'all',
						text:'All'*/
					}],
				selected: 2,
			},
			xAxis: {
				ordinal: false,
				title: {
					text: 'Time (UTC)'
				}
			},
			yAxis: {
				title: {
					text: jsondata.unit,
				}
			},
            series: [{
                name: variable,
				//data: _.zip(_.map(data['samples'][time_col],function(t) {return 1000*t;}),data['samples'][variable]),
				data: data,
                lineWidth: 0,
				//dashStyle: 'longdash',
                marker: {
                    enabled: true,
                    radius: 2
                },
                tooltip: {
                    valueDecimals: 2
                },
                states: {
                    hover: {
                        lineWidthPlus: 0
                    }
                },
            }],
			credits: {
				enabled: false
			}
        });
		
		$('#download_button').show();

		update_stats();
	});
	
	$('#download_button').hide();
	
	$('#download_button').click(function() {
		$(this).attr('download',site + ',' + node + ',' + variable + '.csv');
		var tmp = _.zip(jsondata['samples'][time_col],jsondata['samples'][variable]);
		//var tmp = jsondata;
		for (var i = 0; i < tmp.length; i++) {
			tmp[i] = tmp[i].join(',');
		}
		var csv = tmp.join('\n');
		csv = time_col + ',' + variable + '\n' + csv;
		var data = new Blob([csv]);
		this.href = URL.createObjectURL(data);
	});

	// - - - - -
	
	/*function addpoint(data) {
		if (!(chart == null)) {
			//var series = chart.series[0];
			var series = chart.series;
			var shift = false;
			
			// add the new point
			var ts = Number(data['ts']*1000);
			var v = Number(data[variable]);
			series[0].addPoint([ts,v],true,shift);
		}
	}
		
	var url = "ws://grog.soest.hawaii.edu:9001";
	ws = new ReconnectingWebSocket(url);
	ws.onopen = function(evt) {
		//console.log(evt)
	};
	ws.onclose = function(evt) {
		//console.log("closed")
	};
	ws.onmessage = function(evt) {
		//console.log(evt.data);
		var data = JSON.parse(evt.data);
if ((data['node?'] === node) && (variable in data)) {
			addpoint(data);
		}
	};
	ws.onerror = function(evt) { console.log("error?") };*/
});
