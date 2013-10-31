var load_file_list = function() {
	$('#file_list').fadeOut('fast');
	$('#file_list').load('.', {'load_file_list': null}, function() {
		$('#file_list').fadeIn('fast');
		$('#file_list a').click(function(event) {
			event.preventDefault();
			var file_item = $(this).parent();
			var url = $(this).attr('href');
			$.get(url, function() {
				file_item.fadeOut('fast');
				file_item.remove();
			});
		});

	});
}
$(function() {
	load_file_list();
	$('#id_uploaded_file').change(function() {
		$('#file_upload form').submit();
	});
	$('#file_upload form').submit(function(event) {
		event.preventDefault();
		event.stopPropagation();
		var form = $(this);
		var file = $(this).find('input[type="file"]').get(0).files[0];
		//There's a serious BUG!!!!!!
		//Since the hashMe will somhow change the file, which leads to an estra upload.
		//hashMe(file, function(hex_md5) {
		//	form.ajaxSubmit({
		//		url: '.',
		//		data: {'uploaded_file': null,
		//		       'md5': hex_md5},
		//		complete: function() {
		//			load_file_list();					
		//		},
		//	});
		//});
		form.ajaxSubmit({
			url: '.',
			data: {'uploaded_file': null},
			complete: load_file_list,
		});
		return false; 
	});

});
