
$(document).ready(function(){
    m_h = $("#menu").height();
    b_h = $("#base_content").height();
    
    max_h = m_h;
    if (m_h < b_h) max_h = b_h;

    if (max_h < 500) max_h = 500;

    $("#menu").height(max_h);
    $("#base_content").height(max_h);

});

