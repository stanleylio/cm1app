(function() {
// global: site, node_id

	// from dashboard.js
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
	
$.getJSON('/' + site + '/nodepage/' + node_id + '.json',function(d) {
	//console.log(d);
	
	// - - - - -
	// table of latest readings
	// - - - - -
	var header = $('div.page-header div');
	header.append($('<h1/>',{text:d['name']}))
		.append($('<h4/>',{text:node_id + ' @ ' + d['location']}))
		.append($('<p/>',{text:d['note']}));
	var table = $('<table class="table table-striped table-hover table-condensed"/>');
	var thead = $("<thead><tr><th>Variable</th><th>Value</th><th>Unit</th><th>Description</th></tr></thead>");
	var tbody = $('<tbody/>');
	var readings = d['readings'];

	//for (var i = 0; i < keys(readings).length; i++) {
	for (var i in readings) {
		//console.log($('<td/>',{text:readings[i][0]}).prop('outerHTML'));
		var tag = readings[i]['var'];
		var ts = readings[i]['ts'];
		var val = readings[i]['val'];
		var unit = readings[i]['unit'];
		var range = readings[i]['range'];
		var description = readings[i]['desc'];
		
		if (null === unit) {
			unit = '-';
		}
		
		var valid = true;
		if (typeof range != 'undefined') {
			if ((!(range[0] === null)) && (val < range[0])) {
				valid = false;
			}
			if ((!(range[1] === null)) && (val > range[1])) {
				valid = false;
			}
		}

		var l = '/' + site + '/nodepage/' + node_id + '/' + tag;
		$('<tr/>')
			.append($('<td/>').append($('<a/>',{href:l,text:tag})))
			.append($('<td/>',{text:val,'data-ts':ts,'data-valid':valid}))
			.append($('<td/>',{text:unit}))
			.append($('<td/>',{text:description}))
		.appendTo(tbody);
	}
	table.append(thead).append(tbody);
	$('#table').html(table);
	
	$('td[data-ts]').each(function(i,v) {
		// show "time ago" on hover
		$(v).parent().attr('title',$.timeago(new Date($(v).data('ts')*1000)));
		
		// mark the stale readings
		if (Date.now()/1000 - $(v).data('ts') > 30*60) {
			$(v).parent().addClass('stale');
		} else {
			if (!$(v).data('valid')) {
				// fresh, but not valid
				$(v).addClass('invalid_reading');
			}
		}
	});
	//$('time.timeago').timeago();
	
	// - - - - -
	// static plot grid stuff
	// - - - - -
	//for (var i = 0; i < readings.length; i++) {
	for (var i in readings) {
		//console.log(readings[i][0]);
		var caption = $('<div/>',{id:readings[i]['var'] + '_caption',class:'caption','data-tag':readings[i]['var']});
		var imglink = '/static/' + site + '/' + node_id + '/' + readings[i]['var'] + '.png';
		var a = $('<a/>',{href:imglink,class:'thumbnail','data-lightbox':"plots",'data-title':readings[i]['var'] + ' of ' + node_id});
		a.append(caption);
		a.append($('<img/>',{src:imglink,class:'img-responsive'}));
		var patch = $('<div class="col-xs-12 col-sm-6 col-lg-4"/>');
		patch.append(a);
		$('#static_plots').append(patch);
	}

	// Add caption to each plot in the static plot grid
	$('div.caption').each(function(i,v) {
		$.getJSON('/static/' + site + '/' + node_id + '/' + readings[i]['var'] + '.json',function(d) {
			var span = d['time_end'] - d['time_begin'];
			var nday = Math.floor(span/24/60/60);
			var remain = span % (24*60*60);
			var nhour = Math.floor(span/60/60);
			span = Math.floor(remain/3600) + " hours";
			if (nday > 0) {
				span = nday + " days, " + span;
			}
			$(v).append($('<h4/>',{text:$(v).data('tag')}));
			$(v).append($('<p/>',{text:'Plot generated ' + $.timeago(new Date(d['plot_generated_at']*1000))}));
			$(v).append($('<p/>',{text: d['data_point_count'] + ' pts. | ' + span}));
			$(v).append($('<p/>',{text: 'Last sample in plot: ' + $.timeago(new Date(d['time_end']*1000))}));
		});
	});

	$("#pagegeneratedts").html('<em><p>Page generated ' + $.timeago(Date.now()) + '</p></em>');
	
	lightbox.option({
		'resizeDuration':200,
		'fadeDuration':200,
		'wrapAround':false,
		'albumLabel':'static plots'
	})
});
})();