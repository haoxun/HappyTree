var clear_search_result = function(hide_dom, show_dom) {
	show_dom.find('div.search_result').html("");
}

$(function() {
	$('div.apply_confirm, div.create_group').hide();
	set_trigger_link(
		'#apply_to_group a',
		'#apply_to_group',
		'div.apply_confirm',
		null,
		clear_search_result
	);
	set_cancel_button(
		'#apply_to_group :button',
		'#apply_to_group',
		'div.apply_confirm',
		null
	);
});

$(function() {
	set_create_form('div.create_group form');
	set_trigger_link(
		'#create_group_div a',
		'#create_group_div',
		'div.create_group',
		null	
	);
	set_cancel_button(
		'#create_group_div :button',
		'#create_group_div',
		'div.create_group',
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
