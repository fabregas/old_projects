

function get_checked_radio(table_name) {
    var i, radio;
    var inputs = document.getElementById(table_name).getElementsByTagName('input')
    for (i=0; i<inputs.length; ++i) {
        if ((inputs[i].getAttribute('type') == 'radio') && (inputs[i].checked==true)) {
            radio = inputs[i]
            break
        }
    }
    return radio;
}

function modify_node() {
    var radio = get_checked_radio('nodes_table')

    if (radio) {
        document.location.href = "/cluster/modnode_"+ radio.getAttribute('id')
    } else {
        alert('Select node for it modify!')
    }
}

function remove_node() {
    var radio = get_checked_radio('nodes_table')

    if (radio) {
            var agree = confirm("Do you really want delete node: "+  radio.getAttribute('nname') +"?")
            if (agree) {
                document.location.href = "/cluster/remnode_" + radio.getAttribute('id')
            }
    } else {
        alert('Select node for delete it!')
    }

}


function modify_cluster() {
    var radio = get_checked_radio('clusters_table')

    if (radio) {
        document.location.href = "/cluster/modcluster/" + radio.getAttribute('id')
    } else {
        alert('Select cluster for it modify!');
    }
}

function remove_cluster() {
    var radio = get_checked_radio('clusters_table')

    if (radio) {
            var agree = confirm("Do you really want delete cluster "+  radio.getAttribute('nname') +"?")
            if (agree) {
                document.location.href = "/cluster/remcluster/" + radio.getAttribute('id')
            }
    } else {
        alert('Select cluster for delete it!')
    }

}

function onClusterSelected() {
    var select = document.getElementsByTagName('select')[0]
    var i, val

    for (i=0; i < select.options.length; i++) {
        if (select.options[i].selected) {
            val = select.options[i].value
            break
        }
    }
    
    document.location.href = "/applications/" + val
}



function askWindow(message, link) {
    var agree = confirm(message)

    if (agree) {
        document.location.href = link
    }
}

function undeploy_selected() {
    var radio = get_checked_radio('old_app_table')

    if (radio) {
        var agree = confirm("Do you really want undeploy this version? ")
        if (agree) {
            document.location.href = "/undeploy_application/" + radio.getAttribute('id')
        }
    } else {
        alert('Select application version for undeploying!');
    }
}

function activate_selected() {
    var radio = get_checked_radio('old_app_table')

    if (radio) {
        var agree = confirm("Do you really want activate this version? ")
        if (agree) {
            document.location.href = "/activate_application/" + radio.getAttribute('id')
        }
    } else {
        alert('Select application version for activating!');
    }
}

function selectedAppFile() {
    var i, val
    var inputs = document.getElementById('deploy_table').getElementsByTagName('input')
    for (i=0; i<inputs.length; ++i) {
        if (inputs[i].getAttribute('type') == 'file') {
            val = inputs[i].value
            break
        }
    }
    
    val = val.split('\\').reverse()[0];
    val = val.replace('.zip','')
    var i = val.search('_')
    if (i < 0)
        return;

    document.getElementById('appName').setAttribute('value', val.substr(0,i));
    document.getElementById('appVersion').setAttribute('value', val.substr(i+1));
}

function preSubmitDeploy() {
    var i, val
    var inputs = document.getElementById('deploy_table').getElementsByTagName('input')
    for (i=0; i<inputs.length; ++i) {
        if (inputs[i].getAttribute('type') == 'file') {
            val = inputs[i].value
            break
        }
    }
    if (val == "")
        return;

    val = document.getElementById('appName').getAttribute('value');
    if (val == "")
        return;

    val = document.getElementById('appVersion').getAttribute('value');
    if (val == "")
        return;
    
    val = document.getElementById('deploy_form').submit();
}

function preSubmitNewUser() {
    var i,val, pwd1, pwd2
    var inputs = document.getElementById('create_user_table').getElementsByTagName('input')
    for (i=0; i<inputs.length; ++i) {
        if (inputs[i].value == '') {
            alert("Please, put user name, password and retype password!")
            return
        }
        if (inputs[i].name == 'userPassword') {
            pwd1 = inputs[i].value
            continue
        }
        if (inputs[i].name == 'userPassword2') {
            pwd2 = inputs[i].value
            continue
        }
    }

    if (pwd1 != pwd2) {
        alert("Passwords is mismatch!")
        return
    }
    val = document.getElementById('create_user_form').submit();
}



function preSubmitModUser() {
    var i,val, pwd1, pwd2
    var inputs = document.getElementById('modify_password_table').getElementsByTagName('input')
    for (i=0; i<inputs.length; ++i) {
        if (inputs[i].value == '') {
            alert("Please, put passwords into text fields!")
            return
        }
        if (inputs[i].name == 'newPassword') {
            pwd1 = inputs[i].value
            continue
        }
        if (inputs[i].name == 'newPassword2') {
            pwd2 = inputs[i].value
            continue
        }
    }

    if (pwd1 != pwd2) {
        alert("Passwords is mismatch!")
        return
    }
    val = document.getElementById('modify_password_form').submit();

}



function moveRoleToUser() {
    var i, val, role_name
    var select = document.getElementById('all_roles')

    for (i=0; i < select.options.length; i++) {
        if (select.options[i].selected) {
            val = select.options[i].value
            role_name = select.options[i].innerHTML
            break
        }
    }
    if (val == undefined) {
        return
    }

    var user_roles = document.getElementById('hidden_inputs').getElementsByTagName('input')
    for (i=0; i<user_roles.length; ++i) {
        if (user_roles[i].getAttribute('value') == val) {
            return;
        }
    }

    var newItem = document.createElement('input')
    newItem.setAttribute('type', 'hidden')
    newItem.setAttribute('name', 'role_'+val)
    newItem.setAttribute('value', val)
    document.getElementById('hidden_inputs').appendChild(newItem)

    newItem = document.createElement('option')
    newItem.setAttribute('value', val)
    newItem.appendChild(document.createTextNode(role_name))
    document.getElementById('user_roles').appendChild(newItem)

}


function moveRoleFromUser() {
    var i, val, element, hidden_element
    var select = document.getElementById('user_roles')

    for (i=0; i < select.options.length; i++) {
        if (select.options[i].selected) {
            val = select.options[i].value
            element = select.options[i]
            break
        }
    }
    if (val == undefined) {
        return
    }

    var user_roles = document.getElementById('hidden_inputs').getElementsByTagName('input')
    for (i=0; i<user_roles.length; ++i) {
        if (user_roles[i].getAttribute('value') == val) {
            hidden_element = user_roles[i]
        }
    }
 
    document.getElementById('hidden_inputs').removeChild(hidden_element)
    document.getElementById('user_roles').removeChild(element)
}


function loadStates(url, id_prefix) {
    getrequest = new window.XMLHttpRequest()
    getrequest.onreadystatechange = function() {
        if (getrequest.readyState==4) {
            var json = getrequest.responseText
            var results = eval("("+json+")")

            for (item in results) {
                var e = document.getElementById(id_prefix + item)
                if (results[item]) {
                    e.setAttribute('src','/static/up.png')   
                } else {
                    e.setAttribute('src','/static/down.png')   
                }
            }
        }
    }
    getrequest.open("GET", url, true)
    getrequest.send(null)
}

function loadNodesStates(cluster_id) {
    loadStates("/get_nodes_states/"+cluster_id, "imgNode")
}

function loadApplicationState(app_id) {
    loadStates("/get_application_state/"+app_id, "imgApp")
}
