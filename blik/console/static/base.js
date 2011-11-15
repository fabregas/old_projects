function process_menu_item(item, skip_li) {
    var items = [];

    if (skip_li == 0) {
        items.push('<li id="' + item.sid + '">');
    }
    items.push('<a href="' + item.url + '">' + item.label + '</a>');

    if (item.children && item.children.length > 0) {
        $.each(item.children, function(i,subitem) {
           var subitems = process_menu_item(subitem, 1); 
           items.push('<span>');
           items = items.concat(subitems);
           items.push('</span>');
        });
    }
    if (skip_li == 0) {
        items.push('</li>');
    }

    return items
}


function make_menu_script() {

	$("ul#topnav li").hover(function() {
        $(this).find("span").css('z-index', 100);
		$(this).css({ 'background' : '#8f987d url(/static/topnav_active.gif) repeat-x'});
		$(this).find("span").show();
	} , function() { //on hover out...
		$(this).css({ 'background' : 'none'});
		$(this).find("span").hide();
	});

}

function load_menu() {
    $.getJSON('/get_menu_items', function(data) {
        var menu_html = "";

        $.each(data, function(i, item) {
            var items = process_menu_item(item, 0);
            menu_html = menu_html + items.join('');
        });

        $('<ul/>', {
            'id': 'topnav',
            html: menu_html
        }).appendTo('#menu');
    
        make_menu_script();
    });
}

function fix_console_height() { 
    var min_height = 500;
    var b_h = $("#base_content").height();
    var screen_height = $(window).height() - 120;

    if (b_h < screen_height) b_h = screen_height;
    if (b_h < min_height) b_h = min_height;
    $("#base_content").height(b_h);
}

function calc_height(element_id) {
    var h = $('#base_content').offset().top + $('#base_content').height() - $(element_id).offset().top ;

    return h;
}

function fix_columns_width(element_id) {
    var tbl_width = $('#container').width();
    tbl_width = tbl_width*95/100;

    $.each($(element_id+' th'), function(index, item) {
        if (item.width.substr(-1) == "%") {
            item.width = parseFloat(item.width.substr(0,item.width.length-1)) * tbl_width/100;
        }
    });
}

function get_col_pw(perc) {
    var tbl_width = $('#container').width();
    tbl_width = tbl_width*95/100;

    return perc*tbl_width/100;
}

$(document).ready(function(){
    fix_console_height();
});

$(window).load(function() {
        $('table[auto_height]').each(function(i, item) {
            var table = $(item).parentsUntil('.flexigrid');
            var h = calc_height(table);
            if ($(item).attr('has_pager') == '') {
                h = h-30;
            }
            table.height(h);
        });
});

