async function fetchGameData() {
    try {
        const response = await fetch('/send_game2');
        const data = await response.json();
        document.getElementById('time').textContent = "Time: " + data.time;
        document.getElementById('stage').textContent = "Stage " + data.stage;
        document.getElementById('score').textContent = "Score: " + data.score;
        document.getElementById('question').innerHTML = data.question + `<br>두더지만<br>잡아보세요!`;

        if (data.quit === 1) {  // 조건이 충족되면 페이지 이동
            window.location.href = "/survey2";
        }
    } catch (error) {
        console.error('Error fetching game data:', error);
    }
}

setInterval(fetchGameData, 1000); // 1초마다 데이터 가져오기