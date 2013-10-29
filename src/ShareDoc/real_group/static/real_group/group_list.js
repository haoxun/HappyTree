$(function() {
	$('#apply_to_group > div').hide()
	$('#creat_group > div').hide()

	$("#apply_to_group a, #creat_group a").click(function(event) {
		event.preventDefault();
		$(this).parent().children('div').slideDown('fast');
		$(this).parent().find('input[type="text"]').val("");
		$(this).fadeOut('fast');
	});
	$("#apply_to_group :button, #creat_group :button").click(function(event) {
		$(this).parent().parent().fadeOut('fast');
		$(this).parent().parent().parent().children('a').slideDown('fast');
	});
	
});

$(function() {
	var get_post_str = function() {
		var form = $(this);
		var post_str = form.serialize();
		var submit_name = form.find('input[type="submit"]').attr('name');
		post_str += ('&' + submit_name + '=');
		return post_str;
	};
	$('#apply_to_group form').submit(function(event) {
		event.preventDefault();
		var post_str = get_post_str.call(this);
		form = $(this);
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
						entry_html += "Attend";
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
	$('#creat_group form').submit(function(event) {
		event.preventDefault();
		var post_str = get_post_str.call(this);
		form = $(this);
		$.post('.', post_str, function(json_data) {
			if(json_data.error) {
				form.parent().children('p.error').text(json_data.error);
			}
			else {
				window.location.href = json_data.url;
			}
		});

	});


});
