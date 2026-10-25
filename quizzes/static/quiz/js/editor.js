(() => {
  const container = document.getElementById('questions');
  const hidden = document.getElementById('questionsJson');
  const counter = document.getElementById('questionCount');
  const form = document.getElementById('quizForm');
  if (!container || !hidden || !counter || !form) return;
  const questions = [];
  const colors = ['#7856ff', '#ff7a59', '#00a987', '#f0a500'];
  const escapeHTML = value => String(value).replace(/[&<>"']/g, char => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[char]));
  function render() {
    counter.textContent = questions.length;
    container.innerHTML = questions.map((question, index) => `
      <article class="question-editor">
        <div class="question-editor-head"><span class="question-badge">${String(index + 1).padStart(2, '0')}</span><strong>Câu hỏi ${index + 1}</strong><button class="remove-question" type="button" data-remove="${index}" aria-label="Xóa câu hỏi">×</button></div>
        <textarea class="text-input prompt-input" data-prompt="${index}" maxlength="300" required placeholder="Nhập nội dung câu hỏi...">${escapeHTML(question.text || '')}</textarea>
        <div class="question-options-head"><span>4 lựa chọn</span><span>Chọn vòng tròn ở đáp án đúng</span></div>
        <div class="choice-list">${question.choices.map((choice, choiceIndex) => `
          <div class="choice-input" style="--choice-color:${colors[choiceIndex]}"><label class="choice-pick"><input type="radio" name="correct-${index}" value="${choiceIndex}" ${question.correct === choiceIndex ? 'checked' : ''}><span class="choice-dot"></span><span class="choice-letter">${'ABCD'[choiceIndex]}</span></label><input type="text" data-choice="${index}-${choiceIndex}" maxlength="180" required placeholder="Lựa chọn ${choiceIndex + 1}" value="${escapeHTML(choice)}"></div>`).join('')}</div>
        <div class="question-extra"><label>Điểm cho câu này<input type="number" data-points="${index}" min="0" max="1000" value="${question.points ?? 100}"></label><label class="explanation-field">Giải thích đáp án <span>(không bắt buộc)</span><textarea data-explanation="${index}" maxlength="2000" placeholder="Giải thích ngắn để người chơi hiểu vì sao đáp án này đúng...">${escapeHTML(question.explanation || '')}</textarea></label></div>
      </article>`).join('');
  }
  function sync() {
    container.querySelectorAll('[data-prompt]').forEach(el => { questions[Number(el.dataset.prompt)].text = el.value; });
    container.querySelectorAll('[data-choice]').forEach(el => { const [q, c] = el.dataset.choice.split('-').map(Number); questions[q].choices[c] = el.value; });
    container.querySelectorAll('[data-points]').forEach(el => { questions[Number(el.dataset.points)].points = Number(el.value || 0); });
    container.querySelectorAll('[data-explanation]').forEach(el => { questions[Number(el.dataset.explanation)].explanation = el.value; });
    container.querySelectorAll('input[type=radio]:checked').forEach(el => { questions[Number(el.name.split('-')[1])].correct = Number(el.value); });
    hidden.value = JSON.stringify(questions);
  }
  container.addEventListener('input', sync);
  container.addEventListener('change', sync);
  container.addEventListener('click', event => {
    const button = event.target.closest('[data-remove]');
    if (button) { questions.splice(Number(button.dataset.remove), 1); render(); sync(); }
  });
  document.getElementById('addQuestion').addEventListener('click', () => {
    if (questions.length >= 50) return;
    questions.push({text:'', choices:['','','',''], correct:0, points:100, explanation:''}); render();
    container.lastElementChild.scrollIntoView({behavior:'smooth', block:'center'});
  });
  form.addEventListener('submit', event => {
    sync();
    if (!questions.length) { event.preventDefault(); alert('Thêm ít nhất một câu hỏi nhé!'); }
  });
  questions.push({text:'', choices:['','','',''], correct:0, points:100, explanation:''});
  render(); sync();
})();
