// Hide the form to beginwith
$('#bizplace_form').hide();
$('#tariff_container').hide();
$('#location_view_form').hide();
var locations_title = $('#content-title').text();

function show_editform(id) {
    function success(resp) {
        loc = resp['result'];
        $('input[name="name"]').val(loc.name);
        $('textarea[name="address"]').val(loc.address);
        $('#country option:contains("' +loc.country+ '")').attr('selected','selected');
        $('#tz option:contains("' +loc.tz+ '")').attr('selected','selected');
        $('textarea[name="short_description"]').val(loc.short_description);
        $('input[name="city"]').val(loc.city);
        $('input[name="province"]').val(loc.province);
        $('input[name="email"]').val(loc.email);
        $('#currency').val(loc.currency);
        $('#website').val(loc.website);
        $('input[name="email"]').val(loc.email);
        $('input[name="host_email"]').val(loc.host_email);
        $('input[name="booking_email"]').val(loc.booking_email);
        $('input[name="phone"]').val(loc.phone);
        $('input[name="fax"]').val(loc.fax);
        $('#location_view_form').hide();
        $('#my_loc_list').hide();
        $('#all_loc_list').hide();
        $('#bizplace_form').show();
    };
    function error() {
        alert('Error getting location info');
    };
    var params = {'bizplace_id': id};
    jsonrpc('bizplace.info', params, success, error);
}

function show_mylocations() {
    window.location = basepath + '/bizplaces/'
}

function show_all_locations() {
    $('#bizplace_form').hide();
    $('#all_loc_list').show();
    $('#content-title').text(locations_title);
}

$('#bizplace_form #cancel-btn').click(function() {
    history.back();
});

$('#list-locations-link').click(function(){
    window.location = basepath + '/bizplaces/';
    window.location.reload();
});

$('#all-list-locations-link').click(function(){
    window.location = basepath + '/bizplaces#all-locations';
    window.location.reload();
});

function show_tariff() {
    set_context(parseInt(this.id.split('-')[1], 10));
    window.location = basepath + '/tariffs';
}

function show_tariff_details() {
    var params = {};
    var resource_map =  {}
    function resource_success(resp) {
        var guest_tariff = null;

        function set_guest_tariff(tariff_data) {
            for(var index in tariff_data) {
                if (tariff_data[index]['is_guest_tariff'] == 1) {
                    guest_tariff = tariff_data[index];
                    break;
                }
            }
        }

        function pricing_success(resp) {
            set_guest_tariff(resp['result']);

            resp['result'].forEach(function(rec) {
                var display_data = [];
                var tempObj = {};
                tempObj['name'] = rec['name'];
                tempObj['curr_price'] = guest_tariff['pricings'][rec['id']]['amount']
                tempObj['prices'] = [];
                tempObj['currency'] = locale_data.currency_symbol;
                for (var res in resource_map) {
                    var amount = '-';
                    if (res in rec['pricings']) {
                        amount = rec['pricings'][res]['amount'];
                    }
                    tempObj['prices'].push(amount);
                };
                display_data.push(tempObj);
                $('#tariff_col_tmpl').tmpl(display_data).appendTo('#tariff-box');
            });
        }

        function pricing_error() {
            alert('Error getting pricing');
        }

        $('#all_loc_list').hide();
        $('#location_tabs').hide();
        $('#tariff_container').show();
        var newparams = {};
        resp['result'].forEach(function(item) {
            resource_map[item['id']] = item['name'];
        });
        $('#resource_tmpl').tmpl(resp['result']).appendTo('#resource_column');
        newparams['owner'] = location_id;
        jsonrpc('pricings.by_location', newparams, pricing_success, pricing_error);
    }
    function resource_error() {
        alert('Error getting resources');
    }
    var tariff_info = this.id.split('-');
    var location_id = parseInt(tariff_info[1], 10);
    params['owner'] = location_id;
    $('#content-title').text(tariff_info[2]);
    jsonrpc('resource.list', params, resource_success, resource_error);
}

function show_team() {
    set_context(parseInt(this.id.split('-')[1], 10));
    window.location = basepath + '/team';
}

function edit_location(theform) {
    var inputs = theform.serializeArray();
    var action_status = $('#bizplace_form .action-status');
    var params = {'bizplace_id': loc.id}
    for(var i in inputs){
        params[inputs[i].name] = inputs[i].value;
    }
    function success() {
        action_status.text("Location updated successfully").attr('class', 'status-success');
        setTimeout(function(){
            window.location = basepath + '/bizplaces/'
        }, 1000);
    };
    function error() {
        action_status.text("Error in updating location").attr('class', 'status-fail');
    };
    jsonrpc('bizplace.update', params, success, error);
};

$('#bizplace_form').submit(function () {
    var theform = $(this);
    theform.checkValidity();
    edit_location(theform);
    return false;
});

function location_info(resp) {
    loc = resp['result'];

    // Not all fields from result are show on UI, so we get some error
    // for (var attr in loc) {
    //     $('input[name="location_'+ attr + 'name"]').val(loc.attr);    
    // }

    // for (var attrib in ['name', 'address', 'city', 'email', 'short_description', 'country']) {
    //     $('#location_view_form #location_'+attrib).text(loc.name);
    // }

    // TODO : Populate only appropriate view/form based on which tab is
    // selected

    selected_tab = $('#location_tabs').tabs('option', 'selected');

    $('#location_tabs').hide();
    $('#content-title').text(loc.name);
    $('#location_view_form #name').text(loc.name);
    $('#location_view_form #currency').text(loc.currency);
    $('#location_view_form #website').text(loc.website);
    $('#location_view_form #address').text(loc.address);
    $('#location_view_form #city').text(loc.city);
    $('#location_view_form #email').text(loc.email);
    $('#location_view_form #short_description').text(loc.short_description);
    $('#location_view_form #province').text(loc.province);
    $('#location_view_form #country').text(loc.country);
    $('#location_view_form #tz').text(loc.tz);
    $('#location_view_form #phone').text(loc.phone);
    $('#location_view_form #fax').text(loc.fax);
    $('#location_view_form #host_email').text(loc.host_email);
    $('#location_view_form #booking_email').text(loc.booking_email);
    // Originally, href for edit link was set only if selected tab was 0
    // See additional details in else block
    $('#edit-location-link').attr('href',basepath+'/bizplaces/#/'+loc.id+'/edit');
    if (selected_tab == 0) {  // My Location
        // $('#edit-location-link').attr('href',basepath+'/bizplaces/#/'+loc.id+'/edit');
        $('#my_loc_list').hide();
        $('#bizplace_form').hide();
    } else {
        // Edit link was hidden because current user may not have permission 
        // to edit ANY location.
        // This aspect will be dealt later when roles/permissions are addressed
        // uniformly thru-out the application. Till then allow edit
        // unconditionally

        // $('#edit-location-link').hide();
        $('#all_loc_list').hide();
    }
    $('#location_view_form').show();
}

function bizplace_info_error() {
    alert('Error in bizplace.info')
}

function act_on_route(id) {
    var params = {'bizplace_id': id};
    jsonrpc('bizplace.info', params, location_info, bizplace_info_error);
};

function setup_routing () {
    var routes = {
        '/:id': {
            '/edit': show_editform,
            on: act_on_route
        },
    };

    Router(routes).configure({ recurse: 'forward' }).init();
};

setup_routing();

$(document).ready(function() {
    $('#location_tabs').tabs({
        collapsible:false
    });
    load_my_locations();
    load_all_locations();
});

function load_my_locations() {
    function success(resp) {
        $('#my_loc_tmpl').tmpl(resp['result']).appendTo('#my_loc_list');
        $('.myloc_tariff-btn').click(show_tariff);
        $('.myloc_team-btn').click(show_team);
    };

    function error() {
        alert('Error getting my locations');
    };

    var params = {};
    // TODO : Update role_filter when additional roles like accountant are added
    params = {'user_id': current_userid, 'role_filter':['director','host']};
    if(params['user_id']) {
        jsonrpc('roles.list', params, success, error); 
    };

};

function load_all_locations() {
    function success(resp) {
        $('#all_loc_tmpl').tmpl(resp['result']).appendTo('#all_loc_list');
        $('.loc_tariff-btn').click(show_tariff_details);
    };

    function error() {
        alert('Error getting all locations');
    };

    var params = {};
    jsonrpc('bizplace.all', params, success, error);
};
