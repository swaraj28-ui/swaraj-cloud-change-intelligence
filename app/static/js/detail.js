// detail.js - Controls the release note detail view actions

document.addEventListener('DOMContentLoaded', () => {
    const releaseId = document.getElementById('btn-reanalyze').getAttribute('data-id');
    
    // Elements
    const reanalyzeBtn = document.getElementById('btn-reanalyze');
    const copyBtn = document.getElementById('btn-copy-social');
    const regenSocialBtn = document.getElementById('btn-regenerate-social');
    const socialBox = document.getElementById('social-content-output');
    const charCounter = document.getElementById('char-count');
    const socialTabs = document.querySelectorAll('.social-tab');
    
    let generatedPosts = null;
    let activeTab = 'twitter'; // default

    // Fetch and populate social shares
    async function fetchSocialPosts(forceRegen = false) {
        socialBox.innerText = 'Generating custom draft copy...';
        try {
            const response = await fetch('/api/generate-post', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ release_id: parseInt(releaseId), force: forceRegen })
            });
            
            if (!response.ok) throw new Error('Failed to generate shares');
            generatedPosts = await response.json();
            
            updateSocialTabContent();
        } catch (error) {
            console.error('Error generating social updates:', error);
            socialBox.innerText = 'Failed to generate promotional posts. Try clicking Regenerate.';
        }
    }

    function updateSocialTabContent() {
        if (!generatedPosts) return;
        
        let content = '';
        if (activeTab === 'twitter') {
            content = generatedPosts.twitter_post || '';
        } else if (activeTab === 'linkedin') {
            content = generatedPosts.linkedin_post || '';
        } else if (activeTab === 'blog') {
            content = generatedPosts.blog_summary || '';
        }
        
        socialBox.innerText = content;
        charCounter.innerText = `${content.length} characters`;
    }

    // Tab switcher
    socialTabs.forEach(tab => {
        tab.addEventListener('click', () => {
            socialTabs.forEach(t => t.classList.remove('active'));
            tab.classList.add('active');
            activeTab = tab.getAttribute('data-tab');
            updateSocialTabContent();
        });
    });

    // Copy Content
    copyBtn.addEventListener('click', async () => {
        const text = socialBox.innerText;
        if (!text || text.startsWith('Generating') || text.startsWith('Failed')) return;
        
        try {
            await navigator.clipboard.writeText(text);
            const originalHTML = copyBtn.innerHTML;
            copyBtn.innerHTML = '<i class="fa-solid fa-check"></i> Copied!';
            setTimeout(() => {
                copyBtn.innerHTML = originalHTML;
            }, 2000);
        } catch (err) {
            console.error('Clipboard copy failed:', err);
            alert('Unable to auto-copy to clipboard.');
        }
    });

    // Manual Re-analysis Trigger
    reanalyzeBtn.addEventListener('click', async () => {
        const icon = reanalyzeBtn.querySelector('i');
        reanalyzeBtn.disabled = true;
        if (icon) icon.classList.add('fa-spin');
        
        try {
            const response = await fetch('/api/analyze', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ release_id: parseInt(releaseId) })
            });
            
            const result = await response.json();
            if (result.success) {
                // Instantly reload to display newly calculated stats
                window.location.reload();
            } else {
                alert('Analysis failed: ' + result.error);
            }
        } catch (err) {
            console.error(err);
            alert('Failed to connect to analysis server.');
        } finally {
            reanalyzeBtn.disabled = false;
            if (icon) icon.classList.remove('fa-spin');
        }
    });

    // Regenerate Social trigger
    regenSocialBtn.addEventListener('click', () => {
        fetchSocialPosts(true);
    });

    // Initial Load
    fetchSocialPosts();
});
