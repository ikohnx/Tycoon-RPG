const GameEffects = {
    sounds: {
        coinCollect: null,
        levelUp: null,
        correct: null,
        incorrect: null,
        starEarn: null,
        click: null,
        streak: null,
        combo: null
    },
    
    streakCount: 0,
    
    init: function() {
        this.createSoundElements();
        this.loadStreakFromSession();
    },
    
    createSoundElements: function() {
        const AudioContext = window.AudioContext || window.webkitAudioContext;
        if (AudioContext) {
            this.audioContext = new AudioContext();
        }
    },
    
    playTone: function(frequency, duration, type = 'sine', volume = 0.3) {
        if (!this.audioContext) return;
        
        if (this.audioContext.state === 'suspended') {
            this.audioContext.resume();
        }
        
        const oscillator = this.audioContext.createOscillator();
        const gainNode = this.audioContext.createGain();
        
        oscillator.connect(gainNode);
        gainNode.connect(this.audioContext.destination);
        
        oscillator.frequency.value = frequency;
        oscillator.type = type;
        
        gainNode.gain.setValueAtTime(volume, this.audioContext.currentTime);
        gainNode.gain.exponentialRampToValueAtTime(0.01, this.audioContext.currentTime + duration);
        
        oscillator.start(this.audioContext.currentTime);
        oscillator.stop(this.audioContext.currentTime + duration);
    },
    
    playCoinSound: function() {
        this.playTone(1200, 0.1, 'sine', 0.2);
        setTimeout(() => this.playTone(1500, 0.15, 'sine', 0.15), 80);
    },
    
    playCorrectSound: function() {
        this.playTone(523, 0.1, 'sine', 0.2);
        setTimeout(() => this.playTone(659, 0.1, 'sine', 0.2), 100);
        setTimeout(() => this.playTone(784, 0.15, 'sine', 0.25), 200);
    },
    
    playIncorrectSound: function() {
        this.playTone(200, 0.3, 'sawtooth', 0.15);
    },
    
    playLevelUpSound: function() {
        const notes = [523, 659, 784, 1047];
        notes.forEach((freq, i) => {
            setTimeout(() => this.playTone(freq, 0.2, 'sine', 0.25), i * 150);
        });
    },
    
    playStarSound: function(starNumber) {
        const freqs = [880, 1047, 1319];
        this.playTone(freqs[starNumber - 1] || 880, 0.3, 'sine', 0.2);
    },
    
    playStreakSound: function(count) {
        const baseFreq = 400 + (count * 50);
        this.playTone(baseFreq, 0.1, 'square', 0.15);
        setTimeout(() => this.playTone(baseFreq * 1.5, 0.15, 'square', 0.2), 80);
    },
    
    playComboSound: function() {
        for (let i = 0; i < 5; i++) {
            setTimeout(() => this.playTone(600 + i * 100, 0.1, 'sine', 0.2), i * 60);
        }
    },
    
    createConfetti: function(container, count = 50) {
        const colors = ['#ffd700', '#ff6b6b', '#4ecdc4', '#45b7d1', '#96e6a1', '#dda0dd'];
        const confettiContainer = document.createElement('div');
        confettiContainer.className = 'confetti-container';
        confettiContainer.style.cssText = 'position:fixed;top:0;left:0;width:100%;height:100%;pointer-events:none;z-index:9999;overflow:hidden;';
        
        for (let i = 0; i < count; i++) {
            const confetti = document.createElement('div');
            confetti.className = 'confetti-piece';
            confetti.style.cssText = `
                position: absolute;
                width: ${Math.random() * 10 + 5}px;
                height: ${Math.random() * 10 + 5}px;
                background: ${colors[Math.floor(Math.random() * colors.length)]};
                left: ${Math.random() * 100}%;
                top: -20px;
                opacity: ${Math.random() * 0.5 + 0.5};
                transform: rotate(${Math.random() * 360}deg);
                animation: confettiFall ${Math.random() * 2 + 2}s linear forwards;
                animation-delay: ${Math.random() * 0.5}s;
            `;
            confettiContainer.appendChild(confetti);
        }
        
        document.body.appendChild(confettiContainer);
        
        setTimeout(() => confettiContainer.remove(), 4000);
    },
    
    showFloatingText: function(text, x, y, color = '#ffd700') {
        const floater = document.createElement('div');
        floater.className = 'floating-text';
        floater.textContent = text;
        floater.style.cssText = `
            position: fixed;
            left: ${x}px;
            top: ${y}px;
            color: ${color};
            font-size: 1.5rem;
            font-weight: bold;
            text-shadow: 0 0 10px ${color}, 0 2px 4px rgba(0,0,0,0.5);
            pointer-events: none;
            z-index: 9999;
            animation: floatUp 1.5s ease-out forwards;
        `;
        document.body.appendChild(floater);
        setTimeout(() => floater.remove(), 1500);
    },
    
    showRewardPopup: function(rewards) {
        this.playCoinSound();
        
        const popup = document.createElement('div');
        popup.className = 'reward-popup';
        popup.innerHTML = `
            <div class="reward-popup-content">
                <h3><i class="bi bi-gift-fill"></i> Rewards Earned!</h3>
                <div class="reward-items">
                    ${rewards.exp ? `<div class="reward-item exp"><i class="bi bi-lightning-fill"></i> +${rewards.exp} EXP</div>` : ''}
                    ${rewards.cash ? `<div class="reward-item cash"><i class="bi bi-coin"></i> +$${rewards.cash}</div>` : ''}
                    ${rewards.reputation ? `<div class="reward-item rep"><i class="bi bi-star-fill"></i> +${rewards.reputation} Rep</div>` : ''}
                </div>
            </div>
        `;
        popup.style.cssText = `
            position: fixed;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%) scale(0);
            background: linear-gradient(135deg, rgba(40, 40, 60, 0.98), rgba(20, 20, 40, 0.98));
            border: 3px solid #ffd700;
            border-radius: 15px;
            padding: 2rem;
            z-index: 10000;
            text-align: center;
            animation: popIn 0.4s ease-out forwards;
            box-shadow: 0 0 30px rgba(255, 215, 0, 0.5);
        `;
        document.body.appendChild(popup);
        
        setTimeout(() => {
            popup.style.animation = 'popOut 0.3s ease-in forwards';
            setTimeout(() => popup.remove(), 300);
        }, 2000);
    },
    
    showLevelUpCelebration: function(oldLevel, newLevel, discipline, title) {
        this.playLevelUpSound();
        this.createConfetti(document.body, 80);
        
        const overlay = document.createElement('div');
        overlay.className = 'levelup-overlay';
        overlay.innerHTML = `
            <div class="levelup-content">
                <div class="levelup-flash"></div>
                <div class="levelup-badge">
                    <i class="bi bi-trophy-fill"></i>
                </div>
                <h1 class="levelup-title">LEVEL UP!</h1>
                <div class="levelup-discipline">${discipline}</div>
                <div class="levelup-levels">
                    <span class="old-level">${oldLevel}</span>
                    <i class="bi bi-arrow-right-circle-fill levelup-arrow"></i>
                    <span class="new-level">${newLevel}</span>
                </div>
                <div class="levelup-new-title">${title}</div>
                <div class="levelup-rewards">
                    <div class="reward-badge"><i class="bi bi-plus-circle-fill"></i> +2 Stat Points</div>
                </div>
                <button class="levelup-continue" onclick="this.closest('.levelup-overlay').remove()">
                    <i class="bi bi-check-circle-fill"></i> Awesome!
                </button>
            </div>
        `;
        
        document.body.appendChild(overlay);
        
        setTimeout(() => {
            overlay.classList.add('active');
        }, 50);
    },
    
    incrementStreak: function() {
        this.streakCount++;
        sessionStorage.setItem('gameStreak', this.streakCount);
        
        if (this.streakCount >= 10) {
            this.showStreakBanner('UNSTOPPABLE!', '2x EXP Bonus!', '#ff6b6b');
            this.playComboSound();
        } else if (this.streakCount >= 5) {
            this.showStreakBanner('ON FIRE!', '1.5x EXP Bonus!', '#ff9500');
            this.playStreakSound(this.streakCount);
        } else if (this.streakCount >= 3) {
            this.showStreakBanner('Hot Streak!', '1.2x EXP Bonus!', '#4ecdc4');
            this.playStreakSound(this.streakCount);
        } else {
            this.playCorrectSound();
        }
        
        this.updateStreakDisplay();
        return this.streakCount;
    },
    
    resetStreak: function() {
        if (this.streakCount >= 3) {
            this.showFloatingText('Streak Lost!', window.innerWidth / 2, window.innerHeight / 2, '#ff6b6b');
        }
        this.streakCount = 0;
        sessionStorage.setItem('gameStreak', 0);
        this.playIncorrectSound();
        this.updateStreakDisplay();
    },
    
    showStreakBanner: function(title, subtitle, color) {
        const banner = document.createElement('div');
        banner.className = 'streak-banner';
        banner.innerHTML = `
            <div class="streak-icon"><i class="bi bi-fire"></i></div>
            <div class="streak-text">
                <div class="streak-title">${title}</div>
                <div class="streak-subtitle">${subtitle}</div>
            </div>
            <div class="streak-count">x${this.streakCount}</div>
        `;
        banner.style.cssText = `
            position: fixed;
            top: 80px;
            left: 50%;
            transform: translateX(-50%) translateY(-100px);
            background: linear-gradient(135deg, ${color}, ${color}aa);
            color: white;
            padding: 1rem 2rem;
            border-radius: 50px;
            display: flex;
            align-items: center;
            gap: 1rem;
            z-index: 9999;
            box-shadow: 0 5px 30px ${color}80;
            animation: slideDown 0.4s ease-out forwards;
        `;
        document.body.appendChild(banner);
        
        setTimeout(() => {
            banner.style.animation = 'slideUp 0.3s ease-in forwards';
            setTimeout(() => banner.remove(), 300);
        }, 2500);
    },
    
    updateStreakDisplay: function() {
        let streakEl = document.getElementById('streak-counter');
        if (!streakEl && this.streakCount > 0) {
            streakEl = document.createElement('div');
            streakEl.id = 'streak-counter';
            streakEl.style.cssText = `
                position: fixed;
                top: 70px;
                right: 20px;
                background: linear-gradient(135deg, #ff6b6b, #ff9500);
                color: white;
                padding: 0.5rem 1rem;
                border-radius: 20px;
                font-weight: bold;
                z-index: 1000;
                display: flex;
                align-items: center;
                gap: 0.5rem;
                box-shadow: 0 3px 15px rgba(255, 107, 107, 0.5);
            `;
            document.body.appendChild(streakEl);
        }
        
        if (streakEl) {
            if (this.streakCount > 0) {
                streakEl.innerHTML = `<i class="bi bi-fire"></i> ${this.streakCount}`;
                streakEl.style.display = 'flex';
            } else {
                streakEl.style.display = 'none';
            }
        }
    },
    
    loadStreakFromSession: function() {
        this.streakCount = parseInt(sessionStorage.getItem('gameStreak') || '0');
        this.updateStreakDisplay();
    },
    
    getStreakMultiplier: function() {
        if (this.streakCount >= 10) return 2.0;
        if (this.streakCount >= 5) return 1.5;
        if (this.streakCount >= 3) return 1.2;
        return 1.0;
    },
    
    animateStars: function(container, count) {
        const stars = container.querySelectorAll('.bi-star-fill, .bi-star');
        stars.forEach((star, index) => {
            if (index < count) {
                setTimeout(() => {
                    star.style.animation = 'starPop 0.4s ease-out';
                    this.playStarSound(index + 1);
                }, index * 300);
            }
        });
    },
    
    shakeElement: function(element) {
        element.style.animation = 'shake 0.5s ease-in-out';
        setTimeout(() => element.style.animation = '', 500);
    },
    
    pulseElement: function(element) {
        element.style.animation = 'pulse 0.6s ease-in-out';
        setTimeout(() => element.style.animation = '', 600);
    }
};

window.GameEffects = GameEffects;

GameEffects.init();

document.addEventListener('click', function() {
    if (GameEffects.audioContext && GameEffects.audioContext.state === 'suspended') {
        GameEffects.audioContext.resume();
    }
}, { once: true });
