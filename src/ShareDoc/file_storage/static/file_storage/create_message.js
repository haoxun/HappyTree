var set_create_message_button = function(common_ancestor, hide) {
	common_ancestor.find('input.cancel_button').hide();
	common_ancestor.find('input.delete_button').click(function(event) {
		event.preventDefault();
		event.stopPropagation();
		common_ancestor.find('div.widget_loadder').slideUp('fast');
		hide.fadeIn('fast');
		var url = $(this).attr('href');
		$.get(url);
	});
}
$(function() {
	set_widget_trigger(
		'#create_message', 
		'a.message_widget_trigger', 
		'a.message_widget_trigger',
		set_create_message_button
	);
});
