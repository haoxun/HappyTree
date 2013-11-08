var set_message_list_button = function(common_ancestor, hide) {
	common_ancestor.find('input.cancel_button').click(function(event) {
		event.preventDefault();
		event.stopPropagation();
		common_ancestor.find('div.widget_loadder').slideUp('fast');
		hide.fadeIn('fast');
	});
	common_ancestor.find('input.delete_button').click(function(event) {
		event.preventDefault();
		event.stopPropagation();
		var url = $(this).attr('href');
		$.get(url);
		common_ancestor.fadeOut('slow', function() {
			common_ancestor.remove();
		});
	});
}

$(function() {
	$('#message_container').load('.', {'load_message_list': null}, function() {
		set_widget_trigger(
			'div.message',
			'a.posted_message_widget_trigger',
			'div.display_message, a.posted_message_widget_trigger',
			set_message_list_button
		);
	});
});
