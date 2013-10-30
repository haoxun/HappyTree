
$(function() {
	$('#file_upload form').submit(function(event) {
		var form = $(this);
		var file = $(this).find('input[type="file"]').get(0).files[0];
		new hashMe(file, function(hex_md5) {
			form.ajaxSubmit({
				url: '.',
				data: {'uploaded_file': null,
				       'md5': hex_md5},
			});
		});

		return false; 
	});

});
