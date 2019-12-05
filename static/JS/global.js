$(document).ready(() => {
    $(".modal").draggable({
        handle: ".modal-header"
    });
});
//
$(document).on("click", "#close", () => {
    const ele = document.querySelector(".modal");
    ele.classList.remove("animated", "bounceInDown");
    ele.classList.add("animated", "bounceOutUp");
});
//
$(document).on("click", ".leave-server", function (e) {
    const server_id = $(this).attr("data-serverid");
    const ele = document.querySelector(".modal");
    ele.classList.remove("animated", "bounceOutUp");
    ele.classList.add("animated", "bounceInDown");

    document.getElementById("modal-title").innerHTML = "Are you sure you want to remove the bot?";

    const continue_btn = document.getElementById("btn-continue");
    continue_btn.innerHTML = "Leave Server";
    continue_btn.classList.add("leave-server-btn");
    continue_btn.setAttribute("data-serverid", server_id);
    $("#reason").attr("disabled", true);

    $(".modal").show();
    e.preventDefault();
});
//
$(document).on("click", ".ban-server", function (e) {
    const server_id = $(this).attr("data-serverid");
    const ele = document.querySelector(".modal");
    ele.classList.remove("animated", "bounceOutUp");
    ele.classList.add("animated", "bounceInDown");

    document.getElementById("modal-title").innerHTML = "Are you sure you want to ban this server?";

    const continue_btn = document.getElementById("btn-continue");
    continue_btn.innerHTML = "Ban Server";
    continue_btn.classList.add("ban-server-btn");
    continue_btn.setAttribute("data-serverid", server_id);

    $(".modal").show();
    e.preventDefault();
});
//
$(document).on("click", ".unban-server", function (e) {
    const server_id = $(this).attr("data-serverid");
    const ele = document.querySelector(".modal");
    ele.classList.remove("animated", "bounceOutUp");
    ele.classList.add("animated", "bounceInDown");

    document.getElementById("modal-title").innerHTML = "Are you sure you want to unban this server?";

    const continue_btn = document.getElementById("btn-continue");
    continue_btn.innerHTML = "Unban Server";
    continue_btn.classList.add("unban-server-btn");
    continue_btn.setAttribute("data-serverid", server_id);
    $("#reason").attr("disabled", true);

    $(".modal").show();
    e.preventDefault();
});
//
$(document).on("click", ".leave-server-btn", function (e) {
    const server_id = $(this).attr("data-serverid");
    $("#btn-continue").attr("disabled", true);
    $("#loader").show();
    $.ajax("/api/v1/admin/leaveServer", {
        data: JSON.stringify({server_id}),
        contentType: "application/json",
        type: "POST",
        success: function (data, textStatus, jQxhr) {
            const ele = document.querySelector(".modal");
            ele.classList.remove("animated", "bounceInDown");
            ele.classList.add("animated", "bounceOutUp");
            location.reload();
        }
    });
    e.preventDefault();
});
//
$(document).on("click", ".ban-server-btn", function (e) {
    const server_id = $(this).attr("data-serverid");
    const reason = $(".modal #reason").val();
    $("#btn-continue").attr("disabled", true);
    $("#loader").show();
    $.ajax("/api/v1/admin/banServer", {
        data: JSON.stringify({server_id, reason}),
        contentType: "application/json",
        type: "POST",
        success: function (data, textStatus, jQxhr) {
            location.reload();
        },
        error: function (jqXHR, exception) {
            location.reload()
        }
    });
    e.preventDefault();
});
//
$(document).on("click", ".unban-server-btn", function (e) {
    const server_id = $(this).attr("data-serverid");
    $("#btn-continue").attr("disabled", true);
    $("#loader").show();
    $.ajax("/api/v1/admin/unbanServer", {
        data: JSON.stringify({server_id}),
        contentType: "application/json",
        type: "POST",
        success: function (data, textStatus, jQxhr) {
            location.reload();
        },
        error: function (jqXHR, exception) {
            location.reload()
        }
    });
    e.preventDefault();
});
//
$(document).on("click", ".ban-user", function (e) {
    const user_id = $(this).attr("data-userid");
    const ele = document.querySelector(".modal");
    ele.classList.remove("animated", "bounceOutUp");
    ele.classList.add("animated", "bounceInDown");

    document.getElementById("modal-title").innerHTML = "Are you sure you want to ban this user?";

    const continue_btn = document.getElementById("btn-continue");
    continue_btn.innerHTML = "Ban User";
    continue_btn.classList.add("ban-user-btn");
    continue_btn.setAttribute("data-userid", user_id);

    $(".modal").show();
    e.preventDefault();
});
//
$(document).on("click", ".unban-user", function (e) {
    const user_id = $(this).attr("data-userid");
    const ele = document.querySelector(".modal");
    ele.classList.remove("animated", "bounceOutUp");
    ele.classList.add("animated", "bounceInDown");

    document.getElementById("modal-title").innerHTML = "Are you sure you want to unban this user?";

    const continue_btn = document.getElementById("btn-continue");
    continue_btn.innerHTML = "Unban User";
    continue_btn.classList.add("unban-user-btn");
    continue_btn.setAttribute("data-userid", user_id);
    $("#reason").attr("disabled", true);

    $(".modal").show();
    e.preventDefault();
});
//
$(document).on("click", ".ban-user-btn", function (e) {
    const user_id = $(this).attr("data-userid");
    const reason = $(".modal #reason").val();
    $("#btn-continue").attr("disabled", true);
    $("#loader").show();
    $.ajax("/api/v1/admin/banUser", {
        data: JSON.stringify({user_id, "reason": reason}),
        contentType: "application/json",
        type: "POST",
        success: function (data, textStatus, jQxhr) {
            location.reload();
        },
        error: function (jqXHR, exception) {
            location.reload()
        }
    });
    e.preventDefault();
});
//
$(document).on("click", ".unban-user-btn", function (e) {
    const user_id = $(this).attr("data-userid");
    $("#btn-continue").attr("disabled", true);
    $("#loader").show();
    $.ajax("/api/v1/admin/unbanUser", {
        data: JSON.stringify({user_id}),
        contentType: "application/json",
        type: "POST",
        success: function (data, textStatus, jQxhr) {
            location.reload();
        },
        error: function (jqXHR, exception) {
            location.reload()
        }
    });
    e.preventDefault();
});
//
$(document).ready(function () {
    $(".theme-select").on("click", function (e) {
        $(this).attr("disabled", true);
        const theme_name = $(this).attr("data-name");
        $.ajax("/api/v1/changeTheme", {
            data: JSON.stringify({theme_name}),
            contentType: "application/json",
            type: "POST",
            success: function (data, textStatus, jQxhr) {
                location.reload();
            },
            error: function (jqXHR, exception) {
                location.reload()
            }
        });
        e.preventDefault();
    });

    $("#selectLogChannel").on("change", function (e) {
        $(this).attr("disabled", true);
        $("#loader").show();
        const channel_id = $(this).val();
        const server_id = $("#server-id").attr("data-serverid");
        $.ajax(`/api/v1/${server_id}/updateLogChannel`, {
            data: JSON.stringify({channel_id}),
            contentType: "application/json",
            type: "POST",
            success: function (data, textStatus, jQxhr) {
                location.reload();
            },
            error: function (jqXHR, exception) {
                location.reload()
            }
        });
        e.preventDefault();
    });
});
//
$(document).on("click", ".module-switch", function (e) {
    $(this).attr("disabled", true);
    const server_id = $("#server-id").attr("data-serverid");
    const module = $(this).attr("data-modulename");
    const enabled = !$(this)[0].hasAttribute("checked");
    $.ajax(`/api/v1/${server_id}/toggleModule`, {
        data: JSON.stringify({module, enabled}),
        contentType: "application/json",
        type: "POST",
        success: function (data, textStatus, jQxhr) {
            location.reload();
        },
        error: function (jqXHR, exception) {
            location.reload()
        }
    });
    e.preventDefault();
});
//
$(document).on("click", ".admin-module-switch", function (e) {
    $(this).attr("disabled", true);
    const module = $(this).attr("data-modulename");
    const enabled = !$(this)[0].hasAttribute("checked");
    $.ajax(`/api/v1/admin/toggleModule`, {
        data: JSON.stringify({module, enabled}),
        contentType: "application/json",
        type: "POST",
        success: function (data, textStatus, jQxhr) {
            location.reload();
        },
        error: function (jqXHR, exception) {
            location.reload()
        }
    });
    e.preventDefault();
});
//
$(document).on("click", ".promote-user", function (e) {
    const user_id = $(this).attr("data-userid");
    const ele = document.querySelector(".modal");
    ele.classList.remove("animated", "bounceOutUp");
    ele.classList.add("animated", "bounceInDown");

    document.getElementById("modal-title").innerHTML = "Are you sure you want to promote this user?";

    const continue_btn = document.getElementById("btn-continue");
    continue_btn.innerHTML = "Promote User";
    continue_btn.classList.add("promote-user-btn");
    continue_btn.setAttribute("data-userid", user_id);
    $("#reason").attr("disabled", true);

    $(".modal").show();
    e.preventDefault();
});
//
$(document).on("click", ".demote-user", function (e) {
    const user_id = $(this).attr("data-userid");
    const ele = document.querySelector(".modal");
    ele.classList.remove("animated", "bounceOutUp");
    ele.classList.add("animated", "bounceInDown");

    document.getElementById("modal-title").innerHTML = "Are you sure you want to demote this user?";

    const continue_btn = document.getElementById("btn-continue");
    continue_btn.innerHTML = "Demote User";
    continue_btn.classList.add("demote-user-btn");
    continue_btn.setAttribute("data-userid", user_id);
    $("#reason").attr("disabled", true);

    $(".modal").show();
    e.preventDefault();
});
//
$(document).on("click", ".promote-user-btn", function (e) {
    const user_id = $(this).attr("data-userid");
    $("#btn-continue").attr("disabled", true);
    $("#loader").show();
    $.ajax("/api/v1/admin/promoteUser", {
        data: JSON.stringify({user_id}),
        contentType: "application/json",
        type: "POST",
        success: function (data, textStatus, jQxhr) {
            location.reload();
        },
        error: function (jqXHR, exception) {
            location.reload()
        }
    });
    e.preventDefault();
});
//
$(document).on("click", ".demote-user-btn", function (e) {
    const user_id = $(this).attr("data-userid");
    $("#btn-continue").attr("disabled", true);
    $("#loader").show();
    $.ajax("/api/v1/admin/demoteUser", {
        data: JSON.stringify({user_id}),
        contentType: "application/json",
        type: "POST",
        success: function (data, textStatus, jQxhr) {
            location.reload();
        },
        error: function (jqXHR, exception) {
            location.reload()
        }
    });
    e.preventDefault();
});
//
$(document).on("click", ".event-switch", function (e) {
    $(this).attr("disabled", true);
    const server_id = $("#server-id").attr("data-serverid");
    const event = $(this).attr("data-eventname");
    const enabled = !$(this)[0].hasAttribute("checked");
    $.ajax(`/api/v1/${server_id}/toggleEvent`, {
        data: JSON.stringify({event, enabled}),
        contentType: "application/json",
        type: "POST",
        success: function (data, textStatus, jQxhr) {
            location.reload();
        },
        error: function (jqXHR, exception) {
            //location.reload()
        }
    });
    e.preventDefault();
});
//