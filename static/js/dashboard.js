/**
 * Dashboard Logic - AI Call Center Analytics
 */

document.addEventListener('DOMContentLoaded', function() {
    // Charts are lazy-initialized the first time analytics-view is shown
    initUploadArea();
    initSidebar();
    initActionButtons();
});

// Track whether charts have been initialized
let chartsInitialized = false;

// Dynamic View Switching Logic
function switchView(viewId, element) {
    // Hide all views
    document.querySelectorAll('.view-content').forEach(view => {
        view.classList.add('hidden');
    });

    // Show selected view
    const targetView = document.getElementById(viewId);
    if (targetView) {
        targetView.classList.remove('hidden');
        if (typeof AOS !== 'undefined') AOS.refresh(); // Re-trigger animations
    }

    // Lazy-initialize charts the first time analytics-view is shown
    if (viewId === 'analytics-view' && !chartsInitialized) {
        chartsInitialized = true;
        // Small delay to ensure canvas is visible & has dimensions
        setTimeout(() => initCharts(), 50);
    }

    // Update Sidebar Active State
    document.querySelectorAll('.nav-item').forEach(item => {
        item.classList.remove('active');
    });

    if (element) {
        element.classList.add('active');
    } else {
        // Automatically find the sidebar link that points to this view
        const sidebarLink = document.querySelector(`a[onclick*="${viewId}"]`);
        if (sidebarLink) {
            sidebarLink.classList.add('active');
        }
    }
}

// Settings Toggle Logic
function toggleSetting(element, settingName) {
    const dot = element.querySelector('div');
    const isActive = dot.classList.contains('translate-x-6');
    
    if (isActive) {
        dot.classList.remove('translate-x-6');
        dot.classList.add('translate-x-0');
        element.classList.remove('bg-cyan-400/20');
        element.classList.add('bg-white/10');
        showNotification("Setting Updated", `${settingName} has been disabled.`);
    } else {
        dot.classList.remove('translate-x-0');
        dot.classList.add('translate-x-6');
        element.classList.remove('bg-white/10');
        element.classList.add('bg-cyan-400/20');
        showNotification("Setting Updated", `${settingName} is now active.`);
    }
}

// Action Buttons Logic
function initActionButtons() {
    const exportBtn = document.getElementById('exportBtn');
    const newBtn = document.getElementById('newAnalysisBtn');

    if (exportBtn) {
        exportBtn.addEventListener('click', () => {
            showNotification("Generating Intelligence Report", "Compiling neural insights into PDF...");
            setTimeout(() => {
                window.location.href = '/dashboard/export/';
            }, 1500);
        });
    }

    if (newBtn) {
        newBtn.addEventListener('click', () => {
            // Switch to upload view
            switchView('upload-view');
            
            // Find the upload sidebar item to highlight it
            const uploadNavItem = document.querySelector('a[onclick*="upload-view"]');
            if (uploadNavItem) {
                document.querySelectorAll('.nav-item').forEach(item => item.classList.remove('active'));
                uploadNavItem.classList.add('active');
            }

            // Simulate clearing current session
            const progressContainer = document.getElementById('progressContainer');
            if (progressContainer) progressContainer.classList.add('hidden');
            const progressBar = document.getElementById('progressBar');
            if (progressBar) progressBar.style.width = '0%';
            
            showNotification("Session Initialized", "Neural engine ready for new audio ingestion.");
        });
    }
}

// Initialize Chart.js (called lazily when analytics-view is first shown)
function initCharts() {
    const emotionEl = document.getElementById('emotionChart');
    const accuracyEl = document.getElementById('accuracyChart');
    const trendsEl = document.getElementById('trendsChart');

    if (!emotionEl || !accuracyEl || !trendsEl) {
        console.warn('Chart canvases not found – skipping chart init.');
        return;
    }

    const ctxEmotion = emotionEl.getContext('2d');
    const ctxAccuracy = accuracyEl.getContext('2d');
    const ctxTrends = trendsEl.getContext('2d');

    const charts = [];

    // Emotion Distribution (Pie)
    charts.push(new Chart(ctxEmotion, {
        type: 'doughnut',
        data: {
            labels: ['Happy', 'Angry', 'Neutral'],
            datasets: [{
                data: [45, 25, 30],
                backgroundColor: ['#22c55e', '#ef4444', '#6366f1'],
                borderColor: 'rgba(255, 255, 255, 0.05)',
                borderWidth: 2
            }]
        },
        options: {
            responsive: true,
            cutout: '70%',
            plugins: {
                legend: { position: 'bottom', labels: { color: '#94a3b8', usePointStyle: true } }
            }
        }
    }));

    // Prediction Accuracy (Bar)
    charts.push(new Chart(ctxAccuracy, {
        type: 'bar',
        data: {
            labels: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
            datasets: [{
                label: 'Accuracy %',
                data: [92, 95, 93, 97, 94, 91, 96],
                backgroundColor: '#00f2ff',
                borderRadius: 8
            }]
        },
        options: {
            responsive: true,
            scales: {
                y: { grid: { color: 'rgba(255, 255, 255, 0.05)' }, ticks: { color: '#64748b' } },
                x: { grid: { display: false }, ticks: { color: '#64748b' } }
            },
            plugins: { legend: { display: false } }
        }
    }));

    // Call Trends (Line)
    charts.push(new Chart(ctxTrends, {
        type: 'line',
        data: {
            labels: ['09:00', '12:00', '15:00', '18:00', '21:00'],
            datasets: [{
                label: 'Calls',
                data: [120, 250, 450, 300, 150],
                borderColor: '#6366f1',
                tension: 0.4,
                fill: true,
                backgroundColor: 'rgba(99, 102, 241, 0.1)'
            }]
        },
        options: {
            responsive: true,
            scales: {
                y: { display: false },
                x: { grid: { display: false }, ticks: { color: '#64748b' } }
            },
            plugins: { legend: { display: false } }
        }
    }));

    // Start real-time simulation
    animateCharts(charts);
}

function animateCharts(charts) {
    const pulses = {
        emotion: document.getElementById('emotionPulse'),
        accuracy: document.getElementById('accuracyPulse'),
        trends: document.getElementById('trendsPulse')
    };

    setInterval(() => {
        charts.forEach((chart, index) => {
            // Update Data Jitter
            chart.data.datasets.forEach(dataset => {
                dataset.data = dataset.data.map(val => {
                    const jitter = (Math.random() - 0.5) * 6;
                    return Math.max(10, Math.min(100, val + jitter));
                });
            });
            chart.update('none');

            // Update Pulse Counters
            const latency = (Math.random() * 5).toFixed(2);
            if (index === 0 && pulses.emotion) pulses.emotion.innerText = `${latency}ms`;
            if (index === 1 && pulses.accuracy) pulses.accuracy.innerText = `${latency}ms`;
            if (index === 2 && pulses.trends) pulses.trends.innerText = `${latency}ms`;
        });
    }, 1500);
}

// Drag & Drop Upload Simulation
function initUploadArea() {
    const uploadArea = document.getElementById('uploadArea');
    const fileInput = document.getElementById('fileInput');
    const ingestionAction = document.getElementById('ingestionAction');
    const startBtn = document.getElementById('startIngestionBtn');

    if (!uploadArea) return;

    uploadArea.addEventListener('click', () => fileInput.click());
    fileInput.addEventListener('change', () => {
        if (fileInput.files.length > 0) {
            showNotification("File Staged", `${fileInput.files[0].name} ready for neural processing.`);
            ingestionAction.classList.remove('hidden');
        }
    });

    if (startBtn) {
        startBtn.addEventListener('click', () => {
            ingestionAction.classList.add('hidden');
            simulateIngestion();
        });
    }
}

function simulateIngestion() {
    const container = document.getElementById('progressContainer');
    const bar = document.getElementById('progressBar');
    container.classList.remove('hidden');
    
    let progress = 0;
    const interval = setInterval(() => {
        progress += Math.random() * 8;
        if (progress >= 100) {
            progress = 100;
            clearInterval(interval);
            bar.style.width = '100%';
            
            setTimeout(() => {
                showNotification("Neural Analysis Complete", "Redirecting to Intelligence Reports...");
                setTimeout(() => {
                    switchView('results-view');
                }, 1200);
            }, 600);
        }
        bar.style.width = progress + '%';
    }, 300);
}

// Sidebar Navigation
function initSidebar() {
    const navItems = document.querySelectorAll('.nav-item');
    navItems.forEach(item => {
        item.addEventListener('click', () => {
            navItems.forEach(i => i.classList.remove('active'));
            item.classList.add('active');
        });
    });
}

function showNotification(title, message) {
    // Simple toast notification logic
    const toast = document.createElement('div');
    toast.className = 'fixed top-10 right-10 glass p-6 rounded-2xl border-cyan-400/30 z-[100] animate-fade-in shadow-2xl';
    toast.innerHTML = `
        <div class="flex items-center gap-4">
            <div class="w-10 h-10 rounded-xl bg-cyan-400/10 flex items-center justify-center">
                <i data-lucide="check-circle" class="text-cyan-400"></i>
            </div>
            <div>
                <h4 class="font-bold text-white uppercase tracking-wider text-sm">${title}</h4>
                <p class="text-gray-400 text-xs">${message}</p>
            </div>
        </div>
    `;
    document.body.appendChild(toast);
    lucide.createIcons();
    setTimeout(() => {
        toast.classList.add('opacity-0');
        setTimeout(() => toast.remove(), 600);
    }, 4000);
}
