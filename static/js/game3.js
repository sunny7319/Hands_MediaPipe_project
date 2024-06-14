const video = document.getElementById('webcam');
const overlayhint = document.getElementById('overlay-hint'); // 힌트
const overlayimg = document.getElementById('overlay-img'); // 정답 후 이미지
const overlaywait = document.getElementById('overlay-wait'); // 기다리는 표시
const lastimg = document.getElementById('last-img'); // 정답 후 이미지
// const hint = document.getElementById('hint');
// const hint = document.createElement('div'); // 힌트 요소를 동적으로 생성
// document.body.appendChild(hint); // 힌트 요소를 body에 추가
// hint.id = 'hint'; // 힌트 요소에 ID 추가
const hintBtn = document.getElementById('hintBtn');
// const captureBtn = document.getElementById('captureBtn');
const nextBtn = document.getElementById('nextBtn');
const quizImage = document.getElementById('quizImage');

let currentQuizIndex = 0; // 현재 퀴즈 인덱스
let hintTimeouts = []; // 힌트 타이머 배열
let hintUsed = false; // 2번째 힌트 제시 이후(1분 이후의 여부)
// let hintCount = 0; // 힌트 첫번째(초성), 두번째(정답) 구분하기 위한 변수
// let firstHintTime = null; // 첫번째 힌트 타이머
// let secondHintTimeout = null; // 두번째 힌트 타이머
let correctCount = 0; // 맞춘 문제 수
let wrongCount = 0; // 틀린 문제 수
let skippedCount = 0; // 건너뛴 문제 수
let lastImageData = ''; // 마지막으로 캡처된 이미지 데이터
let canProceed = true; // 다음 문제로 넘어갈 수 있는지 여부

const quizData = [ // 퀴즈 데이터 배열
    {answer: '가지', image: 'img/game3/가지.png'},
    {answer: '나비', image: 'img/game3/나비.png'},
    {answer: '다리', image: 'img/game3/다리.jpeg'},
    {answer: '레몬', image: 'img/game3/레몬.png'},
    {answer: '마늘', image: 'img/game3/마늘.png'},
    {answer: '바위', image: 'img/game3/바위.png'},
    {answer: '사슴', image: 'img/game3/사슴.png'},
    {answer: '아기', image: 'img/game3/애기.png'},
    {answer: '자수', image: 'img/game3/자수.png'},
    {answer: '차고', image: 'img/game3/차고.png'},
    {answer: '카레', image: 'img/game3/카레.png'},
    {answer: '태양', image: 'img/game3/태양.png'},
    {answer: '팔', image: 'img/game3/팔.png'},
    {answer: '하늘', image: 'img/game3/하늘.png'},
];

// 비디오 확인
navigator.mediaDevices.getUserMedia({ video: true })
    .then(stream => {
        video.srcObject = stream;
    })
    .catch(err => {
        console.error("Error accessing webcam: ", err);
    });

// 힌트 버튼
hintBtn.addEventListener('click', () => {
    // let hintUsed = false; // 2번째 힌트 제시 이후(1분 이후의 여부)
    // if (hintUsed) return; // 힌트가 이미 사용되었다면 아무 것도 하지 않음

    const quiz = quizData[currentQuizIndex];
    overlayhint.textContent = `초성 힌트: ${getChosung(quiz.answer)}`;
    overlayhint.style.display = 'flex';

    setTimeout(function() {
        overlayhint.style.display = 'none';
    }, 5000); // 5초 후에 첫 번째 힌트 숨기기

    hintTimeouts.push(setTimeout(() => {
        overlayhint.textContent = `정답: ${quiz.answer}`;
        overlayhint.style.display = 'flex';
        hintUsed = true; // 1분 후에는 정답만 보이게
    }, 30000)); // 힌트 버튼 클릭 후 1분 후 정답 표시 // 현재는 30초로 설정
});

// 힌트 지우기
function clearHints() {
    // let hintUsed = false; // 2번째 힌트 제시 이후(1분 이후의 여부)
    hintTimeouts.forEach(timeout => clearTimeout(timeout));
    hintTimeouts = [];
    overlayhint.textContent = ''; // overlayhint 내용 초기화
    overlayhint.style.display = 'none';
}

// 다음 버튼
nextBtn.addEventListener('click', () => {  
    skippedCount++;
    nextQuiz();
});

// 퀴즈 로드
function loadQuiz() {
    const quiz = quizData[currentQuizIndex];
    quizImage.src = `../static/${quiz.image}`;
    overlayhint.textContent = ''; // 힌트 내용 초기화
    overlayhint.style.display = 'none'; // 힌트 숨김
    overlaywait.textContent = '정답을 기다리고 있어요 ...'; // 기다리는 중 문구
    overlaywait.style.display = 'block'; // 기다리는 중 문구 띄우기
    overlayimg.style.display = 'none'; // 정답 이미지 제거
    quizImage.style.display = 'block';
    video.style.display = 'block';
    canProceed = true;
    clearHints();
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
    if (predictedClass === correctAnswer && predictedProb >= 0.5) {
        // result.textContent = `정답! ${predictedClass} (확률: ${(predictedProb * 100).toFixed(2)}%)`;
        correctCount++;
        if (canProceed) { // 정답이면 힌트와 기다리는 중 문구 제거하고 정답 표시 하면서 2초 후 다음 퀴즈로 넘어감
            canProceed = false;
            setTimeout(function() {
                overlayhint.style.display = 'none'; // 힌트 제거
                overlaywait.style.display = 'none'; // 기다리는 중 문구 제거
                overlayimg.style.display = 'block'; // 정답이에요 표시
            }, 1000); // 1초 뒤 동작
            setTimeout(nextQuiz, 5000); // 4초 동안 정답 이미지 띄우고 다음 퀴즈로 넘어감
        }
    } else {
        console.log(`오답! 예측된 클래스: ${predictedClass} (확률: ${(predictedProb * 100).toFixed(2)}%)`);
        // result.textContent = `오답! 예측된 클래스: ${predictedClass} (확률: ${(predictedProb * 100).toFixed(2)}%)`;
        overlaywait.textContent = '정답을 기다리고 있어요 ...';
        wrongCount++;
    }
}

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

function nextQuiz() {
    currentQuizIndex++;
    if (currentQuizIndex < quizData.length) {
        loadQuiz();
    } else {
        const cci = document.getElementById('cci');
        cci.style.display = 'none';
        overlayimg.style.display = 'none'; // 정답 표시 숨김
        overlaywait.style.display = 'none'; // 기다리는 표시 숨김
        quizImage.style.display = 'none'; // 문제이미지 숨김
        video.style.display = 'none'; // 비디오 숨김
        hintBtn.style.display = 'none'; // 힌트버튼 숨김
        nextBtn.style.display = 'none'; // 다음버튼 숨김
        // lastimg.style.display = 'block'; // 마지막 잘했어요 이미지 띄우기


        // 설문조사 페이지로 이동
        setTimeout(() => {
            window.location.href = "/survey3";
        }, 1000); // 3초 후에 설문조사 페이지로 이동
    }
}

loadQuiz();