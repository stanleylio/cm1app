(function() {

var panel_template = '<div class="panel panel-primary"><div class="panel-heading"><h1 class="panel-title"></h1></div><div class="panel-body"></div></div>';

function c2f(c) {
	return c*9/5 + 32;
}
function ms2kn(ms) {
	return ms*1.94384;
}
function m2ft(m) {
	//return m*100./2.54/12.;
	return 3.28083989501*m;
}
function uM2mgL(um) {
	return um*1e-6*(2*16)/1e-3;
}

function formatwd(d) {
	if ((d === null) || (d < 0)) {
		return '- m - ft.';
	} else {
		return d.toFixed(2) + 'm ' + m2ft(d).toFixed(1) + 'ft.';
	}
}


// initialize the panels
var tmp = $(panel_template);
tmp.find('.panel-heading .panel-title').append('Meteorological');
$('#met_panel').html(tmp);

tmp = $(panel_template);
tmp.find('.panel-heading .panel-title').append('Mākāhā 1');
$('#makaha1_panel').html(tmp);

tmp = $(panel_template);
tmp.find('.panel-heading .panel-title').append('Mākāhā 2');
$('#makaha2_panel').html(tmp);

tmp = $(panel_template);
tmp.find('.panel-heading .panel-title').append('Triple Mākāhā b');
$('#triplemakahab_panel').html(tmp);


//var d = JSON.parse(met_data);
$.getJSON('/poh/data/meteorological.json',function(d) {
	var tmp = $('#met_panel');
	tmp.find('.panel-body')
	.append($('<h1/>')
		.append($('<span class="label label-default">Air Temp.</span>'))
		.append($('<span/>',{
			text: ' ' + d.air_t[1].toFixed(1) + '℃ ' + c2f(d.air_t[1]).toFixed(1) + '℉',
			class:'panel-field',
			'data-ts':d.air_t[0],
		})))
	.append($('<h1/>')
		.append($('<span class="label label-default">Wind Speed</span>'))
		.append($('<span/>',{
			text: ' ' + ms2kn(d.wind_avg[1]).toFixed(1) + 'kn.',
			class:'panel-field',
			'data-ts':d.wind_avg[0],
		})))
	.append($('<h1/>')
		.append($('<span class="label label-default">Air Pressure</span>'))
		.append($('<span/>',{
			text: ' ' + (d.baro_p[1]*10).toFixed(0) + 'hPa',
			class:'panel-field',
			'data-ts':d.baro_p[0],
		})))
	.append($('<h1/>')
		.append($('<span class="label label-default">Humidity</span>'))
		.append($('<span/>',{
			text: ' ' + d.rh[1].toFixed(0) + '%',
			class:'panel-field',
			'data-ts':d.rh[0],
		})));
	color_status();
});


$.getJSON("/poh/data/location/makaha1/depth.json?minutes=15&max_count=60",function(d) {
	//console.log(d);
	try {
		//var latest_entry = _.maxBy(_.zip(d.ReceptionTime,d.depth),function(x) { return x[0] });
		var latest_avg = [_.mean(d.ReceptionTime),_.mean(d.depth)];
		
		$('#makaha1_panel').find('.panel-body')
		.append($('<h1/>')
			.append($('<span class="label label-primary">Depth</span>'))
			.append($('<span/>',{
			text: ' ' + formatwd(latest_avg[1]),
			class:'panel-field',
			'data-ts':latest_avg[0],
			})));
		color_status();
	} catch (e) {
		console.log(e);
	}
});

$.getJSON("/poh/data/location/makaha1/oxygen.json?minutes=15&max_count=60",function(d) {
	//console.log(d);
	try {
		//var latest_entry = _.maxBy(_.zip(d.ReceptionTime,d.oxygen),function(x) { return x[0] });
		var latest_avg = [_.mean(d.ReceptionTime),_.mean(d.oxygen)];
		//console.log(latest_avg);
		
		$('#makaha1_panel').find('.panel-body')
		.append($('<h1/>')
			.append($('<span class="label label-info">O<sub>2</sub></span>'))
			.append($('<span/>',{
			text: ' ' + latest_avg[1].toFixed(0) + 'μM ' + uM2mgL(latest_avg[1]).toFixed(1) + 'mg/L',
			class:'panel-field',
			'data-ts':latest_avg[0],
			})));
		color_status();
	} catch (e) {
		console.log(e);
	}
});

$.getJSON("/poh/data/location/makaha1/air.json?minutes=15&max_count=60",function(d) {
	//console.log(d);
	try {
		//var latest_entry = _.maxBy(_.zip(d.ReceptionTime,d.air),function(x) { return x[0] });
		var latest_avg = [_.mean(d.ReceptionTime),_.mean(d.air)];
		//console.log(latest_avg);
		
		$('#makaha1_panel').find('.panel-body')
		.append($('<h1/>')
			.append($('<span class="label label-info">Air Sat.</span>'))
			.append($('<span/>',{
			text: ' ' + d.air[1].toFixed(0) + '%',
			class:'panel-field',
			'data-ts':latest_avg[0],
			})));
		color_status();
	} catch (e) {
		console.log(e);
	}
});

$.getJSON("/poh/data/location/makaha1/temperature.json?minutes=15&max_count=60",function(d) {
	//console.log(d);
	try {
		var latest_avg = [_.mean(d.ReceptionTime),_.mean(d.temperature)];
		
		$('#makaha1_panel').find('.panel-body')
		.append($('<h1/>')
			.append($('<span class="label label-info">Water Temp.</span>'))
			.append($('<span/>',{
			text: ' ' + d.temperature[1].toFixed(1) + '℃ ' + c2f(d.temperature[1]).toFixed(1) + '℉',
			class:'panel-field',
			'data-ts':latest_avg[0],
			})));
		color_status();
	} catch (e) {
		console.log(e);
	}
});

$.getJSON("/poh/data/location/makaha2/depth.json?minutes=15&max_count=60",function(d) {
	//console.log(d);
	try {
		//var latest_entry = _.maxBy(_.zip(d.ReceptionTime,d.depth),function(x) { return x[0] });
		var latest_avg = [_.mean(d.ReceptionTime),_.mean(d.depth)];
		
		$('#makaha2_panel').find('.panel-body')
		.append($('<h1/>')
			.append($('<span class="label label-primary">Depth</span>'))
			.append($('<span/>',{
			text: ' ' + formatwd(latest_avg[1]),
			class:'panel-field',
			'data-ts':latest_avg[0],
			})));
		color_status();
	} catch (e) {
		console.log(e);
	}
});


/*//var d = JSON.parse(makaha1_data);
$.getJSON('/poh/data/location/makaha1.json',function(d) {
	//console.log(d);
	try {
		var tmp = $(panel_template);
		//console.log(tmp.find('.panel-title').prop('outerHTML'));
		tmp.find('.panel-heading .panel-title').append('Mākāhā 1');
		tmp.find('.panel-body')
		.append($('<h1/>',{
			//text: d.wd[1].toFixed(2) + 'm ' + m2ft(d.wd[1]).toFixed(1) + 'ft.',
			text: formatwd(d.wd[1]),
			class:'panel-field',
			'data-ts':d.wd[0],
			}))
		.append($('<h1/>',{
			text: d.Temperature[1].toFixed(1) + '℃ ' + c2f(d.Temperature[1]).toFixed(1) + '℉',
			class:'panel-field',
			'data-ts':d.Temperature[0],
			}))
		.append($('<h3/>')
			.append($('<span class="label label-info">O<sub>2</sub></span>'))
			.append($('<span/>',{
				text: ' ' + d.O2Concentration[1].toFixed(0) + 'μM ' + uM2mgL(d.O2Concentration[1]).toFixed(1) + 'mg/L',
				class:'panel-field',
				'data-ts':d.O2Concentration[0],
			})))
		.append($('<h3/>')
			.append($('<span class="label label-info">Air Sat.</span>'))
			.append($('<span/>',{
				text: ' ' + d.AirSaturation[1].toFixed(0) + '%',
				class:'panel-field',
				'data-ts':d.AirSaturation[0],
			})));

		$('#makaha1_panel').html(tmp);
		color_status();
	} catch (e) {
		console.log(e);
	}
});

//var d = JSON.parse(makaha2_data);
$.getJSON('/poh/data/location/makaha2.json',function(d) {
	//console.log(d);
	try {
		var tmp = $(panel_template);
		//console.log(tmp.find('.panel-title').prop('outerHTML'));
		tmp.find('.panel-heading .panel-title').append('Kahoʻokele (Mākāhā 2)');
		tmp.find('.panel-body')
		.append($('<h1/>',{
			//text: d.wd[1].toFixed(2) + 'm ' + m2ft(d.wd[1]).toFixed(1) + 'ft.',
			text: formatwd(d.wd[1]),
			class:'panel-field',
			'data-ts':d.wd[0],
			}))
		.append($('<h1/>',{
			text: d.Temperature[1].toFixed(1) + '℃ ' + c2f(d.Temperature[1]).toFixed(1) + '℉',
			class:'panel-field',
			'data-ts':d.Temperature[0],
			}))
		.append($('<h3/>')
			.append($('<span class="label label-info">O<sub>2</sub></span>'))
			.append($('<span/>',{
				text: ' ' + d.O2Concentration[1].toFixed(0) + 'μM ' + uM2mgL(d.O2Concentration[1]).toFixed(1) + 'mg/L',
				class:'panel-field',
				'data-ts':d.O2Concentration[0],
			})))
		.append($('<h3/>')
			.append($('<span class="label label-info">Air Sat.</span>'))
			.append($('<span/>',{
				text: ' ' + d.AirSaturation[1].toFixed(0) + '%',
				class:'panel-field',
				'data-ts':d.AirSaturation[0],
			})))
		.append($('<h3/>')
			.append($('<span class="label label-warning">Turbidity</span>'))
			.append($('<span/>',{
				text: ' ' + d.Turbidity_FLNTU[1].toFixed(0),
				class:'panel-field',
				'data-ts':d.Turbidity_FLNTU[0],
			})))
		.append($('<h3/>')
			.append($('<span class="label label-success">Chlorophyll</span>'))
			.append($('<span/>',{
				text: ' ' + d.Chlorophyll_FLNTU[1].toFixed(0),
				class:'panel-field',
				'data-ts':d.Chlorophyll_FLNTU[0],
			})));

		$('#makaha2_panel').html(tmp);
		color_status();
	} catch (e) {
		console.log(e);
	}
});

//var d = JSON.parse(makaha3_data);
$.getJSON('/poh/data/location/triplemakahab.json',function(d) {
	//console.log(d);
	try {
		var tmp = $(panel_template);
		//console.log(tmp.find('.panel-title').prop('outerHTML'));
		tmp.find('.panel-heading .panel-title').append('Triple Mākāhā b');
		tmp.find('.panel-body')
		.append($('<h1/>',{
			//text: d.wd[1].toFixed(2) + 'm ' + m2ft(d.wd[1]).toFixed(1) + 'ft.',
			text: formatwd(d.wd[1]),
			class:'panel-field',
			'data-ts':d.wd[0],
			}))
		.append($('<h1/>',{
			text: d.Temperature[1].toFixed(1) + '℃ ' + c2f(d.Temperature[1]).toFixed(1) + '℉',
			class:'panel-field',
			'data-ts':d.Temperature[0],
			}))
		.append($('<h3/>')
			.append($('<span class="label label-info">O<sub>2</sub></span>'))
			.append($('<span/>',{
				text: ' ' + d.O2Concentration[1].toFixed(0) + 'μM ' + uM2mgL(d.O2Concentration[1]).toFixed(1) + 'mg/L',
				class:'panel-field',
				'data-ts':d.O2Concentration[0],
			})))
		.append($('<h3/>')
			.append($('<span class="label label-info">Air Sat.</span>'))
			.append($('<span/>',{
				text: ' ' + d.AirSaturation[1].toFixed(0) + '%',
				class:'panel-field',
				'data-ts':d.AirSaturation[0],
			})));

		$('#triplemakahab_panel').html(tmp);
		color_status();
	} catch (e) {
		console.log(e);
	}
});*/

function color_status() {
	$('.panel-field').each(function(i,v) {
		//console.log(v);
		var field = $(v);
		//field.css('color','#E0E0E0');
		field.toggleClass('stale',(Date.now()/1000 - field.data('ts')) >= 3600);
		field.attr('title',$.timeago(new Date(field.data('ts')*1000)));
	});
}
})();