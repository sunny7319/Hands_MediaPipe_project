const video = document.getElementById('webcam');
const overlay = document.getElementById('overlay');
// const hint = document.getElementById('hint');
// const hint = document.createElement('div'); // 힌트 요소를 동적으로 생성
// document.body.appendChild(hint); // 힌트 요소를 body에 추가
// hint.id = 'hint'; // 힌트 요소에 ID 추가
const hintBtn = document.getElementById('hintBtn');
// const captureBtn = document.getElementById('captureBtn');
const nextBtn = document.getElementById('nextBtn');
const result = document.getElementById('result');
const quizImage = document.getElementById('quizImage');

let currentQuizIndex = 0; // 현재 퀴즈 인덱스
let hintTimeouts = []; // 힌트 타이머 배열
let correctCount = 0; // 맞춘 문제 수
let wrongCount = 0; // 틀린 문제 수
let skippedCount = 0; // 건너뛴 문제 수
let lastImageData = ''; // 마지막으로 캡처된 이미지 데이터
let canProceed = true; // 다음 문제로 넘어갈 수 있는지 여부

const quizData = [ // 퀴즈 데이터 배열
    {answer: '가지', image: 'img/game3/가지.jpeg'},
    {answer: '나비', image: 'img/game3/나비.jpeg'},
    {answer: '다리', image: 'img/game3/다리.jpeg'},
    {answer: '레몬', image: 'img/game3/레몬.jpeg'},
    {answer: '마늘', image: 'img/game3/마늘.jpeg'},
    {answer: '바위', image: 'img/game3/바위.jpeg'},
    {answer: '사슴', image: 'img/game3/사슴.jpeg'},
    {answer: '애기', image: 'img/game3/애기.jpeg'},
    {answer: '자수', image: 'img/game3/자수.jpeg'},
    {answer: '차고', image: 'img/game3/차고.jpeg'},
    {answer: '카레', image: 'img/game3/카레.jpeg'},
    {answer: '태양', image: 'img/game3/태양.jpeg'},
    {answer: '팔', image: 'img/game3/팔.jpeg'},
    {answer: '하늘', image: 'img/game3/하늘.jpeg'},
];

hintBtn.addEventListener('click', () => {
    const quiz = quizData[currentQuizIndex];
    console.log(`Current Quiz Answer: ${quiz.answer}`); // 로그 추가
    overlay.textContent = `초성 힌트: ${getChosung(quiz.answer)}`; // 힌트를 overlay에 표시
    overlay.style.display = 'flex'; // overlay 보이기
    hintBtn.classList.remove('shake'); // 흔들림 효과 제거
    console.log('Hint shown:', overlay.textContent); // 로그 추가

    // 1분 후 정답 표시
    hintTimeouts.push(setTimeout(() => {
        overlay.textContent = `정답: ${quiz.answer}`; // overlay에 정답 표시
        console.log('Answer shown:', overlay.textContent); // 로그 추가
    }, 60000));
});

function startHintTimers() {
    hintTimeouts.push(setTimeout(() => {
        hintBtn.textContent = ''; // 힌트 버튼의 텍스트 제거
        hintBtn.classList.add('shake'); // 흔들림 효과 추가
        hintBtn.style.display = 'block';
        
        const quiz = quizData[currentQuizIndex];
        console.log(`Hint timer started for: ${quiz.answer}`); // 로그 추가
        overlay.textContent = `초성 힌트: ${getChosung(quiz.answer)}`;
        overlay.style.display = 'block';
    }, 3000)); // 3초 후 힌트 표시 및 흔들림 효과 추가
}

function clearHints() {
    hintTimeouts.forEach(timeout => clearTimeout(timeout));
    hintTimeouts = [];
    overlay.style.display = 'none'; // overlay 숨김
}

function loadQuiz() {
    const quiz = quizData[currentQuizIndex];
    quizImage.src = `../static/${quiz.image}`;
    result.textContent = '';
    overlay.textContent = ''; // overlay 내용 초기화
    overlay.style.display = 'none'; // overlay 숨김
    hintBtn.classList.remove('shake'); // 흔들림 효과 제거
    hintBtn.style.display = 'block';
    nextBtn.style.display = 'block';
    quizImage.style.display = 'block';
    video.style.display = 'block';
    canProceed = true;
    clearHints();
    startHintTimers();
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
        // result.textContent = `정답! ${predictedClass} (확률: ${(predictedProb * 100).toFixed(2)}%)`;
        correctCount++;
        if (canProceed) {
            canProceed = false;
            setTimeout(nextQuiz, 2000); // 2초 후 다음 퀴즈로 넘어감
        }
    } else {
        // result.textContent = `오답! 예측된 클래스: ${predictedClass} (확률: ${(predictedProb * 100).toFixed(2)}%)`;
        wrongCount++;
    }
}

navigator.mediaDevices.getUserMedia({ video: true })
    .then(stream => {
        video.srcObject = stream;
    })
    .catch(err => {
        console.error("Error accessing webcam: ", err);
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

setInterval(captureAndCompare, 1000);  // 1초마다 실시간으로 확인

nextBtn.addEventListener('click', () => {  // 다음 버튼
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
        nextBtn.style.display = 'none';
        if (correctCount / totalAnswered === 1) {
            result.textContent = '모든 문제를 맞췄습니다! 단어왕!';
        } else {
            result.textContent = '모든 퀴즈를 완료했습니다! 노력왕!';
        }
    }
}

loadQuiz();