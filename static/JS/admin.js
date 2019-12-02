$(document).on('click', '.leave-server-btn', function (e) {
    const server_id = $(this).attr('data-serverid');
    $.ajax("/api/v1/admin/leaveServer", {
        data: JSON.stringify({server_id}),
        contentType: "application/json",
        type: "POST",
        success: function (data, textStatus, jQxhr) {
            location.reload();
        }
    });
    e.preventDefault();
});

$(document).on('click', '.ban-server-btn', function (e) {
    const server_id = $(this).attr('data-serverid');
    $.ajax("/api/v1/admin/banServer", {
        data: JSON.stringify({server_id}),
        contentType: "application/json",
        type: "POST",
        success: function (data, textStatus, jQxhr) {
            location.reload();
        }
    });
    e.preventDefault();
});
$(document).on('click', '.ban-user-btn', function (e) {
    const user_id = $(this).attr('data-userid');
    $.ajax("/api/v1/admin/banUser", {
        data: JSON.stringify({user_id}),
        contentType: "application/json",
        type: "POST",
        success: function (data, textStatus, jQxhr) {
            location.reload();
        },
    });
    e.preventDefault();
});
$(document).on('click', '.unban-user-btn', function (e) {
    const user_id = $(this).attr('data-userid');
    $.ajax("/api/v1/admin/unbanUser", {
        data: JSON.stringify({user_id}),
        contentType: "application/json",
        type: "POST",
        success: function (data, textStatus, jQxhr) {
            location.reload();
        },
    });
    e.preventDefault();
});
$(document).on('click', '.unban-server-btn', function (e) {
    const server_id = $(this).attr('data-serverid');
    $.ajax("/api/v1/admin/unbanServer", {
        data: JSON.stringify({server_id}),
        contentType: "application/json",
        type: "POST",
        success: function (data, textStatus, jQxhr) {
            location.reload();
        },
    });
    e.preventDefault();
});