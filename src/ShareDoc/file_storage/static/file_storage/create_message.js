var load_file_list = function() {
	$('#file_list').fadeOut('fast');
	var url = $('#file_list').attr('href');
	$('#file_list').load(url, {'load_file_list': null}, function() {
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
var create_message_action = function() {
	load_file_list();
	$('#id_uploaded_file').change(function() {
		$('#file_upload form').submit();
	});
	$('#file_upload form').submit(function(event) {
		event.preventDefault();
		event.stopPropagation();
		var form = $(this);
		var url = form.attr('href');
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
			url: url,
			data: {'uploaded_file': null},
			complete: load_file_list,
		});
		return false; 
	});
}

$(function() {
	$('#init_target').hide();
	$('#init').click(function(event) {
		event.preventDefault();
		var url = $(this).attr('href');
		$.get(url, {'load_message': null}, function(data) {
			$('#init').fadeOut('fast');
			$('#init_target').html(data);
			create_message_action();
			$('#init_target').slideDown('fast');
			$('#final_operation input[type="button"]').click(function(event) {
				event.preventDefault();
				event.stopPropagation();
				$('#init_target').slideUp('fast');
				$('#init').fadeIn('fast');
				var url = $(this).attr('href');
				$.get(url);
			});

		});
	});
});
