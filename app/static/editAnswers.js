// Scripts for 'edit-answers.html' and 'answers.html'
document.addEventListener('DOMContentLoaded', function () {
  getAnswers()
})
// AJAX -> 'answers.html'
function getAnswers () {
  let q_id = document.querySelector('#q_id').value
  var req = new XMLHttpRequest()
  req.onreadystatechange = function () {
    if (req.readyState == 4 && req.status == 200) {
      document.querySelector('#answers').innerHTML = req.responseText
    }
  }
  req.open('GET', '/get-answers?q_id=' + q_id, true)
  req.send()
  edited = undefined
}
// Switch to Edit-Mode
function updateAnswer (id) {
  // Prevent multiple edits
  if (typeof edited !== 'undefined') {
    Metro.notify.create(
      'Error',
      'You can only edit one answer at a time. Press ENTER to submit first.',
      { cls: 'alert' }
    )
    return
  }
  edited = true // Will be undefined in getAnswers()

  let form = document.getElementById(`a${id}`)
  let fields = form.getElementsByTagName('div')
  let button = document.getElementById(`b${id}`)

  const f = []
  for (let i = 0; i < 3; i++) {
    if (fields[i].innerHTML == '') {
      fields[i].appendChild(document.createElement('p'))
    }
    f[i] = fields[i]
  }
  let selected0 = ''
  let selectet1 = ''
  if (f[1].children[0].value == 1) {
    selectet1 = 'selected'
  } else {
    selected0 = 'selected'
  }
  // Using 'single quotes' in html to escape quotes in answers/comments
  fields[0].innerHTML = `<input type='text' autocomplete='off' class='input-small' name='answer' data-role='input' value='${f[0].children[0].innerHTML}'>
  <small class='text-light'>Your Markdown tags are displayed as HTML. Leave as is or change back to Markdown. Unsafe tags will be removed or may lead to unwanted results.</small>`
  fields[1].innerHTML = `<select data-role="select" class="input-small" name="is_true"><option value=1 ${selectet1}>True</option><option value=0 ${selected0}>False</option></select>`
  fields[2].innerHTML = `<input type='text' name='comment' autocomplete='off' class='input-small' data-role='input' value='${f[2].children[0].innerHTML}'>`
  button.innerHTML = `<button id="" class="button success mt-4" type="submit">Update</button>
    <button type="button" class="button mt-4" onclick="getAnswers();">Abort</button>`
}
// Send Form changes to server
async function sendUpdate (a_id, event) {
  let q_id = document.querySelector('#q_id').value
  let answer = event.srcElement[1].value
  let is_true = event.srcElement[3].value
  let comment = event.srcElement[7].value
  let req = await fetch(
    '/edit-answers?update_answer=' +
      a_id +
      '&answer=' +
      answer +
      '&is_true=' +
      is_true +
      '&comment=' +
      comment +
      '&q_id=' +
      q_id
  )
  let res = await req.json()
  if (res['success']) {
    Metro.notify.create('Success', res['success'], { cls: 'success' })
  } else {
    Metro.notify.create('Error', res['error'], { cls: 'alert' })
  }
  getAnswers()
}
// Script for new answers form
async function add_answer () {
  let q_id = document.getElementById('add_q_id').value
  let answer = document.getElementById('answer').value
  let is_true = document.getElementById('is_true').value
  let comment = document.getElementById('comment').value
  let req = await fetch(
    '/add-answers?q_id=' +
      q_id +
      '&answer=' +
      answer +
      '&is_true=' +
      is_true +
      '&comment=' +
      comment
  )
  let res = await req.json()
  if (res['success']) {
    Metro.notify.create('Success', res['success'], { cls: 'success' })
  } else {
    Metro.notify.create('Error', res['error'], { cls: 'alert' })
  }
  getAnswers()
}
// Script for deleting answers
async function deleteAnswer (event) {
  let q_id = document.querySelector('#q_id').value
  let req = await fetch(
    '/edit-answers?delete=' + event.srcElement.value + '&q-id=' + q_id
  )
  let res = await req.json()
  if (res['success']) {
    Metro.notify.create('Success', res['success'], { cls: 'success' })
  } else {
    Metro.notify.create('Error', res['error'], { cls: 'alert' })
  }
  getAnswers()
}
