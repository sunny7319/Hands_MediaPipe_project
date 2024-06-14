// // 주기적으로 toggle 값을 가져와서 업데이트하는 함수
// setInterval(function() {
//     fetch('/current_position')
//         .then(response => response.json())
//         .then(data => {
//             if (data.x !== undefined && data.y !== undefined) {
//                 const positionDisplay = document.getElementById('position-display');
//                 const newPos = `(${data.x}, ${data.y})`;
//                 positionDisplay.textContent = newPos;
//                 updateImage(data.label, data.x, data.y);
//             } else {
//                 console.error('Invalid data format:', data);
//             }
//         })
//         .catch(error => {
//             console.error('Error fetching position:', error);
//         });
// }, 1000); // 1초마다 업데이트

// function updateImage(label, x, y) {
//     const imageContainer = document.getElementById('image-container');
//     if (!imageContainer) {
//         console.error('imageContainer not found');
//         return;
//     }
//     imageContainer.innerHTML = ''; // 기존 이미지를 지우고 새로 그림
//     const img = document.createElement('img');
//     img.src = getGifSource(label);
//     img.classList.add('moving-img');
//     img.style.left = `${x}px`;
//     img.style.top = `${y}px`;
//     img.style.width = '300px';
//     imageContainer.appendChild(img);
// }

// function getGifSource(label) {
//     const gifMap = {
//         0: '{{ url_for("static", filename="img/game1/butterfly_1.gif") }}',
//         1: '{{ url_for("static", filename="img/game1/cat_1.gif") }}',
//         2: '{{ url_for("static", filename="img/game1/snail_1.gif") }}',
//         3: '{{ url_for("static", filename="img/game1/deer_1.gif") }}',
//         4: '{{ url_for("static", filename="img/game1/heart.gif") }}',
//         5: '{{ url_for("static", filename="img/game1/duck_1.gif") }}',
//         6: '{{ url_for("static", filename="img/game1/sun.gif") }}',
//         7: '{{ url_for("static", filename="img/game1/house.gif") }}',
//         8: '{{ url_for("static", filename="img/game1/tree.gif") }}',
//         9: '{{ url_for("static", filename="img/game1/rock.gif") }}',
//         10: '{{ url_for("static", filename="img/game1/flower.gif") }}',
//         11: '{{ url_for("static", filename="img/game1/dog_1.gif") }}'
//     };
//     return gifMap[label];
// }

// const quizImages = {
//     0: '{{ url_for("static", filename="img/game1/quiz_sun.png") }}',
//     1: '{{ url_for("static", filename="img/game1/quiz_dog.png") }}',
//     2: '{{ url_for("static", filename="img/game1/quiz_cat.png") }}',
//     3: '{{ url_for("static", filename="img/game1/quiz_heart.png") }}',
//     4: '{{ url_for("static", filename="img/game1/quiz_butterfly.png") }}',
//     5: '{{ url_for("static", filename="img/game1/quiz_flower.png") }}',
//     6: '{{ url_for("static", filename="img/game1/quiz_tree.png") }}'
// };

async function fetchGameData() {
    try {
        const response = await fetch('/send_game1');
        const data = await response.json();
        document.getElementById('stage').textContent = "Stage " + data.stage + " / 7";

        if (data.quit === 1) {  // 조건이 충족되면 페이지 이동
            window.location.href = "/survey1";
        } else {
            updateQuizImage(data.stage);
        }
    } catch (error) {
        console.error('Error fetching game data:', error);
    }
}

function updateQuizImage(stage) {
    const quizImage = document.getElementById('quizImage');
    if (quizImages[stage]) {
        console.log(quizImages[stage]);
        quizImage.src = quizImages[stage];
    } else {
        console.error('Quiz image not found for stage:', stage);
    }
}

setInterval(fetchGameData, 1000); // 1초마다 데이터 가져오기