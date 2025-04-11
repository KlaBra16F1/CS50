let username = document.querySelector('#username');
   
// get username
username.addEventListener('change', async function(){
    let feedback1 = Metro.getPlugin('#username','append');
    let req = await fetch('/register?username=' + username.value);
    let res = '';
    try {
        res = await req.json();
    } catch (SyntaxError) {
        $('#userNameInfo').html('Must be 4-16 characters or numbers. Must not contain whitespaces and special characters.');
    } finally {
        if (res == 'error') {
            $('#userNameAlert').html("<span class='mif-priority_high mif-2x fg-red'></span>");
            $('#userNameInfo').html('<span class="fg-red">Username is already taken</span>');
        } else {
            $('#userNameAlert').html("<span class='mif-more-horiz mif-2x fg-gray'></span>");
            $('#userNameInfo').html('Must be 4-16 characters or numbers. Must not contain whitespaces and special characters.');
        }   
    }
});