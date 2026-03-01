// State Management
const STATE = {
  questions: [],
  allLoadedQuestions: [],
  currentIndex: 0,
  score: 0,
  userAnswers: [],
  theorySources: ['exammmm.pdf', 'ECMG.pdf'],
  practicalSources: ['ICs.pdf', 'DIODES.pdf', 'MEASUREMENTS.pdf', 'CAPACITORS.pdf', 'TRANSISTOR.pdf']
};

// Cached DOM Elements
const UI = {
  loading: document.getElementById('loading'),
  screens: {
    start: document.getElementById('start-screen'),
    quiz: document.getElementById('question-screen'),
    end: document.getElementById('end-screen')
  },
  btns: {
    theory: document.getElementById('theory-btn'),
    practical: document.getElementById('practical-btn'),
    back: document.getElementById('back-btn'),
    skip: document.getElementById('skip-btn'),
    next: document.getElementById('next-btn'),
    home: document.getElementById('home-btn'),
    restart: document.getElementById('restart-btn')
  },
  displays: {
    score: document.getElementById('score'),
    questionText: document.getElementById('question-text'),
    options: document.getElementById('options-container'),
    progress: document.getElementById('progress-bar'),
    counter: document.getElementById('question-counter'),
    source: document.getElementById('source-badge'),
    finalScore: document.getElementById('final-score'),
    accuracy: document.getElementById('percentage-score'),
    totalInfo: document.getElementById('total-questions-info')
  }
};

// Utilities
const shuffle = (arr) => {
  for (let i = arr.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [arr[i], arr[j]] = [arr[j], arr[i]];
  }
  return arr;
};

const updateUI = {
  screen(name) {
    Object.keys(UI.screens).forEach(key =>
      UI.screens[key].classList.toggle('hidden', key !== name)
    );
    UI.btns.home.classList.toggle('hidden', name === 'start');
  },
  score() {
    UI.displays.score.textContent = STATE.score;
  }
};

// Core Logic
async function initApp() {
  try {
    if (typeof RAW_QUESTIONS === 'undefined') throw new Error('Data skip');
    STATE.allLoadedQuestions = RAW_QUESTIONS;

    UI.loading.classList.add('hidden');
    updateUI.screen('start');
    UI.displays.totalInfo.textContent = `Loaded ${STATE.allLoadedQuestions.length} questions. Select an exam:`;
  } catch (e) {
    UI.loading.innerHTML = '<p>Error loading data. Please run the extractor.</p>';
  }
}

function startQuiz(type) {
  STATE.score = 0;
  STATE.currentIndex = 0;
  STATE.userAnswers = [];
  updateUI.score();
  updateUI.screen('quiz');

  const filterFn = (type === 'theory')
    ? q => STATE.theorySources.some(s => q.source.includes(s))
    : (type === 'practical')
      ? q => STATE.practicalSources.some(s => q.source.includes(s))
      : () => true;

  STATE.questions = shuffle([...STATE.allLoadedQuestions].filter(filterFn));
  showQuestion();
}

function showQuestion() {
  const q = STATE.questions[STATE.currentIndex];
  const prevAns = STATE.userAnswers[STATE.currentIndex];

  // Navigation visibility
  UI.btns.next.classList.toggle('hidden', prevAns === undefined);
  UI.btns.skip.classList.toggle('hidden', prevAns !== undefined);
  UI.btns.back.classList.toggle('hidden', STATE.currentIndex === 0);

  // Content updates
  UI.displays.questionText.textContent = q.question;
  UI.displays.source.textContent = q.source || 'PDF';
  UI.displays.counter.textContent = `Question ${STATE.currentIndex + 1}/${STATE.questions.length}`;
  UI.displays.progress.style.width = `${(STATE.currentIndex / STATE.questions.length) * 100}%`;

  // Efficient DOM Injection
  const fragment = document.createDocumentFragment();
  q.options.forEach((opt, idx) => {
    const btn = document.createElement('button');
    btn.className = 'option-btn';
    btn.textContent = opt.text;
    btn.style.animationDelay = `${idx * 0.05}s`;

    if (prevAns !== undefined) {
      btn.disabled = true;
      if (prevAns === idx) btn.classList.add(opt.isCorrect ? 'correct' : 'wrong');
      else if (opt.isCorrect && prevAns !== -1) btn.classList.add('correct');
    } else {
      btn.onclick = () => selectAnswer(btn, idx);
    }
    fragment.appendChild(btn);
  });

  UI.displays.options.replaceChildren(fragment);
}

function selectAnswer(btn, idx) {
  const q = STATE.questions[STATE.currentIndex];
  STATE.userAnswers[STATE.currentIndex] = idx;

  const buttons = UI.displays.options.querySelectorAll('.option-btn');
  buttons.forEach(b => b.disabled = true);

  if (q.options[idx].isCorrect) {
    btn.classList.add('correct');
    STATE.score++;
    updateUI.score();
  } else {
    btn.classList.add('wrong');
    q.options.forEach((opt, i) => {
      if (opt.isCorrect) buttons[i].classList.add('correct');
    });
  }

  UI.btns.skip.classList.add('hidden');
  UI.btns.next.classList.remove('hidden');
}

function handleNext() {
  STATE.currentIndex++;
  if (STATE.currentIndex < STATE.questions.length) showQuestion();
  else showEndScreen();
}

function handleBack() {
  if (STATE.currentIndex > 0) {
    const currentAns = STATE.userAnswers[STATE.currentIndex - 1];
    if (currentAns !== undefined && currentAns !== -1 && STATE.questions[STATE.currentIndex - 1].options[currentAns].isCorrect) {
      STATE.score--;
      updateUI.score();
    }
    STATE.currentIndex--;
    STATE.userAnswers[STATE.currentIndex] = undefined;
    showQuestion();
  }
}

function showEndScreen() {
  updateUI.screen('end');
  UI.displays.finalScore.textContent = `${STATE.score} / ${STATE.questions.length}`;
  const pct = Math.round((STATE.score / STATE.questions.length) * 100) || 0;
  UI.displays.accuracy.textContent = `${pct}% Accuracy`;
}

// Event Listeners
UI.btns.theory.onclick = () => startQuiz('theory');
UI.btns.practical.onclick = () => startQuiz('practical');
UI.btns.next.onclick = handleNext;
UI.btns.skip.onclick = () => { STATE.userAnswers[STATE.currentIndex] = -1; handleNext(); };
UI.btns.back.onclick = handleBack;
UI.btns.restart.onclick = () => updateUI.screen('start');
UI.btns.home.onclick = () => confirm('Lose progress and return home?') && updateUI.screen('start');

initApp();
