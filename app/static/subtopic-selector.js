// Generic Topic-Selector script
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
