(function() {
/* note:
	I can either have the server embed the data as JSON in a js variable inside the html file, or
	I can have the client do AJAX.
	
	I'd also like to have the panels grey out the stale readings, if not asking for server for new readings.
	
	To have both the styling has to be independent from formatting of the readings. But if writing to
	the fields and styling them are separate, the call to styling will have to be called upon (each and every)
	successful AJAX calls.
	
	One of those time when lumping everything together actually saves dev work and performs better.
*/

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

//var d = JSON.parse(met_data);
$.getJSON('/poh/data/meteorological.json',function(d) {
	//console.log(d);
	// there is not much common to all of them...
	//<stuff class="tsr" data-value="" data-time="" data-unit="" data-precision="" data-style="<h1>"></stuff>
	var tmp = $(panel_template);
	tmp.find('.panel-heading .panel-title').append('Meteorological');
	tmp.find('.panel-body')
	/* being able to toggle the display unit would be nice, but then it would have 
	to be persistent over page reload... which means some form of persistent local
	storage (cookie). Maybe later.
	.append($('<div/>',{
		text:'air temperature',
		'class':'panel-field',
		title:$.timeago(new Date(d.air_t[0]*1000)),
		'data-val':JSON.stringify([d.air_t[1].toFixed(1),c2f(d.air_t[1]).toFixed(1)]),
		'data-unit':JSON.stringify(['℃','℉']),
		'data-disp-idx':1,
		}))*/
	.append($('<h1/>',{
		text: d.air_t[1].toFixed(1) + '℃ ' + c2f(d.air_t[1]).toFixed(1) + '℉',
		class:'panel-field',
		'data-ts':d.air_t[0],
		}))
	.append($('<h1/>',{
		text: ms2kn(d.wind_avg[1]).toFixed(1) + 'kn.',
		class:'panel-field',
		'data-ts':d.wind_avg[0],
		}))
	.append($('<h3/>',{
		text: (d.baro_p[1]*10).toFixed(0) + 'hPa',
		class:'panel-field',
		'data-ts':d.baro_p[0],
		}))
	.append($('<h3/>')
		.append($('<span class="label label-default">Humidity</span>'))
		.append($('<span/>',{
			text: ' ' + d.rh[1].toFixed(0) + '%',
			class:'panel-field',
			'data-ts':d.rh[0],
		})));
	
	$('#met_panel').html(tmp);
	color_status();
});

/*$('#met_panel div.panel-field').each(function(i,v) {
	console.log(v);
	var field = $(v);
	var idx = field.data('disp-idx');
	
	field.html($('<h1/>').text(field.data('val')[idx] + field.data('unit')[idx]));
}).click(function() {
	// toggle...
});*/

//var d = JSON.parse(makaha1_data);
$.getJSON('/poh/data/makaha/makaha1.json',function(d) {
	//console.log(d);
	try {
		var tmp = $(panel_template);
		//console.log(tmp.find('.panel-title').prop('outerHTML'));
		tmp.find('.panel-heading .panel-title').append('Mākāhā 1');
		tmp.find('.panel-body')
		.append($('<h1/>',{
			text: d.wd[1].toFixed(2) + 'm ' + m2ft(d.wd[1]).toFixed(1) + 'ft.',
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
$.getJSON('/poh/data/makaha/makaha2.json',function(d) {
	//console.log(d);
	try {
		var tmp = $(panel_template);
		//console.log(tmp.find('.panel-title').prop('outerHTML'));
		tmp.find('.panel-heading .panel-title').append('Kahoʻokele (Mākāhā 2)');
		tmp.find('.panel-body')
		.append($('<h1/>',{
			text: d.wd[1].toFixed(2) + 'm ' + m2ft(d.wd[1]).toFixed(1) + 'ft.',
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
$.getJSON('/poh/data/makaha/triplemakahab.json',function(d) {
	//console.log(d);
	try {
		var tmp = $(panel_template);
		//console.log(tmp.find('.panel-title').prop('outerHTML'));
		tmp.find('.panel-heading .panel-title').append('Triple Mākāhā b');
		tmp.find('.panel-body')
		.append($('<h1/>',{
			text: d.wd[1].toFixed(2) + 'm ' + m2ft(d.wd[1]).toFixed(1) + 'ft.',
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
});

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