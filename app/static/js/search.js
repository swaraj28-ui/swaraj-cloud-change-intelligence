// search.js - Handles natural language search queries

document.addEventListener('DOMContentLoaded', () => {
    const queryInput = document.getElementById('ai-search-query');
    const submitBtn = document.getElementById('btn-search-submit');
    const resultsWrapper = document.getElementById('search-results-wrapper');
    const tbody = document.getElementById('search-results-tbody');
    const placeholder = document.getElementById('search-placeholder');

    async function executeSearch() {
        const query = queryInput.value.trim();
        if (!query) return;

        // Toggle state
        submitBtn.disabled = true;
        const btnIcon = submitBtn.querySelector('i');
        if (btnIcon) {
            btnIcon.className = 'fa-solid fa-spinner fa-spin';
        }
        
        resultsWrapper.style.display = 'block';
        placeholder.style.display = 'none';
        
        tbody.innerHTML = `
            <tr>
                <td colspan="6" style="text-align: center; color: var(--text-muted); padding: 48px 0;">
                    <div class="spinner" style="margin: 0 auto 16px;"></div>
                    Gemini is parsing your intent and scanning cloud updates...
                </td>
            </tr>
        `;

        try {
            const response = await fetch(`/api/search?q=${encodeURIComponent(query)}`);
            if (!response.ok) throw new Error('Search failed');
            
            const results = await response.json();
            renderSearchResults(results);
        } catch (error) {
            console.error('Search error:', error);
            tbody.innerHTML = `
                <tr>
                    <td colspan="6" style="text-align: center; color: var(--accent-error); padding: 40px 0;">
                        <i class="fa-solid fa-triangle-exclamation" style="font-size: 1.5rem; margin-bottom: 8px;"></i>
                        <br>AI Search failed. Please check internet connection or model logs.
                    </td>
                </tr>
            `;
        } finally {
            submitBtn.disabled = false;
            if (btnIcon) {
                btnIcon.className = 'fa-solid fa-magnifying-glass';
            }
        }
    }

    function renderSearchResults(results) {
        if (results.length === 0) {
            tbody.innerHTML = `
                <tr>
                    <td colspan="6" style="text-align: center; color: var(--text-muted); padding: 48px 0;">
                        <i class="fa-solid fa-cloud-bolt" style="font-size: 2rem; margin-bottom: 12px; opacity: 0.3;"></i>
                        <p>No matching release updates found for your prompt.</p>
                    </td>
                </tr>
            `;
            return;
        }

        tbody.innerHTML = results.map(r => {
            const date = new Date(r.published_date).toLocaleDateString(undefined, {
                month: 'short',
                day: 'numeric',
                year: 'numeric'
            });
            
            const analysis = r.analysis || {};
            const severity = analysis.severity || 'Low';
            const category = analysis.category || 'Infrastructure';
            const score = analysis.impact_score || '-';

            return `
                <tr onclick="window.location.href='/release/${r.id}'">
                    <td style="color: var(--text-secondary); font-size: 0.9rem; white-space: nowrap;">${date}</td>
                    <td><span class="badge badge-service">${r.source_name}</span></td>
                    <td style="font-weight: 500; font-size: 0.95rem; color: var(--text-primary); max-width: 400px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;">
                        ${r.title}
                    </td>
                    <td><span class="badge badge-category">${category}</span></td>
                    <td style="text-align: center; font-weight: 600;">
                        <span style="color: ${getImpactColor(score)}">${score}</span>
                    </td>
                    <td><span class="badge badge-${severity.toLowerCase()}">${severity}</span></td>
                </tr>
            `;
        }).join('');
    }

    function getImpactColor(score) {
        if (score === '-') return 'var(--text-muted)';
        if (score >= 9) return 'var(--accent-critical)';
        if (score >= 7) return 'var(--accent-error)';
        if (score >= 5) return 'var(--accent-warning)';
        return 'var(--accent-success)';
    }

    // Submit Triggers
    submitBtn.addEventListener('click', executeSearch);
    queryInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            executeSearch();
        }
    });
});
