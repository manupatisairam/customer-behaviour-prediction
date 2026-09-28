(function() {
    const canvas = document.createElement('canvas');
    const ctx = canvas.getContext('2d');
    document.body.appendChild(canvas);

    // Styling the canvas to be a full-screen overlay
    canvas.style.position = 'fixed';
    canvas.style.top = '0';
    canvas.style.left = '0';
    canvas.style.width = '100vw';
    canvas.style.height = '100vh';
    canvas.style.pointerEvents = 'none';
    canvas.style.zIndex = '10000'; // Above everything

    let particles = [];
    const colors = ['#00f2ff', '#6366f1', '#ffffff', '#a5b4fc'];

    function resize() {
        canvas.width = window.innerWidth;
        canvas.height = window.innerHeight;
    }

    window.addEventListener('resize', resize);
    resize();

    // Track mouse position and velocity
    let mouseX = 0;
    let mouseY = 0;
    let lastX = 0;
    let lastY = 0;

    window.addEventListener('mousemove', (e) => {
        mouseX = e.clientX;
        mouseY = e.clientY;
        
        // Calculate velocity for slightly dynamic particles
        const velocity = Math.sqrt(Math.pow(mouseX - lastX, 2) + Math.pow(mouseY - lastY, 2));
        
        // Create sprinkles based on movement
        const count = Math.min(Math.floor(velocity / 5) + 1, 5);
        
        for(let i = 0; i < count; i++) {
            particles.push(new Particle(mouseX, mouseY));
        }
        
        lastX = mouseX;
        lastY = mouseY;
    });

    class Particle {
        constructor(x, y) {
            this.x = x;
            this.y = y;
            // Random size for "sprinkle" look
            this.size = Math.random() * 2.5 + 0.5;
            // Random direction
            this.speedX = (Math.random() - 0.5) * 2;
            this.speedY = (Math.random() - 0.5) * 2;
            // Pick a themed color
            this.color = colors[Math.floor(Math.random() * colors.length)];
            // Initial opacity
            this.opacity = 1;
            // Fade rate
            this.fade = Math.random() * 0.015 + 0.005;
        }

        update() {
            this.x += this.speedX;
            this.y += this.speedY;
            this.opacity -= this.fade;
            if (this.size > 0.1) this.size -= 0.01;
        }

        draw() {
            ctx.save();
            ctx.globalAlpha = this.opacity;
            ctx.fillStyle = this.color;
            
            // Add a neon glow to each sprinkle
            ctx.shadowBlur = 8;
            ctx.shadowColor = this.color;
            
            ctx.beginPath();
            ctx.arc(this.x, this.y, this.size, 0, Math.PI * 2);
            ctx.fill();
            ctx.restore();
        }
    }

    function animate() {
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        
        for (let i = 0; i < particles.length; i++) {
            particles[i].update();
            particles[i].draw();
            
            // Remove dead particles
            if (particles[i].opacity <= 0) {
                particles.splice(i, 1);
                i--;
            }
        }
        
        // Performance cap
        if (particles.length > 300) {
            particles.shift();
        }
        
        requestAnimationFrame(animate);
    }

    animate();
})();
