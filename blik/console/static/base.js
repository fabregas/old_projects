function process_menu_item(item) {
    var items = [];

    items.push('<li id="' + item.id + '">');
    items.push('<a href="' + item.url + '">' + item.label + '</a>');
    if (item.subitems && item.subitems.length > 0) {
        $.each(item.subitems, function(i,subitem) {
           var subitems = process_menu_item(subitem); 
           items.push('<ul class="subnav">');
           items = items.concat(subitems);
           items.push('</ul>');
        });
    }
    items.push('</li>');

    return items
}


function make_menu() {
        $("ul.subnav").parent().append("<span></span>"); //Only shows drop down trigger when js is enabled (Adds empty span tag after ul.subnav*)

	    $("ul.topnav li span").click(function() { //When trigger is clicked...

		    //Following events are applied to the subnav itself (moving subnav up and down)
		    $(this).parent().find("ul.subnav").slideDown('fast').show(); //Drop down the subnav on click

		    $(this).parent().hover(function() {
		        }, function(){
			        $(this).parent().find("ul.subnav").slideUp('slow'); //When the mouse hovers out of the subnav, move it back up
		        });

		    //Following events are applied to the trigger (Hover events for the trigger)
		}).hover(function() {
			$(this).addClass("subhover"); //On hover over, add class "subhover"
		    }, function(){	//On Hover Out
			    $(this).removeClass("subhover"); //On hover out, remove class "subhover"
	        });
}

function load_menu() {
    $.getJSON('get_menu_items', function(data) {
        var menu_html = "";

        $.each(data, function(i, item) {
            var items = process_menu_item(item);
            menu_html = menu_html + items.join('');
        });

        $('<ul/>', {
            'class': 'topnav',
            html: menu_html
        }).appendTo('#menu');
    
        make_menu();

    });
}

function fix_console_height() { 
    b_h = $("#base_content").height();
    screen_height = $('body').height() - 100;

    if (b_h < screen_height) b_h = screen_height;
    $("#base_content").height(b_h);
}

$(document).ready(function(){
    load_menu();
    fix_console_height();
});

