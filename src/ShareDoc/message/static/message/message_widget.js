var set_remove = function(common_ancestor, file_list) {
	file_list.find('a').click(function(event) {
		event.preventDefault();
		var file_item = $(this).parent();
		var url = $(this).attr('href');
		var file_pointer_id = $(this).attr('file_pointer_id');
		$.ajax({
			type: 'DELETE',
			url: url,
		    data: {file_pointer_id: file_pointer_id}
		}).success(function() {
			file_item.fadeOut('fast', function() {
				file_item.remove();
				control_submit(common_ancestor);
			});
		});
	});
}

var load_file_list = function(common_ancestor) {
	var file_list = common_ancestor.find('div.file_list');
	file_list.fadeOut('fast');
	var url = file_list.attr('href');
	$.get(url, {'load_file_list': null}, function(data) {
		file_list.html(data);
		file_list.fadeIn('fast');
		set_remove(common_ancestor, file_list);
		control_submit(common_ancestor);
	});
}

var test_textarea_and_files = function(common_ancestor) {
	return common_ancestor.find('div.form_div textarea').val() != "" || common_ancestor.find('div.file_list').children().size() != 0;
}

var control_submit = function(common_ancestor) {
	if(test_textarea_and_files(common_ancestor)) {
		common_ancestor.find('div.final_operation input[type="submit"]').prop('disabled', false);
	}
	else {
		common_ancestor.find('div.final_operation input[type="submit"]').prop('disabled', true);
	}
}


var widget_action = function(common_ancestor, hide) {
	load_file_list(common_ancestor);
	// file upload
	common_ancestor.find('div.file_upload input[type="file"]').fileupload({
		formData: {
			'uploaded_file': null
		},
		add: function(e, data) {
			upload_div = $('<div class="uploading"></div>')
				.append('<div class="uploading_file_name">' + data.files[0].name + '</div>')
				.append('<div class="progress"><div class="bar"></div></div>')
				.append('<a href="#">[取消]</a>');
			common_ancestor.find('div.uploading_list').append(upload_div);
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
			// add file_dom to file list
			var uploaded_file_dom = $('<p class="remove">' + data.files[0].name + '</p>')
				.append('[<a href="' + data.result.url + '">remove</a>]');
			set_remove(common_ancestor, uploaded_file_dom);
			uploaded_file_dom.hide();
			common_ancestor.find('div.file_list').append(uploaded_file_dom);
			uploaded_file_dom.fadeIn('fast');
			
			control_submit(common_ancestor);
		},
		fail: function(e, data) {
			data.context.fadeOut('fast', function() {
				data.context.remove();
			});
		}
	});

	common_ancestor.find('div.form_div textarea').keyup(function() {
		control_submit(common_ancestor);
	});
}
