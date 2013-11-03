$(function() {
	hide_dom('#apply_to_group > div, #creat_group > div');
	set_trigger_link("#apply_to_group a, #creat_group a");
	set_cancel_buttom("#apply_to_group :button, #creat_group :button");
});

$(function() {
	set_search_form('#apply_to_group form');
	set_create_form('#creat_group form');
});
