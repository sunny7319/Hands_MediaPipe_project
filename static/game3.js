const video = document.getElementById('webcam');
const captureBtn = document.getElementById('captureBtn');
const nextBtn = document.getElementById('nextBtn');
const result = document.getElementById('result');
let currentQuizIndex = 0;

const quizData = [
    {answer: '가지', image: '{{ url_for("static", filename="img/game3/가지.jpeg") }}'},
    {answer: '나비', image: '{{ url_for("static", filename="img/game3/나비.jpeg") }}'},
    {answer: '다리', image: '{{ url_for("static", filename="img/game3/다리.jpeg") }}'},
    {answer: '레몬', image: '{{ url_for("static", filename="img/game3/레몬.jpeg") }}'},
    {answer: '마늘', image: '{{ url_for("static", filename="img/game3/마늘.jpeg") }}'},
    {answer: '바위', image: '{{ url_for("static", filename="img/game3/바위.jpeg") }}'},
    {answer: '사슴', image: '{{ url_for("static", filename="img/game3/사슴.png") }}'},
    {answer: '애기', image: '{{ url_for("static", filename="img/game3/애기.jpeg") }}'},
    {answer: '자수', image: '{{ url_for("static", filename="img/game3/자수.jpeg") }}'},
    {answer: '차고', image: '{{ url_for("static", filename="img/game3/차고.jpeg") }}'},
    {answer: '카레', image: '{{ url_for("static", filename="img/game3/카레.jpeg") }}'},
    {answer: '태양', image: '{{ url_for("static", filename="img/game3/태양.jpeg") }}'},
    {answer: '팔', image: '{{ url_for("static", filename="img/game3/팔.jpeg") }}'},
    {answer: '하늘', image: '{{ url_for("static", filename="img/game3/하늘.jpeg") }}'}
];

function showContent() {
    document.getElementById('loading-screen').style.display = 'none';
    document.getElementById('content').style.display = 'block';
}

function loadQuiz() {
    const quiz = quizData[currentQuizIndex];
    document.getElementById('quizImage').src = quiz.image;
    result.textContent = '';
    nextBtn.style.display = 'none';
    captureBtn.style.display = 'block';
}

function checkAnswer(predictedClass) {
    const correctAnswer = quizData[currentQuizIndex].answer;
    if (predictedClass === correctAnswer) {
        result.textContent = `정답! ${predictedClass}`;
        nextBtn.style.display = 'block';
        captureBtn.style.display = 'none';
    } else {
        result.textContent = `오답! 예측된 클래스: ${predictedClass}`;
    }
}

navigator.mediaDevices.getUserMedia({ video: true })
    .then(stream => {
        video.srcObject = stream;
        showContent();  // 카메라 스트림을 성공적으로 가져오면 로딩 화면을 숨기고 콘텐츠를 표시합니다.
    });

captureBtn.addEventListener('click', () => {
    const canvas = document.createElement('canvas');
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    canvas.getContext('2d').drawImage(video, 0, 0);
    const data = canvas.toDataURL('image/jpeg');
    fetch('/capture', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ image: data })
    })
    .then(response => response.json())
    .then(data => {
        checkAnswer(data.class);
        // 서버에서 반환된 값을 표시합니다.
        const resultElement = document.getElementById('result');
        resultElement.textContent = `예측된 클래스: ${data.class}, 확률: ${data.probability}`;
    });
});

nextBtn.addEventListener('click', () => {
    currentQuizIndex++;
    if (currentQuizIndex < quizData.length) {
        loadQuiz();
    } else {
        result.textContent = '모든 퀴즈를 완료했습니다!';
        nextBtn.style.display = 'none';
    }
});

loadQuiz(); // 첫 퀴즈를 로드합니다.
