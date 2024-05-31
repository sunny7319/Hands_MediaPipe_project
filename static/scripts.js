document.getElementById('loginButton').addEventListener('click', () => {
    document.getElementById('initialView').classList.add('hidden');
    document.getElementById('loginView').classList.remove('hidden');
});

document.getElementById('registerButton').addEventListener('click', () => {
    document.getElementById('initialView').classList.add('hidden');
    document.getElementById('registerView').classList.remove('hidden');
});

document.getElementById('loginForm').addEventListener('submit', (event) => {
    event.preventDefault();
    const username = document.getElementById('loginUsername').value;
    const storedUsernames = JSON.parse(localStorage.getItem('usernames') || '[]');
    
    if (storedUsernames.includes(username)) {
        document.getElementById('loginView').classList.add('hidden');
        document.getElementById('mainView').classList.remove('hidden');
    } else {
        alert('등록된 아이디가 없습니다. 회원가입하시겠습니까?');
        document.getElementById('loginView').classList.add('hidden');
        document.getElementById('registerView').classList.remove('hidden');
    }
});

document.getElementById('registerForm').addEventListener('submit', (event) => {
    event.preventDefault();
    const username = document.getElementById('registerUsername').value;
    let storedUsernames = JSON.parse(localStorage.getItem('usernames') || '[]');

    if (!storedUsernames.includes(username)) {
        storedUsernames.push(username);
        localStorage.setItem('usernames', JSON.stringify(storedUsernames));
        alert('회원가입이 완료되었습니다. 로그인 하시겠습니까?');
        document.getElementById('registerView').classList.add('hidden');
        document.getElementById('loginView').classList.remove('hidden');
    } else {
        alert('이미 존재하는 아이디입니다.');
    }
});
