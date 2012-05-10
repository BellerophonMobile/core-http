$(document).ready(function() {
    function getSessionList() {
        $.ajax({
            url: '/sessions/',
            dataType: 'json',
            success: function(data) {
                console.log('getSessionList Success:', data);
                $('#sessions').empty();
                session_id = 0;
                if (data.sessions.length > 0) {
                    $.each(data.sessions, function(i) {
                        $('#sessions').append('<option value="' + i + '">' + i + ' - ' + data.sessions[i].name + '</option>');
                    });
                    $('#sessions').removeAttr('disabled');
                } else {
                    $('#sessions').append('<option>No sessions running</option>');
                    $('#sessions').prop('disabled', true);
                }
                getObjectList(session_id)
            },
            error: function(data) {
                console.log('Error:', data);
            },
        });
    }

    function getObjectList(sid) {
        $.ajax({
            url: '/sessions/' + sid + '/objects/',
            dataType: 'json',
            success: function(data) {
                console.log('getObjectList Success:', data);
                $('#objects').empty();
                $.each(data.objects, function(i) {
                    $('#objects').append('<li>' + i + ': ' + data.objects[i].name + ', ' + data.objects[i].type.replace(/</g,'&lt;') + '</li>');
                });
            },
            error: function(data) {
                console.log('Error:', data);
            },
        });
    }

    // need to store this somewhere, should be in a better place
    var session_id;

    $('#new_session').on('submit', function(event) {
        console.log('Submit:', $(this).attr('action'));
        $.ajax({
            url: $(this).attr('action'),
            type: 'POST',
            dataType: 'json',
            data: $(this).serialize(),
            success: function(data) {
                console.log('Post success:', data);
                getSessionList();
            },
            error: function(data) {
                console.log('Post failure:', data);
            }
        });
        return false;
    });

    $('#new_object').on('submit', function(event) {
        console.log('Submit:', $(this).attr('action'));
        $.ajax({
            url: $(this).attr('action'),
            type: 'POST',
            dataType: 'json',
            data: $(this).serialize(),
            success: function(data) {
                console.log('Post success:', data);
                getObjectList(session_id);
            },
            error: function(data) {
                console.log('Post failure:', data);
            }
        });
        return false;
    });

    $('#sessions').on('change', function(event) {
        session_id = event.target.value;
        $('#new_session').attr('action', '/sessions/' + session_id + '/objects/');
    });

    getSessionList();
});
