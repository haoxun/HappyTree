var set_modify_trigger = function(common_ancestor_dom, trigger_dom, hide_dom, set_button, get_widget) {
	var trigger = $(trigger_dom);
	trigger.click(function(event) {
		event.preventDefault();
		var common_ancestor = $(this).parents(common_ancestor_dom);
		var hide = common_ancestor.find(hide_dom);
		var url = $(this).attr('href');
		$.get(url, function(data) {
			var widget_loadder = common_ancestor.find('div.widget_loadder');
			widget_loadder.html(data);
			widget_action(common_ancestor, hide);
			set_button(common_ancestor, hide);
			hide.fadeOut('fast');
			widget_loadder.slideDown('fast');
		});
	});
}

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
		$.ajax({
			type: 'DELETE',
			url: url
		});
		common_ancestor.fadeOut('slow', function() {
			common_ancestor.remove();
		});
	});
	common_ancestor.find('div.widget_loadder').find('div.post_message').find('form').submit(function(event) {
		event.preventDefault();
		event.stopPropagation();
		var form = $(this);
		var post_str = form.serialize();
		var submit_name = form.find('input[type="submit"]').attr('name');
		post_str += ('&' + submit_name + '=');
		var url = form.attr('action');
		$.ajax({
			type: 'PUT',
			url: url,
			data: post_str,

		}).success(function() {
			load_message_list();
		});
		return false;		
	});
}

var load_message_list = function() {
	$('#message_container').load('.', {'load_message_list': null}, function() {
		set_modify_trigger(
			'div.user_post_message',
			'a.posted_message_widget_trigger',
			'div.display_message, a.posted_message_widget_trigger',
			set_message_list_button
		);
	});
}
$(function() {
	load_message_list();
});
