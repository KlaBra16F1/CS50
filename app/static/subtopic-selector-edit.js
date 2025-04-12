// Scripts for 'edit-questions.html'
var subtopics_loaded
let topic = document.querySelector('#topic')
topic.addEventListener('change', async function () {
  subtopics_loaded = false
  let res = await fetch('/get-subtopics?t_id=' + topic.value)
  document.querySelector('#subtopic').innerHTML = ''
  let subtopics = await res.json()
  let html = '<option value="">Please Select</option>'
  for (s of subtopics) {
    html +=
      '<option value="' +
      s.s_id +
      '">' +
      s.subtopic +
      ' (' +
      s.count +
      ')</option>'
  }
  document.querySelector('#subtopic').innerHTML = html
  subtopics_loaded = true
})
// DELETE SCRIPTS
async function deleteTopicSubtopic () {
  let topic = document.querySelector('#topic')
  let subtopic = document.querySelector('#subtopic')
  if (subtopic.value == '' && topic.value == '') {
    return
  }
  let del = ''
  let = target = ''
  if (!subtopic.value) {
    del = topic.value
    target = 't_id'
  } else {
    del = subtopic.value
    target = 's_id'
  }
  console.log(target, del)
  let req = await fetch(
    '/edit-questions?delTopicSubtopic=' + target + '&id=' + del
  )
  let res = await req.json()

  if (target == 't_id') {
    topic.selectedIndex = 0
  } else {
    res['topics'] = 0
  }

  subtopic.selectedIndex = 0
  topic.dispatchEvent(new Event('change', { bubbles: true }))
  Metro.notify.create(
    'Success',
    `Deleted:<br>${res['topics']} Topics<br>${res['subtopics']} Subtopics<br> 
            ${res['questions']} Questions<br>${res['answers']} Answers<br>
            ${res['user_stats']} User-Statistics`,
    { cls: 'success' }
  )

  if (target == 't_id') {
    window.location.href = './edit-questions'
  }
}
