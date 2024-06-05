const video = document.getElementById('webcam');
const overlay = document.getElementById('overlay');
const hint = document.getElementById('hint');
const hintBtn = document.getElementById('hintBtn');
// const captureBtn = document.getElementById('captureBtn');
const nextBtn = document.getElementById('nextBtn');
const result = document.getElementById('result');
const quizImage = document.getElementById('quizImage');
const quizData = JSON.parse('{{ quiz_data | tojson | safe }}');

let currentQuizIndex = 0; // 현재 퀴즈 인덱스
let hintTimeouts = []; // 힌트 타이머 배열
let correctCount = 0; // 맞춘 문제 수
let wrongCount = 0; // 틀린 문제 수
let skippedCount = 0; // 건너뛴 문제 수
let lastImageData = ''; // 마지막으로 캡처된 이미지 데이터
let canProceed = true; // 다음 문제로 넘어갈 수 있는지 여부

function loadQuiz() {
    const quiz = quizData[currentQuizIndex];
    quizImage.src = `./static/${quiz.image}`;
    result.textContent = '';
    hint.textContent = '';
    hint.style.display = 'none';
    hintBtn.style.display = 'none';
    skipBtn.style.display = 'block';
    quizImage.style.display = 'block';
    video.style.display = 'block';
    quizPrompt.style.display = 'block';
    canProceed = true;
    clearHints();
    startHintTimers();
}

function startHintTimers() {
    hintTimeouts.push(setTimeout(() => {
        hintBtn.style.display = 'block';
    }, 60000)); // 1분 후 힌트 버튼 표시
}

hintBtn.addEventListener('click', () => {
    const quiz = quizData[currentQuizIndex];
    hint.textContent = `초성 힌트: ${getChosung(quiz.answer)}`;
    hint.style.display = 'block';

    hintTimeouts.push(setTimeout(() => {
        hint.textContent = `정답: ${quiz.answer}`;
    }, 60000)); // 힌트 버튼 클릭 후 1분 후 정답 표시
});

function clearHints() {
    hintTimeouts.forEach(timeout => clearTimeout(timeout));
    hintTimeouts = [];
    hint.style.display = 'none';
    hintBtn.style.display = 'none';
}

function getChosung(word) {
    const CHOSUNG_LIST = [
        "ㄱ", "ㄲ", "ㄴ", "ㄷ", "ㄸ", "ㄹ", "ㅁ", "ㅂ", "ㅃ", "ㅅ",
        "ㅆ", "ㅇ", "ㅈ", "ㅉ", "ㅊ", "ㅋ", "ㅌ", "ㅍ", "ㅎ"
    ];
    let result = "";
    for (let i = 0; i < word.length; i++) {
        let code = word.charCodeAt(i) - 44032;
        if (code > -1 && code < 11172) {
            result += CHOSUNG_LIST[Math.floor(code / 588)];
        } else {
            result += word.charAt(i);
        }
    }
    return result;
}

function checkAnswer(predictedClass, predictedProb) {
    const correctAnswer = quizData[currentQuizIndex].answer;
    if (predictedClass === correctAnswer && predictedProb >= 0.93) {
        result.textContent = `정답! ${predictedClass} (확률: ${(predictedProb * 100).toFixed(2)}%)`;
        correctCount++;
        if (canProceed) {
            canProceed = false;
            setTimeout(nextQuiz, 2000); // 2초 후 다음 퀴즈로 넘어감
        }
    } else {
        result.textContent = `오답! 예측된 클래스: ${predictedClass} (확률: ${(predictedProb * 100).toFixed(2)}%)`;
        wrongCount++;
    }
}

navigator.mediaDevices.getUserMedia({ video: true })
    .then(stream => {
        video.srcObject = stream;
    });

function captureAndCompare() {
    const canvas = document.createElement('canvas');
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    canvas.getContext('2d').drawImage(video, 0, 0);
    const data = canvas.toDataURL('image/jpeg');
    
    if (data !== lastImageData) {
        lastImageData = data;
        fetch('/capture', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ image: data })
        })
        .then(response => response.json())
        .then(data => {
            checkAnswer(data.class, data.probability);
        });
    }
}

setInterval(captureAndCompare, 1000);

skipBtn.addEventListener('click', () => {
    skippedCount++;
    nextQuiz();
});

function nextQuiz() {
    currentQuizIndex++;
    if (currentQuizIndex < quizData.length) {
        loadQuiz();
    } else {
        const totalAnswered = correctCount + wrongCount + skippedCount;
        quizImage.style.display = 'none';
        video.style.display = 'none';
        skipBtn.style.display = 'none';
        quizPrompt.style.display = 'none';
        if (correctCount / totalAnswered === 1) {
            wordKingImage.style.display = 'block';
            result.textContent = '모든 문제를 맞췄습니다! 단어왕!';
        } else {
            effortKingImage.style.display = 'block';
            result.textContent = '모든 퀴즈를 완료했습니다! 노력왕!';
        }
    }
}

loadQuiz();