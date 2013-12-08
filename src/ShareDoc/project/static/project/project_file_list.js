var set_remove = function(file_list) {
	file_list.find('a.remove').click(function(event) {
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
			});
		});
	});
}

var load_file_list = function() {
	var file_list = $('#file_list');
	file_list.fadeOut('fast');
	$.post('.', {'load_file_list': null}, function(data) {
		file_list.html(data);
		file_list.fadeIn('fast');
		set_remove(file_list);
	});
}



$(function() {
	load_file_list();
});
