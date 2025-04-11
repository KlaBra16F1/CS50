document.addEventListener('DOMContentLoaded', function(){
    let form = document.querySelector('#make-test');
    let subtopic = document.querySelector("#subtopic");
    let sub = Metro.getPlugin(subtopic, 'select');
    let = val = '';
    subtopic.addEventListener('change', function() {
        val = '[' + sub.val().toString() + ']';
    });
    form.addEventListener('submit', function() {
        let opt = document.createElement('option');
        opt.value = val;
        subtopic.appendChild(opt)
        subtopic.value = val;
    });

});