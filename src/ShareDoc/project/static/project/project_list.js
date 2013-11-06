var clear_search_result = function(hide_dom, show_dom) {
	show_dom.find('div.search_result').html("");
}

$(function() {
	$('div.apply_confirm, div.create_project').hide();
	set_trigger_link(
		'#apply_to_project a',
		'#apply_to_project',
		'div.apply_confirm',
		null,
		clear_search_result
	);
	set_cancel_button(
		'#apply_to_project :button',
		'#apply_to_project',
		'div.apply_confirm',
		null
	);
});

$(function() {
	set_create_form('div.create_project form');
	set_trigger_link(
		'#create_project_div a',
		'#create_project_div',
		'div.create_project',
		null	
	);
	set_cancel_button(
		'#create_project_div :button',
		'#create_project_div',
		'div.create_project',
		null	
	);
});

$(function() {
	set_search_form(
		'div.apply_confirm form',
		'div.apply_confirm',
		'p.error',
		'div.search_result'
	);
});
