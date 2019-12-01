$(document).on('click', '.leave-server-btn', function (e) {
    const server_id = $(this).attr('data-serverid');
    $.post("/api/v1/admin/leaveServer", {server_id}, () => {
        alert("Sent")
    });
    e.preventDefault()
});

$(document).on('click', '.ban-server-btn', function (e) {
    const server_id = $(this).attr('data-serverid');
    $.post("/api/v1/admin/banServer", {server_id}, () => {
        alert("Sent")
    });
    e.preventDefault()
});
$(document).on('click', '.ban-user-btn', function (e) {
    const user_id = $(this).attr('data-userid');
    $.ajax("/api/v1/admin/banUser", {
        data: JSON.stringify({user_id}),
        contentType: "application/json",
        type: "POST",
        success: function (data, textStatus, jQxhr) {
            new Noty({
                type: "success",
                text: data,
                theme: "bootstrap-v4",
                timeout: 3000
            }).show();
            location.reload();
        },
        error: function (jqXhr, textStatus, errorThrown) {
            new Noty({
                type: "error",
                text: errorThrown,
                theme: "bootstrap-v4",
                timeout: 3000
            }).show()
        }
    });
    e.preventDefault()
});
$(document).on('click', '.unban-user-btn', function (e) {
    const user_id = $(this).attr('data-userid');
    $.ajax("/api/v1/admin/unbanUser", {
        data: JSON.stringify({user_id}),
        contentType: "application/json",
        type: "POST",
        success: function (data, textStatus, jQxhr) {
            new Noty({
                type: "success",
                text: data,
                theme: "bootstrap-v4",
                timeout: 3000
            }).show();
            location.reload();
        },
        error: function (jqXhr, textStatus, errorThrown) {
            new Noty({
                type: "error",
                text: errorThrown,
                theme: "bootstrap-v4",
                timeout: 3000
            }).show()
        }
    });
    e.preventDefault()
});
$(document).on('click', '.unban-server-btn', function (e) {
    const server_id = $(this).attr('data-serverid');
    $.post("/api/v1/admin/unbanServer", {server_id}, () => {
        alert("Sent")
    });
    e.preventDefault()
});