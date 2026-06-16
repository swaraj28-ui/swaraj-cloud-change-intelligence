// dashboard.js - Handles live data loading, searching, and filtering on the dashboard

document.addEventListener('DOMContentLoaded', () => {
    // UI elements
    const tbody = document.getElementById('releases-tbody');
    const searchInput = document.getElementById('dashboard-search');
    const serviceFilter = document.getElementById('filter-service');
    const categoryFilter = document.getElementById('filter-category');
    const severityFilter = document.getElementById('filter-severity');
    const sortBySelect = document.getElementById('sort-by');
    
    let allReleases = [];

    // Fetch and render data
    async function loadReleases() {
        showLoadingState();
        try {
            // Build query parameters
            const params = new URLSearchParams();
            if (serviceFilter.value) params.append('source_id', serviceFilter.value);
            if (categoryFilter.value) params.append('category', categoryFilter.value);
            if (severityFilter.value) params.append('severity', severityFilter.value);
            if (sortBySelect.value) params.append('sort_by', sortBySelect.value);
            
            const response = await fetch(`/api/releases?${params.toString()}`);
            if (!response.ok) throw new Error('Failed to load release updates');
            
            allReleases = await response.json();
            renderTable(allReleases);
        } catch (error) {
            console.error('Error fetching releases:', error);
            tbody.innerHTML = `
                <tr>
                    <td colspan="6" style="text-align: center; color: var(--accent-error); padding: 40px 0;">
                        <i class="fa-solid fa-triangle-exclamation" style="font-size: 1.5rem; margin-bottom: 8px;"></i>
                        <br>Error loading release updates. Please try refreshing.
                    </td>
                </tr>
            `;
        }
    }

    function renderTable(releases) {
        const searchText = searchInput.value.toLowerCase().trim();
        
        // Filter locally by search text
        const filtered = releases.filter(r => {
            if (!searchText) return true;
            return r.title.toLowerCase().includes(searchText) || 
                   r.content.toLowerCase().includes(searchText) ||
                   (r.analysis && r.analysis.executive_summary.toLowerCase().includes(searchText));
        });

        if (filtered.length === 0) {
            tbody.innerHTML = `
                <tr>
                    <td colspan="6" style="text-align: center; color: var(--text-muted); padding: 40px 0;">
                        <i class="fa-regular fa-folder-open" style="font-size: 1.5rem; margin-bottom: 8px;"></i>
                        <br>No matching release updates found.
                    </td>
                </tr>
            `;
            return;
        }

        tbody.innerHTML = filtered.map(r => {
            const date = new Date(r.published_date).toLocaleDateString(undefined, {
                month: 'short',
                day: 'numeric',
                year: 'numeric'
            });
            
            const analysis = r.analysis || {};
            const severity = analysis.severity || 'Low';
            const category = analysis.category || 'Infrastructure';
            const impact = analysis.impact_score || '-';
            
            return `
                <tr onclick="window.location.href='/release/${r.id}'">
                    <td style="color: var(--text-secondary); font-size: 0.9rem; white-space: nowrap;">${date}</td>
                    <td><span class="badge badge-service">${r.source_name}</span></td>
                    <td style="font-weight: 500; font-size: 0.95rem; color: var(--text-primary); max-width: 400px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;">
                        ${r.title}
                    </td>
                    <td><span class="badge badge-category">${category}</span></td>
                    <td style="text-align: center; font-weight: 600;">
                        <span style="color: ${getImpactColor(impact)}">${impact}</span>
                    </td>
                    <td><span class="badge badge-${severity.toLowerCase()}">${severity}</span></td>
                </tr>
            `;
        }).join('');
    }

    function showLoadingState() {
        tbody.innerHTML = `
            <tr>
                <td colspan="6" style="text-align: center; color: var(--text-muted); padding: 48px 0;">
                    <div class="spinner" style="margin: 0 auto 16px;"></div>
                    Filtering release data feed...
                </td>
            </tr>
        `;
    }

    function getImpactColor(score) {
        if (score === '-') return 'var(--text-muted)';
        if (score >= 9) return 'var(--accent-critical)';
        if (score >= 7) return 'var(--accent-error)';
        if (score >= 5) return 'var(--accent-warning)';
        return 'var(--accent-success)';
    }

    // Event listeners
    searchInput.addEventListener('input', () => renderTable(allReleases));
    serviceFilter.addEventListener('change', loadReleases);
    categoryFilter.addEventListener('change', loadReleases);
    severityFilter.addEventListener('change', loadReleases);
    sortBySelect.addEventListener('change', loadReleases);

    // Initial Load
    loadReleases();
});
