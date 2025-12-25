// Ejemplo: Botón de modo oscuro
document.addEventListener('DOMContentLoaded', function() {
    const btn = document.createElement('button');
    btn.innerHTML = '🌙';
    btn.style.position = 'fixed';
    btn.style.bottom = '20px';
    btn.style.right = '20px';
    btn.style.zIndex = 1000;
    btn.onclick = () => document.body.classList.toggle('dark-mode');
    document.body.appendChild(btn);
});