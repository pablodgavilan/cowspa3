//****************************Global Section************************************
var invoice_pref_info, invoice_email_text;
var changed_values = {};
var image_size_limit = 128000;//128kb
//xxxxxxxxxxxxxxxxxxxxxxxxxxEnd Global Sectionxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
$("#invoicepref_tabs").tabs({
    collapsible:false,
});
$("#edit-link").click(function(){
    $("#view-section").hide();
    $("#edit-section").show();
});

$("#cancel-btn").click(function(){
    $("#edit-section").hide();
    $("#invoice_email_text").val(invoice_email_text);
    $("#payment_terms").val(invoice_pref_info.payment_terms);
    $("#due_date").val(invoice_pref_info.due_date);
    $("#bank_details").val(invoice_pref_info.bank_details);
    $("#bcc_invoice").val(invoice_pref_info.bcc_email);
    $("#freetext1").val(invoice_pref_info.freetext1);
    $("#freetext2").val(invoice_pref_info.freetext2);
    changed_values = {}; 
    $('#edit_invoicepref-msg').html("");
    $("#view-section").show();
});

//**********************Update Invoice Preference Info**************************
$("#save-btn").click(function(){
    var params = {'owner':current_ctx};
    for(var key in changed_values){
        if(changed_values[key]==invoice_pref_info[key]){
            delete(changed_values[key])
        }
    }    
    function success() {
        if('logo' in changed_values){
            $("#data-logo").attr('src', changed_values.logo);
            invoice_pref_info.logo = changed_values.logo;
            delete(changed_values.logo);
        }
        for(key in changed_values){
            $("#data-"+key).text(changed_values[key]);
            invoice_pref_info[key] = changed_values[key];
        }
        changed_values = {};
        $('#edit_invoicepref-msg').html("");
        $("#edit-section").hide();
        $("#view-section").show();
    };
    function error(){
        $('#edit_invoicepref-msg').html("<big>Error in Updating Invoice Preferences. Try again</big>");
    };
    if($.isEmptyObject(changed_values) == false){    
        changed_values.owner = current_ctx; 
        jsonrpc('invoicepref.update', changed_values, success, error);
    }
    else{
        $('#edit_invoicepref-msg').html("");
        $("#edit-section").hide();
        $("#view-section").show();
    }
});
//xxxxxxxxxxxxxxxxxxxxxEnd Update Invoice Preference Infoxxxxxxxxxxxxxxxxxxxxxxx

//***************************Upload Invoice Logo********************************
$('#logo').change(function handleFileSelect(evt) {
    var files = evt.target.files;
    var reader = new FileReader();
    reader.onload = (function(e) {
        changed_values.logo = e.target.result;
    });
    if(files.length == 1){
        if(files[0].size <= image_size_limit)
            reader.readAsDataURL(files[0]);
        else
            alert("Image size exceeds image upload limit, Image size must be less than "+ (image_size_limit/1000) + "kb.");
    }
});
//xxxxxxxxxxxxxxxxxxxxxxxxxEnd Upload Invoice Logoxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

//*************************Get Invoice Preference Info**************************
function success(response) {
    invoice_pref_info = response.result;
    if (invoice_pref_info.logo=='data:') {
        $("#data-logo").hide();
    } else {
        $("#data-logo").attr('src', invoice_pref_info.logo);
    };
    $("#data-payment_terms").text(invoice_pref_info.payment_terms); 
    $("#payment_terms").val(invoice_pref_info.payment_terms);
    $("#data-due_date").text(invoice_pref_info.due_date); 
    $("#due_date").val(invoice_pref_info.due_date);
    $("#data-bank_details").text(invoice_pref_info.bank_details); 
    $("#bank_details").val(invoice_pref_info.bank_details);
    $("#data-bcc_email").text(invoice_pref_info.bcc_email); 
    $("#bcc_email").val(invoice_pref_info.bcc_email);
    $("#data-freetext1").text(invoice_pref_info.freetext1);
    $("#freetext1").val(invoice_pref_info.freetext1);
    $("#data-freetext2").text(invoice_pref_info.freetext2);
    $("#freetext2").val(invoice_pref_info.freetext2);    
};
var params = { 'owner' : current_ctx};
jsonrpc('invoicepref.info', params, success);
//xxxxxxxxxxxxxxxxxxxxxxxxEnd Get Invoice Preference Infoxxxxxxxxxxxxxxxxxxxxxxx

//***********************Changed Input Field Value******************************
$('.changed-data').change(function(){ 
    changed_values[$(this).attr('id')] = $(this).val(); 
});
//xxxxxxxxxxxxxxxxxxxxxxxxEnd Changed Input Field Valuexxxxxxxxxxxxxxxxxxxxxxxxx
//****************************Email Text Section********************************
$("#edit-link2").click(function(){
    $('#edit-section2 .action-status').text("").removeClass("status-fail");
    $("#view-section2").hide();
    $("#edit-section2").show();
});
$("#cancel-btn2").click(function(){
    $("#data-email_text").val(invoice_email_text);
    $("#edit-section2").hide();
    $("#view-section2").show();
});
$("#save-btn2").click(function(){
    invoice_email_text = $("#invoice-email_text").val();
    var params = {owner_id: current_ctx, name: "invoice", content: invoice_email_text};
    function on_save_emailtext_success() {
        $("#data-email_text").text(invoice_email_text);
        $("#edit-section2").hide();
        $("#view-section2").show();
    };
    function on_save_emailtext_error(){
        $('#edit-section2 .action-status').text("Error in Updating Invoice Preferences. Try again").addClass("status-fail");
    };
    jsonrpc('messagecust.update', params, on_save_emailtext_success, on_save_emailtext_error);
});

function on_get_emailtext_success(response) {
    invoice_email_text = response.result; 
    $("#data-email_text").text(invoice_email_text);
    $("#invoice-email_text").val(invoice_email_text);
};
var params1 = { 'owner_id' : current_ctx, 'name':"invoice"};
jsonrpc('messagecust.get', params1, on_get_emailtext_success);
