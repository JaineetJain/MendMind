document.addEventListener('DOMContentLoaded', function () {
    const moodForm = document.getElementById('mood-form');
    if (moodForm) {
        moodForm.addEventListener('submit', function (e) {
            const submitBtn = this.querySelector('button[type="submit"]');
            submitBtn.innerHTML = '⏳ Saving...';
            submitBtn.disabled = true;
        });
    }

    const chartCanvas = document.getElementById('moodChart');
    if (chartCanvas) {
        const chartCtx = chartCanvas.getContext('2d');
        const loadingEl = document.querySelector('.chart-loading');

        fetch('/mood-data')
            .then(response => response.json())
            .then(data => {
                loadingEl.style.display = 'none';

                const gradient = chartCtx.createLinearGradient(0, 0, 0, 400);
                gradient.addColorStop(0, 'rgba(52, 152, 219, 0.2)');
                gradient.addColorStop(1, 'rgba(52, 152, 219, 0.05)');

                new Chart(chartCtx, {
                    type: 'line',
                    data: {
                        labels: data.dates,
                        datasets: [{
                            label: 'Mood Sentiment',
                            data: data.sentiments,
                            borderColor: '#3498db',
                            backgroundColor: gradient,
                            tension: 0.3,
                            fill: true,
                            pointBackgroundColor: function (context) {
                                const value = context.dataset.data[context.dataIndex];
                                if (value < -0.5) return '#e74c3c';
                                if (value < 0) return '#f39c12';
                                return '#2ecc71';
                            },
                            pointRadius: 6,
                            pointHoverRadius: 8,
                            pointBorderWidth: 2,
                            pointBorderColor: '#fff'
                        }]
                    },
                    options: {
                        responsive: true,
                        maintainAspectRatio: false,
                        animations: {
                            tension: {
                                duration: 1000,
                                easing: 'linear'
                            }
                        },
                        scales: {
                            y: {
                                min: -1,
                                max: 1,
                                ticks: {
                                    callback: function (value) {
                                        if (value === -1) return '😢 Very Negative';
                                        if (value === 0) return '😐 Neutral';
                                        if (value === 1) return '😊 Very Positive';
                                        return '';
                                    },
                                    font: { size: 12 }
                                },
                                grid: { color: 'rgba(0,0,0,0.05)' }
                            },
                            x: {
                                ticks: { maxRotation: 45, minRotation: 45, font: { size: 10 } },
                                grid: { display: false }
                            }
                        },
                        plugins: {
                            tooltip: {
                                callbacks: {
                                    label: function (context) {
                                        const value = context.parsed.y;
                                        if (value < -0.7) return '😭 Crisis';
                                        if (value < -0.3) return '😟 Negative';
                                        if (value < 0.3) return '😐 Neutral';
                                        return '😊 Positive';
                                    }
                                }
                            },
                            legend: { labels: { font: { size: 14 } } }
                        }
                    }
                });
            })
            .catch(error => {
                console.error('Error loading mood data:', error);
                loadingEl.textContent = '❌ Failed to load chart data';
            });
    }

    // Enhanced animation functions
    const animateEmojis = () => {
        document.querySelectorAll('.suggestion-emoji').forEach(emoji => {
            emoji.style.animationDelay = `${Math.random() * 2}s`;
        });
    };
    
    const animateOnScroll = () => {
        const elements = document.querySelectorAll('.entry-card, .suggestion-item');
        elements.forEach((el, index) => {
            el.style.animationDelay = `${0.1 * index}s`;
        });
    };
    
    const addHoverAnimations = () => {
        // Mood emoji hover animation
        document.querySelectorAll('.mood-emoji').forEach(emoji => {
            emoji.addEventListener('mouseenter', () => {
                emoji.style.animation = 'wiggle 0.5s ease';
                setTimeout(() => emoji.style.animation = '', 500);
            });
        });
        
        // Suggestion emoji hover animation
        document.querySelectorAll('.suggestion-emoji').forEach(emoji => {
            emoji.addEventListener('mouseenter', () => {
                emoji.style.animation = 'wiggle 0.5s ease, float 4s infinite ease-in-out';
                setTimeout(() => emoji.style.animation = 'float 4s infinite ease-in-out', 500);
            });
        });
    };
    
    const addRippleEffect = () => {
        document.querySelectorAll('.ripple').forEach(button => {
            button.addEventListener('click', function(e) {
                const circle = document.createElement('span');
                circle.classList.add('ripple-effect');
                
                const diameter = Math.max(this.clientWidth, this.clientHeight);
                const radius = diameter / 2;
                
                circle.style.width = circle.style.height = `${diameter}px`;
                circle.style.left = `${e.clientX - (this.offsetLeft + radius)}px`;
                circle.style.top = `${e.clientY - (this.offsetTop + radius)}px`;
                circle.style.animation = 'ripple 1s ease-out';
                
                this.appendChild(circle);
                
                setTimeout(() => circle.remove(), 1000);
            });
        });
    };
    
    // Initialize all animations
    animateEmojis();
    animateOnScroll();
    addHoverAnimations();
    addRippleEffect();

    // Empty state animation
    if (document.querySelector('.empty-state')) {
        const emptyEmoji = document.querySelector('.empty-emoji');
        if (emptyEmoji) {
            setTimeout(() => {
                emptyEmoji.classList.add('animate__tada');
            }, 1000);
        }
    }
});