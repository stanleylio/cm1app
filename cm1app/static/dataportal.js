$(function () {
	var time_col = 'ReceptionTime';
	var minutes = 90*24*60;
	//var minutes = 60;
	var json = null;
	$.getJSON('/' + site + '/data/' + node + '/' + variable + '.json?minutes=' + minutes,function(data) {
		//console.log(data);
		//console.log(data['samples'][time_col]);
		
		jsondata = data;
		
        $('#container').highcharts('StockChart', {
			chart: {
				zoomType: 'x',
			},
            rangeSelector: {
                selected: 2
            },
            title: {
                text: data.description + ' (' + site + ' > ' + node + ' >  ' + variable + ')',
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
								['month',[1]]],
						groupPixelWidth: 10,
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
					},{
						type:'all',
						text:'All'
					}]
			},
			yAxis: {
				title: {
					text: "it's beyond my paygrade"
				}
			},
            series: [{
                name: variable,
				data: _.zip(_.map(data['samples'][time_col],function(t) {return 1000*t;}),data['samples'][variable]),
                lineWidth: 0,
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
                }
            }],
			credits: {
				enabled: false
			}
        });
		
		$('#download_button').show();
	});
	
	$('#download_button').hide();
	
	$('#download_button').click(function() {
		$(this).attr('download',site + ',' + node + ',' + variable + '.csv');
		var tmp = _.zip(jsondata['samples'][time_col],jsondata['samples'][variable]);
		for (var i = 0; i < tmp.length; i++) {
			tmp[i] = tmp[i].join(',');
		}
		var csv = tmp.join('\n');
		csv = time_col + ',' + variable + '\n' + csv;
		var data = new Blob([csv]);
		this.href = URL.createObjectURL(data);
	});
});
