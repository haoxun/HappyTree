$(function() {
	$('#modify_group_name').hide();
	$('#modify_group_description').hide();

	$('div.group_basic_info a').click(function(event) {
		event.preventDefault();
		var display = $(this).parent();
		var modify = $(this).parent().parent().children('div[id^="modify_group"]');
		var display_content = display.children('span').text();
		modify.find('p.error').text("");
		modify.find('input[type="text"]').val(display_content);
		display.fadeOut('fast');
		modify.slideDown('fast');

	});
	$('div.group_basic_info form :button').click(function(event) {
		event.preventDefault();
		$(this).parent().parent().fadeOut('fast');
		var display = $(this).parent().parent().parent().children('div[id^="display_group"]');
		display.slideDown('fast');

	});

});

//$(function() {
//	$('div.member_list a').click(function(event) {
//		event.preventDefault();
//		$.get($(this).attr('href'), function(data) {
//			console.log(data);
//		});
//		$(this).parent().fadeOut('fast');
//	});
//});

$(function() {
	var get_post_str = function() {
		var form = $(this);
		var post_str = form.serialize();
		var submit_name = form.find('input[type="submit"]').attr('name');
		post_str += ('&' + submit_name + '=');
		return post_str;
	};
	$('div.group_basic_info form').submit(function(event) {
		event.preventDefault();
		post_str = get_post_str.call(this);
		form = $(this);
		$.post('.', post_str, function(json_data) {
			if(json_data.error) {
				error_msg = "";
				$.each(json_data.data, function(index, value) {
					error_msg += index + ":" + value;
				});
				form.parent().children('p.error').text(error_msg);
			}
			else {
				$.each(json_data.data, function(index, value) {
					form.parent().parent().find('span').text(value);
				});
				form.find(':button').click();

			}
		});
	});
	$('div.apply_confirm form').submit(function(event) {
		event.preventDefault();
		post_str = get_post_str.call(this);
		var form = $(this);
		$.post('.', post_str, function(json_data) {
			if(json_data.error) {
				form.parent().children('p.error').text(json_data.error);	
			}
			else {
				var search_result = form.parent().children('div.search_result');
				var html = "";
				if($.isEmptyObject(json_data.data)) {
					html = "<p>Can't Find Anything</p>";
				}
				else {
					$.each(json_data.data, function(index, value) {
						entry_html = "<p>";
					       	entry_html += index;
					       	entry_html += '<a href="' + value + '">';
						entry_html += "Add";
						entry_html += "</a>";
						entry_html += "</p>";
						html += entry_html;
					});
				}
				search_result.html(html);
				search_result.find('a').click(function(event) {
					event.preventDefault();
					var add_item = $(this).parent();
					$.get($(this).attr('href'), function(data) {
						add_item.fadeOut('fast');
					});
					
				});
			}
		});

	});
});
		
