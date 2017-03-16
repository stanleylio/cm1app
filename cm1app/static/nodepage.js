(function() {
// global: site, node

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

//console.log('/' + site + '/nodepage/' + node + '.json');

$.getJSON('/' + site + '/nodepage/' + node + '.json',function(d) {
	//console.log(d);
	
	// - - - - -
	// table of latest readings
	// - - - - -
	var header = $('div.page-header div');
	header.append($('<h1/>',{text:d['name']}))
		.append($('<h4/>',{text:node + ' @ ' + d['location']}))
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

		//var l = '/' + site + '/nodepage/' + node + '/' + tag;
		var l = '/' + site + '/dataportal/' + node + '/' + tag;
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
		$(v).parent().attr('title',$.timeago(new Date($(v).data('ts')*1e3)));
		
		// mark the stale readings
		if (Date.now()/1e3 - $(v).data('ts') > 60*60) {
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
		var variable = readings[i]['var'];
		var caption = $('<div/>',{id:variable + '_caption',class:'caption','data-tag':variable});
		var imglink = '/static/img/' + site + '/' + node + '/' + variable + '.png';
		//var a = $('<a/>',{href:imglink,class:'thumbnail','data-lightbox':"plots",'data-title':variable + ' of ' + node});

		var a = $('<div/>',{class:'thumbnail'});
		a.append(caption);
		
		// now only the img is a link, not the whole patch
		// lightbox: add data-lightbox to the image link, not to the image
		//var tmp = $('<a/>',{href:imglink,'data-lightbox':"plots",'data-title':variable + ' of ' + node});
		var tmp = $('<a/>',{href:imglink,'data-lightbox':"plots",'data-title':variable});
		tmp.append($('<img/>',{src:imglink,class:'img-responsive'}));
		a.append(tmp);
		
		//a.append($('<img/>',{src:imglink,class:'img-responsive'}));
		var patch = $('<div class="col-xs-12 col-sm-6 col-lg-4"/>');
		patch.append(a);
		$('#static_plots').append(patch);
	}

	// generate the caption for each plot in the static plot grid
	$('div.caption').each(function(i,v) {
		var variable = $(v).data('tag');
		//$.getJSON('/static/' + site + '/' + node + '/' + readings[i]['var'] + '.json',function(d) {
		$.getJSON('/static/img/' + site + '/' + node + '/' + variable + '.json',function(d) {
			var span = d['time_end'] - d['time_begin'];
			var nday = Math.floor(span/24/60/60);
			var remain = span % (24*60*60);
			var nhour = Math.floor(span/60/60);
			span = Math.floor(remain/3600) + ' hours';
			if (nday > 0) {
				span = nday + ' days, ' + span;
			}
			$(v).append($('<h4/>',{text:variable}));
			//var imglink_bounded = '/static/' + site + '/bounded/' + node + '/' + variable + '.png';
			//$(v).append($('<h4><a href="' + imglink_bounded + '" title="filtered plot">' + variable + '</a></h4>'));
			$(v).append($('<p/>',{text:'Plot generated ' + $.timeago(new Date(d['plot_generated_at']*1000))}));
			$(v).append($('<p/>',{text: d['data_point_count'] + ' pts., ' + span}));
			$(v).append($('<p/>',{text: 'Last sample in plot: ' + $.timeago(new Date(d['time_end']*1000))}));
		});
	});

	$("#pagegeneratedts").html('<em><p>Page generated ' + $.timeago(Date.now()) + '</p></em>');
	
})
.fail(function(d,textStatus,error) {
	console.error("getJSON failed, status: " + textStatus + ", error: " + error)
});

lightbox.option({
	'resizeDuration':100,
	'fadeDuration':100,
	'wrapAround':false,
	'albumLabel':node
})

})();