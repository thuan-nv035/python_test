const canvas = document.getElementById("gameCanvas");
const ctx = canvas.getContext("2d");
const scoreElement = document.getElementById("score");

let snake = [{x: 200, y: 200}];
let food = {x: 0, y: 0};
let dx = 20, dy = 0;
let score = 0;

        function createFood() {
            food.x = Math.floor(Math.random() * 20) * 20;
            food.y = Math.floor(Math.random() * 20) * 20;
        }

        function draw() {
            // Xóa màn hình
            ctx.fillStyle = "#1a202c";
            ctx.fillRect(0, 0, canvas.width, canvas.height);

            // Vẽ rắn
            ctx.fillStyle = "#48bb78";
            snake.forEach(part => ctx.fillRect(part.x, part.y, 18, 18));

            // Vẽ mồi
            ctx.fillStyle = "#f56565";
            ctx.fillRect(food.x, food.y, 18, 18);

            // Di chuyển đầu rắn
            const head = {x: snake[0].x + dx, y: snake[0].y + dy};
            snake.unshift(head);

            // Kiểm tra ăn mồi
            if (head.x === food.x && head.y === food.y) {
                score += 10;
                scoreElement.innerText = score;
                createFood();
            } else {
                snake.pop();
            }

            // Kiểm tra đâm tường hoặc đâm vào thân
            if (head.x < 0 || head.x >= 400 || head.y < 0 || head.y >= 400) {
    guiDiemLenServer(score); // Gọi hàm gửi điểm
    alert("Game Over! Điểm: " + score);
//    location.reload();
}
        }

        document.addEventListener("keydown", e => {
            if (e.key === "ArrowUp" && dy === 0) { dx = 0; dy = -20; }
            if (e.key === "ArrowDown" && dy === 0) { dx = 0; dy = 20; }
            if (e.key === "ArrowLeft" && dx === 0) { dx = -20; dy = 0; }
            if (e.key === "ArrowRight" && dx === 0) { dx = 20; dy = 0; }
        });

        createFood();
        setInterval(draw, 100); // Tốc độ game

function guiDiemLenServer(diemSo) {
  fetch('/save-score', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ score: diemSo }), // Chuyển điểm thành chuỗi JSON
  })
    .then((response) => response.json())
    .then((data) => {
      console.log('Server trả về:', data.message);
    })
    .catch((error) => {
      console.error('Lỗi khi gửi điểm:', error);
    });
}

// Tìm chỗ Game Over trong code cũ và sửa lại:

