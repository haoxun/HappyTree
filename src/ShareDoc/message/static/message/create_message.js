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
	common_ancestor.find('div.widget_loadder').find('div.post_message').find('form').submit(function(event) {
		event.preventDefault();
		event.stopPropagation();
		var form = $(this);
		var post_str = form.serialize();
		var submit_name = form.find('input[type="submit"]').attr('name');
		post_str += ('&' + submit_name + '=');
		var url = form.attr('action');
		$.post(url, post_str, function() {
			load_message_list();
			common_ancestor.find('div.widget_loadder').slideUp('fast');
			hide.fadeIn('fast');
		});
		return false;		
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
