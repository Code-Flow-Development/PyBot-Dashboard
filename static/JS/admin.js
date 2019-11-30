$(document).ready(() => {
    $("#leave").on('click', (e) => {
        const guild_id = $(this).attr('data-guildid');
        $.post("http://185.230.160.118:5001/api/admin/leaveServer", {guild_id}, () => {
            alert("Sent")
        });
        e.preventDefault()
    });
});