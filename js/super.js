const REFRESH_PAGE = 60000

$(document).ready(function() {
    if (window.tvMode === true) {
        $('nav').hide();
        $('form').hide();
    } else {
        $('nav').show();
        $('form').show();
    }
    $('#url').val($(location).attr('href'));
    $('.url_note').val($(location).attr('href'));
    $(document).on('click', '.del_note', function(e) {
        if (!confirm("This note will be deleted. Are you sure?")) {
            e.preventDefault();
        }
    });

    $(document).ready(function(){
        $('[data-toggle="tooltip"]').tooltip();
    });

    function checkHealth() {
        fetch('/healthcheck')
            .then(response => {
                if (response.ok) {
                    window.location.reload();
                } else {
                    throw new Error('Server responded with an error!');
                }
            })
            .catch(error => {
                $('#health-status').removeClass('badge-success').addClass('badge-danger').text('Super is DOWN');
            });
    }

    setInterval(checkHealth, REFRESH_PAGE);
});
