var load_file_list = function() {
	$('#file_list').load('.', {'load_file_list': null}, function() {
		$('#file_list a:contains("Remove")').click(function(event) {
			event.preventDefault();
			var url = $(this).attr('href');
			$.get(url, load_file_list);
		});

	});
}

$(function() {
	load_file_list.call();
});
