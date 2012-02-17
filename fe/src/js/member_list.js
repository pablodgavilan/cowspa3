function on_get_member_list_success(response) {
	$('#member_table').dataTable({
		"sDom": '<"H"lT>rt<"F"ip>',
		"oTableTools": {
		    "sSwfPath": "/swf/copy_cvs_xls_pdf"
		},
		"aaData": response.result,
        "bJQueryUI": true,
        "bDestroy": true,
        "sPaginationType": "full_numbers",
        "aaSorting": [[ 0, "asc" ]],
        "aoColumns": [
                { "sTitle": "Name", "sWidth": "25%" },
                { "sTitle": "Membership No", "sWidth": "25%"},
                { "sTitle": "Membership", "sWidth": "25%" },
                { "sTitle": "Email", "sWidth": "25%",
                    "fnRender": function(obj) {
                        var email = obj.aData[obj.iDataColumn];
                        return "<A href='mailto:"+email+"'>"+email+"</A>";
                        }
                }
                ]
	});
};
jsonrpc('memberships.list_by_bizplace', {bizplace_id: current_ctx, hashrows: false}, on_get_member_list_success);
