// 로딩창
window.onload = function() {
    setTimeout(function() {
        document.getElementById('loading-screen').style.display = 'none';
        document.getElementById('content').style.display = 'block';
    }, 1000);
}