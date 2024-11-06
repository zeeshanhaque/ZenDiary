function changeImage(imgId, state, filename) {
    var img = document.getElementById(imgId);
    if (state === 'hover') {
        img.src = "/static/assets/" + filename + "-hover.png";
    } else {
        img.src = "/static/assets/" + filename + ".png";
    }
}