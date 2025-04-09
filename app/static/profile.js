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
};

function getDetails(t_id){
    let topic = document.querySelector(`#t${t_id}`)
    let details = document.querySelector('#details') 
    var req = new XMLHttpRequest();
    req.onreadystatechange = function() {
        if (req.readyState == 4 && req.status == 200) {
            document.querySelector('#subtopics').innerHTML = req.responseText;
            details.innerHTML = `Details for topic '${topic.innerHTML}'`
        }
    };
    req.open('GET', '/profile?t_id='+ t_id, true);
    req.send();
};