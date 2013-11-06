var load_user = function() {
	$('#manager_list').load('.', {'load_manager_list': null}, function() {
	});
	$('#member_list').load('.', {'load_member_list': null}, function() {
	});
}

$(function() {
	load_user();
});
