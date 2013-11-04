var set_link_behavior = function(callback) {
	$(this).find('a').click(function(event) {
		event.preventDefault();
		var url = $(this).attr('href');
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

var load_perm = function() {
	$('#project_default_perm').load('.', {'load_default_perm': null}, function() {
		set_link_behavior.call(this, load_perm);
	});
}

$(function() {
	load_user();
	load_perm();
});

$(function() {
	$('#modify_project_name').hide();
	$('#modify_project_description').hide();

	set_trigger_link(
		'div.project_basic_info a',
		'div.project_basic_info',
		'div[id^="display"]',
		'div[id^="modify"]'
    	);
	set_cancel_button(
		'div.project_basic_info :button',
		'div.project_basic_info',
		'div[id^="modify"]',
		'div[id^="display"]'
    	);
});

$(function() {
	set_basic_info_form('div.project_basic_info form');
	set_search_form('div.apply_confirm form');
});

$(function() {
	$('div[id^="display_project"] a').hide();
	$('div[id^="display_project"]').hover(
		function() {
			$(this).children('a').fadeIn('fast');
		},
		function() {
			$(this).children('a').fadeOut('fast');
		}
	);
});
