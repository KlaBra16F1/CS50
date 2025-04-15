// Script of 'results.html'
// Fill Scorebar with values from page
document.addEventListener('DOMContentLoaded', function() {
  let questions = document.querySelector('#questionCount').value
  let rightAnswers = document.querySelector('#rightCount').value
  let percent = document.querySelector('#percent')
  let info = document.querySelector('#info')
  let score = (rightAnswers / questions) * 100
  percent.innerHTML = `${score.toFixed(2)} %`
  let controller = Metro.getPlugin('#score', 'progress')
  controller.val(score)
  info.innerHTML = `You mastered ${rightAnswers} out of ${questions} questions.`
})
// Save test to user-profile and prevent multiple saves
async function saveTest() {
  if (typeof sentTest !== 'undefined') {
      Metro.notify.create('Error', 'You already saved this test.', {
          cls: 'alert'
      })
      return
  }
  sentTest = true
  let u_id = document.getElementById('u_id')
  let testName = document.querySelector('#test-name')
  let req = await fetch(
      '/save-test?save=' + u_id.value + '&name=' + testName.value
  )
  let res = await req.json()
  if (res['success']) {
      Metro.notify.create('Success', res['success'], {
          cls: 'success'
      })
  } else {
      Metro.notify.create('Error', res['error'], {
          cls: 'alert'
      })
  }
}
