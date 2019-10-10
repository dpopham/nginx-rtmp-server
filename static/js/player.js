const player = videojs('#player');
function changeVideo() {
    var e = document.getElementById("videoStreamsDropdown");
    var videoUrl = e.options[e.selectedIndex].value;
    $( "#currently-playing" ).html("<h3>Now Playing: " + e.options[e.selectedIndex].text + "</h3>");
    if (videoUrl != -1) {
        player.reset();
        player.controls(true);
        player.src({
                src: videoUrl,
                type: 'application/vnd.apple.mpegurl'
        });
        player.play();
    } else {
        player.pause();
        player.reset();
        player.controls(false);
    }
}
function loadStreams() {
    $.getJSON( "/streams", function( data ) {
        var s = '<option value="-1">Please Select a Video Stream</option>';
        for (var i = 0; i < data.length; i++) {
            s += '<option value="' + data[i].url + '">' + data[i].name + '</option>';
        }
        $("#videoStreamsDropdown").html(s);
    });
};
function logout() {
    window.location.replace("/logout");
}
function login() {
    window.location.replace("/login");
}
player.reset();
player.controls(false);
loadStreams();

