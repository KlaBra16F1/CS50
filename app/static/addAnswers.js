let i = 2;
document.getElementById('add-new-answer').onclick = function () {
    let q_id = document.getElementById('q_id')
    let template = `
        <h3>Answer ${i}:</h3>
        <div class="row">
            <div class="cell-md-half">
                <input type="hidden" name="answer[${i}][q_id]" value="${q_id.value}">
                <label>Answer</label><br>
                <input name="answer[${i}][answer]" data-role="input" autocomplete="off">>
                <small>Markdown supported for <strong>__bold__</strong>, <em>_italics_</em> and <code>\`code\`.</code> </small>
            </div>
            <div class="cell-md-fifth">
                <label>True</label><br>
                <select name="answer[${i}][true]" data-role="select" data-filter="false">
                    <option value="0">False</option>
                    <option value="1">True</option>
                </select>
            </div>
            <div class="cell-md-full">
                <label>Comment</label><br>
                <textarea name="answer[${i}][comment]" data-role="textarea" class="w-75"></textarea>
                <small>Markdown supported for <strong>__bold__</strong>, <em>_italics_</em> and <code>\`code\`.</code> </small>
            </div>
        </div>`;

    let container = document.getElementById('answer-container');
    let div = document.createElement('div');
    div.innerHTML = template;
    container.appendChild(div);

    i++;
};