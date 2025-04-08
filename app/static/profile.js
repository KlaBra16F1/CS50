function loadTest(event) {
    test = event.srcElement.value;
    window.location.href = `./make-test?test=${test}`;
};
async function deleteTest(event) {
    test = event.srcElement;
    let req = await fetch("/delete-test?ut_id=" + test.value)
    let res = await req.json()
    if (res['success']) {
        test.parentElement.parentElement.remove();
        Metro.notify.create('Success',res['success'],{ cls: 'success'} );
    } else {
        Metro.notify.create('Success',res['error'],{ cls: 'alert'});
    }
}