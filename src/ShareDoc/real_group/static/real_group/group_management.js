var set_link_behavior = function(callback) {
	$(this).find('a').click(function(event) {
		event.preventDefault();
		url = $(this).attr('href');
		$.get(url, callback);
	});
}

var load_user = function() {
	$('#manager_list').load('.', {'load_manager_list': null}, function() {
		set_link_behavior.call(this, load_user);
	});
	$('#member_list').load('.', {'load_member_list': null}, function() {
		set_link_behavior.call(this, load_user);
	});
}

$(function() {
	load_user();
});


var copy_text = function(hide_dom, show_dom) {
	var display_content = hide_dom.children('span').text();
	show_dom.find('p.error').text("");
	show_dom.find('input[type="text"]').val(display_content);
	show_dom.find('textarea').val(display_content);
}

$(function() {
	$('#modify_group_name').hide();
	$('#modify_group_description').hide();

	set_trigger_link(
		'div.group_basic_info a',
		'div.group_basic_info', 
		'div[id^="modify"]',
		'div[id^="display"]',
		copy_text
    	);
	set_cancel_button(
		'div.group_basic_info :button', 
		'div.group_basic_info', 
		'div[id^="modify"]',
		'div[id^="display"]'
    	);
});

var clear_search_result = function(hide_dom, show_dom) {
	show_dom.find('div.search_result').html("");
}

$(function() {
	$('div.apply_confirm').hide();
	set_trigger_link(
		'div.trigger > a',
		'div.apply_confirm_div',
		'div.apply_confirm',
		'div.trigger',
		clear_search_result
	);
	set_cancel_button(
		'div.apply_confirm :button',
		'div.apply_confirm_div',
		'div.apply_confirm',
		'div.trigger'
	);
});

$(function() {
	set_basic_info_form('div.group_basic_info form');
	set_search_form(
		'div.apply_confirm form',
		'div.apply_confirm',
		'p.error',
		'div.search_result'
	);
});

$(function() {
	$('div[id^="display_group"] a').hide();
	$('div[id^="display_group"]').hover(
		function() {
			$(this).children('a').fadeIn('fast');
		},
		function() {
			$(this).children('a').fadeOut('fast');
		}
	);
});
