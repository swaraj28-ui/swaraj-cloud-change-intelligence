// analytics.js - Controls Chart.js rendering on the Trend Analytics view

document.addEventListener('DOMContentLoaded', async () => {
    // Config Chart Defaults for Dark Mode
    Chart.defaults.color = '#9CA3AF';
    Chart.defaults.borderColor = 'rgba(255, 255, 255, 0.05)';
    Chart.defaults.font.family = "'Inter', sans-serif";

    try {
        const response = await fetch('/api/releases');
        if (!response.ok) throw new Error('Failed to fetch analytics payload');
        
        const data = await response.json();
        
        buildSourceChart(data);
        buildCategoryChart(data);
        buildTimelineChart(data);
        
    } catch (err) {
        console.error('Analytics load error:', err);
    }

    function buildSourceChart(releases) {
        const counts = {};
        releases.forEach(r => {
            counts[r.source_name] = (counts[r.source_name] || 0) + 1;
        });

        const ctx = document.getElementById('chart-sources').getContext('2d');
        new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: Object.keys(counts),
                datasets: [{
                    data: Object.values(counts),
                    backgroundColor: [
                        '#6366F1', // Indigo
                        '#3B82F6', // Blue
                        '#10B981', // Emerald
                        '#EC4899', // Pink
                        '#F59E0B'  // Amber
                    ],
                    borderWidth: 2,
                    borderColor: '#111726'
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom',
                        labels: { boxWidth: 12, padding: 16 }
                    }
                }
            }
        });
    }

    function buildCategoryChart(releases) {
        const counts = {};
        releases.forEach(r => {
            const cat = (r.analysis && r.analysis.category) || 'Infrastructure';
            counts[cat] = (counts[cat] || 0) + 1;
        });

        const sortedKeys = Object.keys(counts).sort((a, b) => counts[b] - counts[a]);
        const values = sortedKeys.map(k => counts[k]);

        const ctx = document.getElementById('chart-categories').getContext('2d');
        new Chart(ctx, {
            type: 'bar',
            data: {
                labels: sortedKeys,
                datasets: [{
                    label: 'Count of Updates',
                    data: values,
                    backgroundColor: 'rgba(99, 102, 241, 0.85)',
                    hoverBackgroundColor: '#6366F1',
                    borderRadius: 4
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { display: false }
                },
                scales: {
                    x: { grid: { display: false } },
                    y: { beginAtZero: true }
                }
            }
        });
    }

    function buildTimelineChart(releases) {
        // Group by Year-Month
        const counts = {};
        releases.forEach(r => {
            const date = new Date(r.published_date);
            const key = date.toLocaleDateString(undefined, { month: 'short', year: 'numeric' });
            counts[key] = (counts[key] || 0) + 1;
        });

        // Sort chronological (simplified by assuming the list is sorted desc, so reverse it)
        const keys = Object.keys(counts).reverse();
        const values = keys.map(k => counts[k]);

        const ctx = document.getElementById('chart-timeline').getContext('2d');
        new Chart(ctx, {
            type: 'line',
            data: {
                labels: keys,
                datasets: [{
                    label: 'Updates Ingested',
                    data: values,
                    borderColor: '#10B981',
                    backgroundColor: 'rgba(16, 185, 129, 0.1)',
                    borderWidth: 3,
                    fill: true,
                    tension: 0.3,
                    pointBackgroundColor: '#10B981'
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { display: false }
                },
                scales: {
                    x: { grid: { display: false } },
                    y: { beginAtZero: true, ticks: { precision: 0 } }
                }
            }
        });
    }
});
