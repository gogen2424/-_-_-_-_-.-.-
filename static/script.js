function updateTime() {
    const now = new Date();
    const timeElement = document.getElementById('current-time');
    const dateElement = document.getElementById('current-date');

    const options = { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' };
    const formattedDate = now.toLocaleDateString('ru-RU', options);

    const formattedTime = now.toLocaleTimeString('ru-RU', {
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit',
    });

    timeElement.textContent = formattedTime;
    dateElement.textContent = formattedDate;
}

// Обновление времени и даты каждую секунду
setInterval(updateTime, 1000);

// Вызов функции updateTime для отображения времени и даты при загрузке страницы
updateTime();
function f1(){
    window.location.href("statistics.html")
}