//***************************** Global Section ***********************************
var picture = null;
var resource_list = {};
var state = 0;
var checked_map = {'checked':true, 'on':true, undefined:false};
var states = {'enabled':1, 'host_only':2, 'repairs':4};
var image_size_limit = 256000;//256kb
var res_id = null;
var this_resource = null;
var this_res_pricing = null;
//xxxxxxxxxxxxxxxxxxxxxxxxxxx End Global Section xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

// Routing

function setup_routing () {
    var routes = {
        '/:id': {
            '/edit/profile' : get_resource,
            '/edit/pricing' : get_pricing,
            on: act_on_route
        },
    };
    Router(routes).configure({ recurse: 'forward' }).init();
};

function act_on_route(id) {
    res_id = id;
    this_resource_id = id;
    view_resource_tabs();
    $('.tab').each( function () {
        var href = $(this).attr('href');
        var new_href = href.replace('ID', id);
        $(this).attr('href', new_href);
    });
    $('.tab[href="'+window.location.hash+'"]').addClass('tab-selected');
};

// Tabs

$('.tab').click( function () {
    $('.tab').removeClass('tab-selected');
    $(this).addClass('tab-selected');
});


function view_resource_tabs() {
    $('.tab-container').show();
    $('#list-container').hide();
    $('.tab-content').hide();
};

function view_resource_list() {
    $('.tab-container').hide();
    $('#list-container').show();
    window.location.hash = '';
};

//****************************List Resource*************************************

function on_resource_data(resource) {
    resource.flag  = resource.state.enabled?1:0;
    resource.flag |= resource.state.host_only?2:0;
    resource.flag |= resource.state.repairs?4:0;
    resource_list[resource.id] = resource;
    if(!resource.time_based) {
        $("#clock_"+resource.id).hide();
    };
};

function on_list_resources(resp) {
    var result = resp.result;
    $('#resource-tmpl').tmpl(result).appendTo('#resource_list');
    for(i in result) {
        on_resource_data(result[i]);
    };
    view_resource_list();
};

if (window.location.hash == '') {
    function error(){};
    jsonrpc('resource.list', {'owner':current_ctx}, on_list_resources, error);
};

function load_resource(resp) {
    on_resource_data(resp.result);
    resource_editing();
};

function get_resource(id) {
    if ((this_resource == null) || (this_resource.id != id)) {
        function error(resp) {};
        jsonrpc('resource.info', {'res_id':id}, load_resource, error);
    } else { resource_editing(); };
};

//xxxxxxxxxxxxxxxxxxxxxxxxxxxEnd List Resourcexxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

//***************************Upload Resource Picture****************************
$('#picture').change(function handleFileSelect(evt) {
    var files = evt.target.files;
    var reader = new FileReader();
    reader.onload = (function(e) {
        picture = e.target.result;
    });
    if(files.length == 1){
        if(files[0].size <= image_size_limit)
            reader.readAsDataURL(files[0]);
        else
            alert("Image size exceeds image upload limit, Image size must be less than "+ (image_size_limit/1000) + "kb.");
    }
});
//xxxxxxxxxxxxxxxxxxxxxxxxxEnd Upload Invoice Picturexxxxxxxxxxxxxxxxxxxxxxxxxxx

//*****************************On Resource Type Click***************************
function show_resource(){
    $(this).attr('class', 'resource_type-show');
    var type = ($(this).val()).toLowerCase();
    $('.typed_resource-hidden').each(function(){
        res_id = parseInt($(this).attr('id').split('_')[1]);
        if(resource_list[res_id]['type'] == type){
            $(this).removeClass("typed_resource-hidden");
            $(this).addClass("typed_resource-visible");
        }
        if($(this).hasClass('typed_resource-visible') && $(this).hasClass('filtered_resource-visible')){
            $(this).removeClass("resource-hidden");
            $(this).addClass("resource-visible");
        }
        else{
            $(this).addClass("resource-hidden");
            $(this).removeClass("resource-visible");
        }
    });
    $('.resource_type-show').click(hide_resource);
};

function hide_resource(){
    $(this).attr('class', 'resource_type-hide');
    type = ($(this).val()).toLowerCase();
    $('.typed_resource-visible').each(function(){
        res_id = parseInt($(this).attr('id').split('_')[1]);
        if(resource_list[res_id]['type'] == type){
            $(this).addClass("typed_resource-hidden");
            $(this).removeClass("typed_resource-visible");
            $(this).addClass("resource-hidden");
            $(this).removeClass("resource-visible");
        }
    });
    $('.resource_type-hide').click(show_resource);
};

$('.resource_type-hide').click(show_resource);
$('.resource_type-show').click(hide_resource);
//xxxxxxxxxxxxxxxxxxxxxxxxxxxxEnd On Resource Type Clickxxxxxxxxxxxxxxxxxxxxxxxx

//***************************On Resource Filter Click***************************
function show_filtered_resources(){
    state |= states[$(this).attr('id')];
    $('.filtered_resource-visible').each(function(){
        res_id = parseInt($(this).attr('id').split('_')[1]);
        if((resource_list[res_id].flag & state) != state){
            $(this).removeClass("filtered_resource-visible");
            $(this).addClass("filtered_resource-hidden");
            $(this).removeClass("resource-visible");
            $(this).addClass("resource-hidden");
        }
    });
    $(this).unbind('click');
    $(this).attr('class', 'resource_filter-show');
    $(this).click(hide_filtered_resources);
};

function hide_filtered_resources(){
    state ^= states[$(this).attr('id')];
    $('.filtered_resource-hidden').each(function(){
        res_id = parseInt($(this).attr('id').split('_')[1]);
        if((resource_list[res_id].flag & state) == state){
            $(this).addClass("filtered_resource-visible");
            $(this).removeClass("filtered_resource-hidden");
        }
        if($(this).hasClass('typed_resource-visible') && $(this).hasClass('filtered_resource-visible')){
            $(this).removeClass("resource-hidden");
            $(this).addClass("resource-visible");
        }
        else{
            $(this).addClass("resource-hidden");
            $(this).removeClass("resource-visible");
        }
    });
    $(this).unbind('click');
    $(this).attr('class', 'resource_filter-hide');
    $(this).click(show_filtered_resources);
};

$('.resource_filter-hide').click(show_filtered_resources);
$('.resource_filter-show').click(hide_filtered_resources);
//xxxxxxxxxxxxxxxxxxxxxxxxxxEnd On Resource Filter Clickxxxxxxxxxxxxxxxxxxxxxxxx

//*******************************Edit Resource**********************************
$("#resource_edit_form #update_resource-btn").click(function(){
    var params = {'res_id': res_id};
    function success(resp) {
        resource_list[res_id]['name'] = params['name'];
        $("#edit_"+params['res_id']).text(params['name']);
        resource_list[res_id]['type'] = params['type'];
        resource_list[res_id]['short_description'] = params['short_description'];
        $("#short_description_"+params['res_id']).text(params['short_description']);
        resource_list[res_id].state = params.state
        resource_list[res_id]['long_description'] = params['long_description'];
        resource_list[res_id].flag = resource_list[res_id].state['enabled']?1:0;
        resource_list[res_id].flag |= resource_list[res_id].state['host_only']?2:0;
        resource_list[res_id].flag |= resource_list[res_id].state['repairs']?4:0;
        resource_list[res_id]['time_based'] = params['time_based'];
        if(picture){
            resource_list[res_id]['picture'] = picture;
            $("#picture_"+res_id).show();
            $("#picture_"+res_id).attr('src', picture);
        }
        if(resource_list[res_id]['time_based'])
            $("#clock_"+res_id).show();
        else
            $("#clock_"+res_id).hide();
        if((resource_list[res_id].flag & state) != state){
            $("#resource_"+res_id).removeClass("filtered_resource-visible");
            $("#resource_"+res_id).addClass("filtered_resource-hidden");
        }
        if(!$("#rtype_"+resource_list[res_id]['type']).hasClass('resource_type-show')){
            $("#resource_"+res_id).removeClass("typed_resource-visible");
            $("#resource_"+res_id).addClass("typed_resource-hidden");
        }
        if(!$("#resource_"+res_id).hasClass('typed_resource-visible') || !$("#resource_"+res_id).hasClass('filtered_resource-visible')){
            $("#resource_"+res_id).addClass("resource-hidden");
            $("#resource_"+res_id).removeClass("resource-visible");
        }
        $("#resource_list").show();
        $("#resource_filters").show();
        $("#resource_types").show();
        picture = null;
        view_resource_list();
    };
    function error() {
        $("#edit_resource-msg").text("Error in Updating Resource").addClass('status-fail');
    };
    params['name'] = $("#name").val();
    params['type'] = $("#type").val();
    params['short_description'] = $("#short_desc").val();
    params['long_description'] = $("#long_desc").val();
    params['time_based'] = checked_map[$("#time_based:checked").val()];
    params.state = {};
    params.state['enabled'] = checked_map[$("#state_enabled:checked").val()];
    params.state['host_only'] = checked_map[$("#state_host_only:checked").val()];
    params.state['repairs'] = checked_map[$("#state_repairs:checked").val()];
    if(picture)
        params['picture'] = picture;
    jsonrpc('resource.update', params, success, error); 
});

$("#resource_edit_form #cancel-btn").click( view_resource_list );

function resource_editing() {
    this_resource = resource_list[res_id];
    var name = this_resource.name;
    $('#res-profile-content').show();
    $("#content-title").text(name);
    $("#name").val(name);
    $("#type option[value='" + this_resource.type + "']").attr('selected', 'selected');
    $("#short_desc").val(this_resource.short_description);
    $("#long_desc").val(this_resource.long_description);
    $("#time_based").attr('checked', this_resource.time_based);
    $("#state_enabled").attr('checked', this_resource.state.enabled);
    $("#state_host_only").attr('checked', this_resource.state.host_only);
    $("#state_repairs").attr('checked', this_resource.state.repairs);
};

function on_resource_pricings(resp) {
    this_res_pricing = resp.result;
    $('#price-tmpl').tmpl(this_res_pricing).appendTo('#current-prices');
    $('#res-pricing-content').show();
};

function on_tariff_list(resp)  {
    $('#tariff-option-tmpl').tmpl(resp.result).appendTo('#tariff-select');
};

function on_tariff_pricings(resp) {
    $('#new-pricing').slideDown();
    $('#old-pricings').empty();
    $('#old-pricing-tmpl').tmpl(resp.result).appendTo('#old-pricings');
    $('.pricing-date').each( function() {
        $(this).text(to_formatted_date($(this).text()));
    });
};

function error(resp) {
    alert('error fetching pricings: ' + resp.error.message);
};

function get_pricing(id) {
    if (this_res_pricing == null) {
        var params = {'resource_id': id};
        jsonrpc('pricings.by_resource', params, on_resource_pricings, error);
        var params = {'owner': current_ctx};
        jsonrpc('tariffs.list', params, on_tariff_list, error);
    } else {
        $('#res-pricing-content').show();
    };
};

function load_tariff_pricings() {
    var params = {'resource_id': this_resource_id, 'tariff_id': $('#tariff-select').val()};
    jsonrpc('pricings.list', params, on_tariff_pricings, error);
};

$('#tariff-select').change( load_tariff_pricings );

$('#new-starts-vis').datepicker( {
    altFormat: 'yy-mm-dd',
    altField: '#new-starts',
    dateFormat: 'M d, yy'
});

function add_new_pricing() {
    var params = {'resource_id': this_resource_id, 'tariff_id': $('#tariff-select').val(), 'starts': $('#new-starts').val(), 
        'amount': $('#new-amount').val()};
    function error(resp) {
        alert('error adding new pricings: ' + resp.error.message);
    };
    function success () {};
    jsonrpc("pricings.new", params, load_tariff_pricings, error);
};

$('#new-pricing').submit(function () {
    $(this).checkValidity();
    add_new_pricing();
    return false;
});

setup_routing();
