let cards = [];
let flippedCards = [];
let matchedPairs = 0;
let moves = 0;
let canFlip = true;
let currentTheme = 'emoji';

async function initGame() {
    const themeSelect = document.getElementById('theme-select');
    currentTheme = themeSelect.value;
    
    const response = await fetch(`api/new-game?theme=${currentTheme}`);
    const data = await response.json();
    cards = data.cards;
    matchedPairs = 0;
    moves = 0;
    flippedCards = [];
    canFlip = true;
    
    document.getElementById('win-modal').classList.add('hidden');
    updateUI();
    renderBoard();
}

function renderBoard() {
    const board = document.getElementById('game-board');
    board.innerHTML = '';
    
    cards.forEach((item, index) => {
        const card = document.createElement('div');
        card.className = 'card';
        card.dataset.index = index;
        
        const displayContent = currentTheme === 'emoji' ? item : `<div class="text-card">${item}</div>`;
        
        card.innerHTML = `
            <span class="back">❓</span>
            <span class="front">${displayContent}</span>
        `;
        card.addEventListener('click', () => flipCard(index));
        board.appendChild(card);
    });
}

function flipCard(index) {
    if (!canFlip) return;
    
    const cardElement = document.querySelector(`[data-index="${index}"]`);
    
    if (cardElement.classList.contains('flipped') || 
        cardElement.classList.contains('matched')) {
        return;
    }
    
    cardElement.classList.add('flipped');
    flippedCards.push(index);
    
    if (flippedCards.length === 2) {
        canFlip = false;
        moves++;
        updateUI();
        checkMatch();
    }
}

function checkMatch() {
    const [index1, index2] = flippedCards;
    const card1 = document.querySelector(`[data-index="${index1}"]`);
    const card2 = document.querySelector(`[data-index="${index2}"]`);
    
    if (cards[index1] === cards[index2]) {
        setTimeout(() => {
            card1.classList.add('matched');
            card2.classList.add('matched');
            createMatchSparkle(card1);
            createMatchSparkle(card2);
            matchedPairs++;
            updateUI();
            flippedCards = [];
            canFlip = true;
            
            if (matchedPairs === 8) {
                setTimeout(() => {
                    showWinModal();
                }, 500);
            }
        }, 500);
    } else {
        setTimeout(() => {
            card1.classList.remove('flipped');
            card2.classList.remove('flipped');
            flippedCards = [];
            canFlip = true;
        }, 1000);
    }
}

function updateUI() {
    document.getElementById('moves').textContent = moves;
    document.getElementById('matches').textContent = matchedPairs;
}

function showWinModal() {
    document.getElementById('final-moves').textContent = moves;
    document.getElementById('win-modal').classList.remove('hidden');
    createConfetti();
}

function createMatchSparkle(cardElement) {
    const rect = cardElement.getBoundingClientRect();
    const colors = ['#ffd93d', '#a8e6cf', '#667eea'];
    
    for (let i = 0; i < 8; i++) {
        const sparkle = document.createElement('div');
        sparkle.style.position = 'fixed';
        sparkle.style.width = '8px';
        sparkle.style.height = '8px';
        sparkle.style.backgroundColor = colors[Math.floor(Math.random() * colors.length)];
        sparkle.style.borderRadius = '50%';
        sparkle.style.left = rect.left + rect.width / 2 + 'px';
        sparkle.style.top = rect.top + rect.height / 2 + 'px';
        sparkle.style.pointerEvents = 'none';
        sparkle.style.zIndex = '1000';
        
        document.body.appendChild(sparkle);
        
        const angle = (i / 8) * Math.PI * 2;
        const distance = 50;
        const xMovement = Math.cos(angle) * distance;
        const yMovement = Math.sin(angle) * distance;
        
        sparkle.animate([
            { transform: 'translate(0, 0) scale(1)', opacity: 1 },
            { transform: `translate(${xMovement}px, ${yMovement}px) scale(0)`, opacity: 0 }
        ], {
            duration: 600,
            easing: 'ease-out'
        });
        
        setTimeout(() => sparkle.remove(), 600);
    }
}

function createConfetti() {
    const colors = ['#667eea', '#764ba2', '#a8e6cf', '#ffd93d', '#ff6b9d'];
    const confettiCount = 50;
    
    for (let i = 0; i < confettiCount; i++) {
        setTimeout(() => {
            const confetti = document.createElement('div');
            confetti.style.position = 'fixed';
            confetti.style.width = '10px';
            confetti.style.height = '10px';
            confetti.style.backgroundColor = colors[Math.floor(Math.random() * colors.length)];
            confetti.style.left = Math.random() * 100 + '%';
            confetti.style.top = '-10px';
            confetti.style.borderRadius = Math.random() > 0.5 ? '50%' : '0';
            confetti.style.opacity = '1';
            confetti.style.pointerEvents = 'none';
            confetti.style.zIndex = '9999';
            
            document.body.appendChild(confetti);
            
            const duration = 2000 + Math.random() * 1000;
            const xMovement = (Math.random() - 0.5) * 200;
            
            confetti.animate([
                { transform: 'translate(0, 0) rotate(0deg)', opacity: 1 },
                { transform: `translate(${xMovement}px, ${window.innerHeight + 20}px) rotate(${Math.random() * 720}deg)`, opacity: 0 }
            ], {
                duration: duration,
                easing: 'cubic-bezier(0.25, 0.46, 0.45, 0.94)'
            });
            
            setTimeout(() => confetti.remove(), duration);
        }, i * 30);
    }
}

document.getElementById('reset-btn').addEventListener('click', initGame);
document.getElementById('play-again-btn').addEventListener('click', initGame);
document.getElementById('theme-select').addEventListener('change', initGame);

initGame();
