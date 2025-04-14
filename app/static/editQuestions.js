// Scripts of 'edit-questions.html' and 'questions.html'
let selector = document.querySelector('#topic-selector')
selector.addEventListener('change', function () {
  getQuestions()
})
// AJAX -> 'questions.html'
function getQuestions () {
  let t_id = document.querySelector('#topic').value
  let s_id = document.querySelector('#subtopic').value
  if (subtopics_loaded == false) {
    s_id = ''
  }
  var req = new XMLHttpRequest()
  req.onreadystatechange = function () {
    if (req.readyState == 4 && req.status == 200) {
      document.querySelector('#table').innerHTML = req.responseText
    }
  }
  req.open('GET', '/get-questions?t_id=' + t_id + '&s_id=' + s_id, true)
  req.send()
  editable = undefined
}
// Delete
async function deleteQuestion (event) {
  let del = event.currentTarget.value
  let req = await fetch('/edit-questions?delete=' + del)
  let res = await req.json()
  if (res['success']) {
    Metro.notify.create('Success', res['success'], { cls: 'success' })
  } else {
    Metro.notify.create('Error', res['error'], { cls: 'alert' })
  }
  getQuestions()
}
// Send updated for to server
async function sendUpdate (q_id, event) {
  let question = event.srcElement[0].value
  let multiple = event.srcElement[2].value
  event.preventDefault()
  let req = await fetch(
    '/edit-questions?update=' +
      q_id +
      '&question=' +
      question +
      '&multiple=' +
      multiple
  )
  let res = await req.json()
  if (res['success']) {
    Metro.notify.create('Success', res['success'], { cls: 'success' })
  } else {
    Metro.notify.create('Error', res['error'], { cls: 'alert' })
  }
  getQuestions()
  editable = undefined
}
// Switch to Edit-Mode
function update (id) {
  // prevent multiple call for update
  if (typeof editable !== 'undefined') {
    Metro.notify.create(
      'Error',
      'You can only edit one question at a time. Press ENTER to submit first.',
      { cls: 'alert' }
    )
    return
  }
  editable = true
  // Setting delay of 500 ms to compensate for lag in table-search
  setTimeout(function () {
    let tr = document.querySelector(`#q${id}`).parentElement.parentElement
    let td = tr.getElementsByTagName('td')

    if (td[4].querySelector('p') == undefined) {
      td[4].querySelector('div').appendChild(document.createElement('p'))
    }
    let question = td[4].querySelector('p').innerHTML
    console.log(question)
    let multiple = td[5].querySelector('input').value
    // Make pre-selection based on previous entry
    let selected0 = ''
    let selectet1 = ''
    if (multiple == 1) {
      selectet1 = 'selected'
    } else {
      selected0 = 'selected'
    }
    // Using 'single quotes' in html to escape quotes in questions
    let html = `
        <td>${td[2].innerHTML}</td>
        <td>${td[3].innerHTML}</td>
        <td colspan='2'>
            <form onsubmit='sendUpdate(${id}, event);return false;'>

                <label>Question</label>
                <input name='question' value='${question}' type='text' data-role='input' >
                <small class='text-light'>Your Markdown tags are displayed as HTML. Leave as is or change back to Markdown. Unsafe tags will be removed or may lead to unwanted results.</small>
                <br><label>Multiple Choice</label>
                <select name='multiple' class='input-small w-25' data-filter='false'>
                    <option value=0 ${selected0}>No</option>
                    <option value=1 ${selectet1}>Yes</option>
                </select>
            <br><button class='button success mt-5'>Update</button>
            <button type='button' class='button mt-5' onclick='getQuestions();'>Abort</button>

            </form>
        </td>
        <td>${td[6].innerHTML}</td>`
    tr.innerHTML = html
  }, 500)
}
