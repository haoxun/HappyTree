var copy_text = function(display, modify) {
	var display_content = display.children('span').text();
	modify.find('p.error').text("");
	modify.find('input[type="text"]').val(display_content);
}
var set_trigger_link = function(link_dom_str, common_ancestor, show_dom_str, hide_dom_str, callback) {
	callback = typeof a !== 'undefined' ? callback : copy_text; 
	$(link_dom_str).click(function(event) {
		event.preventDefault();
		var display = $(this).parents(common_ancestor).children(show_dom_str);
		var modify = $(this).parents(common_ancestor).children(hide_dom_str);

		callback(display, modify);

		display.fadeOut('fast');
		modify.slideDown('fast');
	});
}

var set_cancel_button = function(button_dom_str, common_ancestor, hide_dom_str, show_dom_str) {
	$(button_dom_str).click(function(event) {
		event.preventDefault();
		$(this).parents(common_ancestor).children(hide_dom_str).slideUp('fast');
		$(this).parents(common_ancestor).children(show_dom_str).fadeIn('fast');
	});
}

var get_post_str = function() {
	var form = $(this);
	var post_str = form.serialize();
	var submit_name = form.find('input[type="submit"]').attr('name');
	post_str += ('&' + submit_name + '=');
	return post_str;
};

var set_basic_info_form = function(form_dom_str) {
	$(form_dom_str).submit(function(event) {
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
}

var set_search_form = function(form_dom_str) {
	$(form_dom_str).submit(function(event) {
		event.preventDefault();
		post_str = get_post_str.call(this);
		var form = $(this);
		$.post('.', post_str, function(json_data) {
			if(json_data.error) {
				error_msg = "";
				$.each(json_data.error, function(index, value) {
					error_msg += index + ":" + value;
				});
				form.parent().children('p.error').text(error_msg);
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
}
