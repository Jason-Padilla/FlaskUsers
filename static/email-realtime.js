
$(document).ready(function(){
    $('#email').keyup(function(){
        var data = $("#userForm").serialize()   // capture all the data in the form in the variable data
        $.ajax({
            method: "POST",   // we are using a post request here, but this could also be done with a get
            url: "/users/new/email-realtime",
            data: data
        })
        .done(function(res){
            $('#emailMsg').html(res)  // manipulate the dom when the response comes back
        })
    })
});   