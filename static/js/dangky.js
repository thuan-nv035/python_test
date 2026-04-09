
const username = document.getElementById("username").value
const password = document.getElementById("password").value

function resgister() {
    fetch('/dangky', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json' // Dòng này cực kỳ quan trọng!
    },
    body: JSON.stringify({
        username: username,
        password: password
    })
})
}