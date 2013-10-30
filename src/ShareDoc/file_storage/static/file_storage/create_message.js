var load_file_list = function() {
	$('#file_list').load('.', {'load_file_list': null}, function() {
		$('#file_list a').click(function(event) {
			event.preventDefault();
			var url = $(this).attr('href');
			$.get(url, load_file_list);
		});

	});
}
$(function() {
	load_file_list.call();
	$('#file_upload form').submit(function(event) {
		var form = $(this);
		var file = $(this).find('input[type="file"]').get(0).files[0];
		new hashMe(file, function(hex_md5) {
			form.ajaxSubmit({
				url: '.',
				data: {'uploaded_file': null,
				       'md5': hex_md5},
				complete: load_file_list,
			});
		});

		return false; 
	});

});
