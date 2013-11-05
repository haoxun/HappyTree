var set_link_behavior = function() {
	$('div.member_list a').click(function(event) {
		event.preventDefault();
		url = $(this).attr('href');
		$.get(url);
		load_member_list();
	});
}

var load_member_list = function() {
	$('#group_manager_and_member').load(
		'.', 
		{'load_manager_and_member_list': null},
		set_link_behavior
	);
}

$(function() {
	load_member_list();
	$('#modify_group_name').hide();
	$('#modify_group_description').hide();

	set_trigger_link(
		'div.group_basic_info a',
		'div.group_basic_info', 
		'div[id^="display"]',
		'div[id^="modify"]'
    	);
	set_cancel_button(
		'div.group_basic_info :button', 
		'div.group_basic_info', 
		'div[id^="modify"]',
		'div[id^="display"]'
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
