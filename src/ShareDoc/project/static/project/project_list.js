$(function() {
	hide_dom('#apply_to_project > div, #creat_project > div');
	set_trigger_link("#apply_to_project a, #creat_project a");
	set_cancel_button("#apply_to_project :button, #creat_project :button");
});

$(function() {
	set_search_form('#apply_to_project form');
	set_create_form('#creat_project form');
});
