$(function() {
	$('#login form').submit(function(event) {
		event.preventDefault();
		var email = $('#email input').val();
		var password = $('#password input').val();
		var next = $(this).find('input[type="hidden"]').val();
		hex_md5_password = hex_md5(password);
		var post_data = {
			'email': email,
			'password': hex_md5_password,
			'next': next
		};
		$.post('.', post_data, function(data) {
			window.location.replace(data);
		});
	});
});
