function getAnswers() {
    let q_id = document.querySelector('#q_id').value;
    console.log(q_id);
    var req = new XMLHttpRequest();
    req.onreadystatechange = function() {
        if (req.readyState == 4 && req.status == 200) {
            document.querySelector('#answers').innerHTML = req.responseText;
        }
    };
    req.open('GET', '/get-answers?q_id='+ q_id, true);
    req.send();
    edited = undefined;
};

document.addEventListener('DOMContentLoaded', function() {
    getAnswers();
});

function updateAnswer(id) {
    if (typeof(edited) !== 'undefined') {
        Metro.notify.create('Error','You can only edit one answer at a time. Press ENTER to submit first.',{ cls: 'alert'})
        return
    }
    edited = true;
    console.log(id)
    let form = document.getElementById(`a${id}`);
    let fields = form.getElementsByTagName('div');
    let button = document.getElementById(`b${id}`);

    // if (fields[2].innerHTML == '') {
    //     fields[2].appendChild(document.createElement("p"));
    // }
    const f = [];
    for (let i = 0; i < 3; i++) {
        if (fields[i].innerHTML == ''){
            fields[i].appendChild(document.createElement("p"))
        }
        f[i] = fields[i];
    }
    let selected0 = '';
    let selectet1 = '';
    if (f[1].children[0].value == 1) {
        
        selectet1 = 'selected';
    } else {
        selected0 = 'selected';
    }
    fields[0].innerHTML = `<input type="text" class="input-small" name="answer" data-role="input" value="${f[0].children[0].innerHTML}">`;
    fields[1].innerHTML = `<select data-role="select" class="input-small" name="is_true"><option value=1 ${selectet1}>True</option><option value=0 ${selected0}>False</option></select>`
    fields[2].innerHTML = `<input type="text" name="comment" class="input-small" data-role="input" value="${f[2].children[0].innerHTML}">`;
    button.innerHTML = `<button id="" class="button success mt-4" type="submit">Update</button>
    <button type="button" class="button mt-4" onclick="getAnswers();">Abort</button>`

};
async function sendUpdate(a_id, event) {
    let q_id = document.querySelector('#q_id').value;
    console.log(q_id);
    let answer = event.srcElement[1].value
    let is_true = event.srcElement[3].value
    let comment = event.srcElement[7].value
    let req = await fetch('/edit-answers?update_answer=' + a_id + '&answer=' + answer + 
        '&is_true=' + is_true + '&comment=' + comment + '&q-id=' + q_id);
    let res = await req.json();
    console.log(res);
    if (res["success"]) {
        Metro.notify.create('Success',res["success"],{ cls: 'success'});
    } else {
        Metro.notify.create('Error',res["error"],{ cls: 'alert'});
    }
    getAnswers();
};
async function add_answer() {
    let q_id = document.getElementById('add_q_id').value;
    let answer = document.getElementById('answer').value;
    let is_true = document.getElementById('is_true').value;
    let comment = document.getElementById('comment').value;
    let req = await fetch('/add-answers?q_id=' + q_id + '&answer=' 
    + answer + '&is_true=' + is_true + '&comment=' + comment);
    let res = await req.json();
    if (res["success"]) {
        Metro.notify.create('Success',res["success"],{ cls: 'success'});
    } else {
        Metro.notify.create('Error',res["error"],{ cls: 'alert'});
    }
    getAnswers();
};
async function deleteAnswer(event) {
    let q_id = document.querySelector('#q_id').value;
    let req = await fetch("/edit-answers?delete=" + event.srcElement.value + '&q-id=' + q_id);
    let res = await req.json();
    console.log(res);
    if (res["success"]) {
        Metro.notify.create('Success',res["success"],{ cls: 'success'});
    } else {
        Metro.notify.create('Error',res["error"],{ cls: 'alert'});
    }
    getAnswers();
};