var load_file_list = function() {
	$('#ac_list').load('.', {'load_ac_list': null}, function() {
		$('#ac_list a').click(function(event) {
			event.preventDefault();
			link = $(this);
			var url = link.attr('href');
			$.get(url, function() {
				link.parent().fadeOut('fast');
			});
		});
	});
}

$(function() {
	load_file_list.call();
});
