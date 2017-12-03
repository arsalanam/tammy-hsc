// custom javascript




	function Edit(elm){
		localStorage.setItem('editId',$(elm).attr('data-id'));
		$.ajax({
			url : '/getGenerated',
			data : {id:$(elm).attr('data-id')},
			type : 'POST',
			success: function(res){

				var data = JSON.parse(res);

				console.log(res);
                $('#idweek').val( data[0]['week'] );
                $('#idyear').val(data[0]['year']);

                 $('#idfile').val( data[0]['file_name']);

                // Trigger the Pop Up
                $('#editModal').modal();



			},
			error: function(error){
				console.log(error);
			}
		});
	}



$('#btnUpdate').click(function() {
    $.ajax({
        url: '/sendmail',
        data: {
            recipients: $('#id_recipients').val(),
            message: $('#id_message').val(),
            week: $('#idweek').val(),
            year: $('#idyear').val(),
            file_name: $('#idfile').val(),
        },
        type: 'POST',
        success: function(res) {
            $('#editModal').modal('hide');
            // Re populate the grid
        },
        error: function(error) {
            console.log(error);
        }
    })
});

$(function() {
    // Since there's no list-group/tab integration in Bootstrap
    $('.list-group-item').on('click',function(e){
     	  var previous = $(this).closest(".list-group").children(".active");
     	  previous.removeClass('active'); // previous list-item
     	  $(e.target).addClass('active'); // activated list-item
   	});
});


