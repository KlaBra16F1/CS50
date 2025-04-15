// Password confirm match?
let password = document.querySelector('#password')
let confirm = document.querySelector('#confirm')
confirm.addEventListener('change', async function() {
    let pw = document.querySelector('#password').value
    if (confirm.value != pw) {
        console.log('cp')
        $('#confirmInfo').html(
            '<span class="fg-red">Passwords do not match!</span>'
        )
    } else {
        $('#confirmInfo').html('&nbsp;')
    }
})