const API_URL = "";

async function handleAuth(type) {
    const formData = new FormData();
    formData.append('username', document.getElementById('username').value);
    formData.append('password', document.getElementById('password').value);

    const res = await fetch(`/${type}`, { method: 'POST', body: formData });
    const data = await res.json();

    if (data.access_token) {
        localStorage.setItem('token', data.access_token);
        window.location.href = "/";
    } else {
        alert(type === 'login' ? "Ошибка входа" : "Регистрация успешна! Теперь войдите");
    }
}

// Показ редактора если залогинен
if (localStorage.getItem('token')) {
    document.getElementById('editor-zone').style.display = 'block';
    document.getElementById('auth-nav').innerHTML = '<button onclick="logout()">Выйти</button>';
}

document.getElementById('postForm')?.addEventListener('submit', async (e) => {
    e.preventDefault();
    const formData = new FormData();
    formData.append('title', document.getElementById('title').value);
    formData.append('content', document.getElementById('content').value);
    formData.append('tags', document.getElementById('tags').value);
    formData.append('is_hidden', document.getElementById('is_hidden').checked);

    await fetch('/posts', {
        method: 'POST',
        headers: {'Authorization': 'Bearer ' + localStorage.getItem('token')},
        body: formData
    });
    location.reload();
});

async function followUser(userId) {
    await fetch(`/follow/${userId}`, {
        method: 'POST',
        headers: {'Authorization': 'Bearer ' + localStorage.getItem('token')}
    });
    alert("Подписка оформлена");
}

async function addComment(postId) {
    const text = document.getElementById(`comm-${postId}`).value;
    const formData = new FormData();
    formData.append('text', text);

    await fetch(`/posts/${postId}/comment`, {
        method: 'POST',
        headers: {'Authorization': 'Bearer ' + localStorage.getItem('token')},
        body: formData
    });
    location.reload();
}

function logout() {
    localStorage.clear();
    location.reload();
}