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
				file_item.fadeOut('fast', function() {
					file_item.remove();
				});
			});
		});

	});
}
var create_message_action = function() {
	load_file_list();
	$('#file_upload input[type="file"]').fileupload({
		formData: {'uploaded_file': null},
		add: function(e, data) {
			console.log(data);
			upload_div = $('<div class="uploading"></div>')
				.append('<div class="uploading_file_name">' + data.files[0].name + '</div>')
				.append('<div class="progress"><div class="bar"></div></div>')
				.append('<a href="#">[取消]</a>');
			$('#uploading_list').append(upload_div);
			upload_div.children('a').click(function() {
				data.jqXHR.abort();
			});
			data.context = upload_div;
			data.submit();
		},
		progress: function(e, data) {
			var progress = parseInt(data.loaded / data.total * 100, 10);			
			data.context.find(".bar").css(
				'width',
				progress + '%'
			);
		},
		done: function(e, data) {
			data.context.fadeOut('fast', function() {
				data.context.remove();
			});
			load_file_list();
		},
		fail: function(e, data) {
			data.context.fadeOut('fast', function() {
				data.context.remove();
			});
		}
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
