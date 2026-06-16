// settings.js - Dynamically manages ingestion sources and alerts routing rules

document.addEventListener('DOMContentLoaded', () => {
    // Sources Elements
    const sourcesContainer = document.getElementById('sources-list-container');
    const feedNameInput = document.getElementById('feed-name');
    const feedUrlInput = document.getElementById('feed-url');
    const addSourceBtn = document.getElementById('btn-add-source');

    // Rules Elements
    const rulesContainer = document.getElementById('rules-list-container');
    const ruleNameInput = document.getElementById('rule-name');
    const ruleTypeSelect = document.getElementById('rule-cond-type');
    const ruleValInput = document.getElementById('rule-cond-value');
    const ruleChannelSelect = document.getElementById('rule-channel');
    const ruleRecipInput = document.getElementById('rule-recipient');
    const addRuleBtn = document.getElementById('btn-add-rule');

    // ----------------------------------------------------
    // INGESTION SOURCES SECTION
    // ----------------------------------------------------

    async function loadSources() {
        sourcesContainer.innerHTML = '<div class="spinner" style="margin: 20px auto;"></div>';
        try {
            const response = await fetch('/api/settings/sources');
            const sources = await response.json();
            
            if (sources.length === 0) {
                sourcesContainer.innerHTML = '<p style="color: var(--text-muted); text-align: center; padding: 20px;">No feed sources configured.</p>';
                return;
            }

            sourcesContainer.innerHTML = sources.map(s => {
                const checked = s.is_active ? 'checked' : '';
                return `
                    <div class="source-item">
                        <div class="item-info">
                            <h4>${s.name}</h4>
                            <p style="word-break: break-all;">${s.feed_url}</p>
                            <p style="font-size: 0.75rem; margin-top: 4px;">Last run: ${s.last_fetched_at ? new Date(s.last_fetched_at).toLocaleString() : 'Never'}</p>
                        </div>
                        <div style="display: flex; align-items: center; gap: 16px;">
                            <label class="switch">
                                <input type="checkbox" class="source-toggle" data-id="${s.id}" ${checked}>
                                <span class="slider"></span>
                            </label>
                            <button class="delete-icon-btn btn-delete-source" data-id="${s.id}">
                                <i class="fa-solid fa-trash-can"></i>
                            </button>
                        </div>
                    </div>
                `;
            }).join('');

            // Register event listeners
            document.querySelectorAll('.source-toggle').forEach(t => {
                t.addEventListener('change', async (e) => {
                    const id = e.target.getAttribute('data-id');
                    const is_active = e.target.checked;
                    await updateSourceState(id, { is_active });
                });
            });

            document.querySelectorAll('.btn-delete-source').forEach(b => {
                b.addEventListener('click', async (e) => {
                    const id = e.currentTarget.getAttribute('data-id');
                    if (confirm('Are you sure you want to delete this ingestion source?')) {
                        await deleteSource(id);
                    }
                });
            });

        } catch (err) {
            console.error(err);
            sourcesContainer.innerHTML = '<p style="color: var(--accent-error);">Error loading feed sources.</p>';
        }
    }

    async function updateSourceState(id, data) {
        try {
            await fetch('/api/settings/sources', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ id: parseInt(id), ...data })
            });
        } catch (err) {
            console.error('Failed to toggle source:', err);
        }
    }

    async function deleteSource(id) {
        try {
            const r = await fetch(`/api/settings/sources/${id}`, { method: 'DELETE' });
            if (r.ok) loadSources();
        } catch (err) {
            console.error(err);
        }
    }

    addSourceBtn.addEventListener('click', async () => {
        const name = feedNameInput.value.trim();
        const feed_url = feedUrlInput.value.trim();
        if (!name || !feed_url) {
            alert('Please fill out both feed source fields.');
            return;
        }

        try {
            const response = await fetch('/api/settings/sources', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ name, feed_url })
            });
            if (response.ok) {
                feedNameInput.value = '';
                feedUrlInput.value = '';
                loadSources();
            } else {
                const res = await response.json();
                alert('Failed: ' + res.error);
            }
        } catch (err) {
            console.error(err);
        }
    });

    // ----------------------------------------------------
    // NOTIFICATION RULES SECTION
    // ----------------------------------------------------

    async function loadRules() {
        rulesContainer.innerHTML = '<div class="spinner" style="margin: 20px auto;"></div>';
        try {
            const response = await fetch('/api/settings/notifications');
            const rules = await response.json();
            
            if (rules.length === 0) {
                rulesContainer.innerHTML = '<p style="color: var(--text-muted); text-align: center; padding: 20px;">No alert routing rules created.</p>';
                return;
            }

            rulesContainer.innerHTML = rules.map(r => {
                const checked = r.is_active ? 'checked' : '';
                const displayChannel = r.delivery_channel === 'slack' ? 'Slack Webhook' : 'Email Alert';
                const condSymbol = r.condition_type === 'impact_score' ? '>=' : '=';
                return `
                    <div class="rule-item">
                        <div class="item-info">
                            <h4>${r.rule_name}</h4>
                            <p><strong>Route:</strong> ${displayChannel} to <span style="font-family: monospace;">${r.recipient.substring(0, 40)}...</span></p>
                            <p style="margin-top: 4px; font-size: 0.75rem;"><strong>Trigger:</strong> ${r.condition_type} ${condSymbol} ${r.condition_value}</p>
                        </div>
                        <div style="display: flex; align-items: center; gap: 16px;">
                            <label class="switch">
                                <input type="checkbox" class="rule-toggle" data-id="${r.id}" ${checked}>
                                <span class="slider"></span>
                            </label>
                            <button class="delete-icon-btn btn-delete-rule" data-id="${r.id}">
                                <i class="fa-solid fa-trash-can"></i>
                            </button>
                        </div>
                    </div>
                `;
            }).join('');

            // Register event listeners
            document.querySelectorAll('.rule-toggle').forEach(t => {
                t.addEventListener('change', async (e) => {
                    const id = e.target.getAttribute('data-id');
                    const is_active = e.target.checked;
                    await updateRuleState(id, { is_active });
                });
            });

            document.querySelectorAll('.btn-delete-rule').forEach(b => {
                b.addEventListener('click', async (e) => {
                    const id = e.currentTarget.getAttribute('data-id');
                    if (confirm('Are you sure you want to delete this alert rule?')) {
                        await deleteRule(id);
                    }
                });
            });

        } catch (err) {
            console.error(err);
            rulesContainer.innerHTML = '<p style="color: var(--accent-error);">Error loading alert rules.</p>';
        }
    }

    async function updateRuleState(id, data) {
        try {
            await fetch('/api/settings/notifications', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ id: parseInt(id), ...data })
            });
        } catch (err) {
            console.error('Failed to toggle rule:', err);
        }
    }

    async function deleteRule(id) {
        try {
            const r = await fetch(`/api/settings/notifications/${id}`, { method: 'DELETE' });
            if (r.ok) loadRules();
        } catch (err) {
            console.error(err);
        }
    }

    addRuleBtn.addEventListener('click', async () => {
        const rule_name = ruleNameInput.value.trim();
        const condition_type = ruleTypeSelect.value;
        const condition_value = ruleValInput.value.trim();
        const delivery_channel = ruleChannelSelect.value;
        const recipient = ruleRecipInput.value.trim();
        
        if (!rule_name || !condition_value || !recipient) {
            alert('Please fill out all rule fields.');
            return;
        }

        try {
            const response = await fetch('/api/settings/notifications', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    rule_name,
                    condition_type,
                    condition_value,
                    delivery_channel,
                    recipient
                })
            });
            if (response.ok) {
                ruleNameInput.value = '';
                ruleValInput.value = '';
                ruleRecipInput.value = '';
                loadRules();
            } else {
                const res = await response.json();
                alert('Failed: ' + res.error);
            }
        } catch (err) {
            console.error(err);
        }
    });

    // Initialize Page
    loadSources();
    loadRules();
});
