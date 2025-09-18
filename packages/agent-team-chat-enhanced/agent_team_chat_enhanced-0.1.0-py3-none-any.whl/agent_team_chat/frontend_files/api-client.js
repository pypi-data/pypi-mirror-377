/**
 * API Client for Agent Team Chat Frontend
 *
 * This module handles all communication with the backend API bridge
 */

class ApiClient {
    constructor(baseUrl = 'http://localhost:5000/api') {
        this.baseUrl = baseUrl;
        this.isConnected = false;
        this.checkConnection();
    }

    async checkConnection() {
        try {
            const response = await fetch(`${this.baseUrl}/health`);
            const data = await response.json();
            this.isConnected = data.success;
            this.updateConnectionStatus();
        } catch (error) {
            console.error('Connection check failed:', error);
            this.isConnected = false;
            this.updateConnectionStatus();
        }
    }

    updateConnectionStatus() {
        const statusElement = document.querySelector('.connection-status');
        if (statusElement) {
            statusElement.textContent = this.isConnected ? 'Connected' : 'Disconnected';
            statusElement.className = `connection-status ${this.isConnected ? 'text-green-400' : 'text-red-400'}`;
        }

        // Update connection indicator
        const indicator = document.querySelector('.connection-indicator');
        if (indicator) {
            indicator.className = `w-2 h-2 rounded-full ${this.isConnected ? 'bg-green-400 online-pulse' : 'bg-red-400'}`;
        }
    }

    async request(endpoint, options = {}) {
        try {
            const response = await fetch(`${this.baseUrl}${endpoint}`, {
                headers: {
                    'Content-Type': 'application/json',
                    ...options.headers
                },
                ...options
            });

            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.error || `HTTP ${response.status}`);
            }

            return data;
        } catch (error) {
            console.error(`API request failed: ${endpoint}`, error);
            throw error;
        }
    }

    // Project Methods
    async getProjects() {
        return this.request('/projects');
    }

    async createProject(name, description = '') {
        return this.request('/projects', {
            method: 'POST',
            body: JSON.stringify({ name, description })
        });
    }

    async getProjectSummary(projectId) {
        return this.request(`/projects/${projectId}/summary`);
    }

    // Message Methods
    async getMessages(projectId, limit = 50) {
        return this.request(`/projects/${projectId}/messages?limit=${limit}`);
    }

    async sendMessage(projectId, content, agent = 'human_operator', role = 'user') {
        return this.request(`/projects/${projectId}/messages`, {
            method: 'POST',
            body: JSON.stringify({ content, agent, role })
        });
    }

    // Agent Methods
    async getAgentStatuses() {
        return this.request('/agents');
    }

    async updateAgentStatus(agentName, projectId, status, details = {}) {
        return this.request(`/agents/${agentName}/status`, {
            method: 'POST',
            body: JSON.stringify({ project_id: projectId, status, details })
        });
    }

    // Documentation Methods
    async searchDocs(query) {
        return this.request(`/docs/search?query=${encodeURIComponent(query)}`);
    }

    async addDocumentation(title, text, source = 'user') {
        return this.request('/docs', {
            method: 'POST',
            body: JSON.stringify({ title, text, source })
        });
    }

    // Image Methods
    async uploadImage(imageData, filename) {
        return this.request('/upload-image', {
            method: 'POST',
            body: JSON.stringify({ image_data: imageData, filename })
        });
    }
}

// Global API client instance
window.apiClient = new ApiClient();

// Enhanced frontend functions that use real API
window.loadProjects = async function() {
    try {
        const response = await window.apiClient.getProjects();

        if (!response.success) {
            throw new Error(response.error || 'Failed to load projects');
        }

        const projects = response.projects || [];
        const projectsList = document.getElementById('projects-list');
        projectsList.innerHTML = '';

        if (projects.length === 0) {
            projectsList.innerHTML = `
                <div class="text-center text-gray-400 py-4">
                    <i class="fas fa-folder-open text-2xl mb-2"></i>
                    <p class="text-sm">No projects yet</p>
                    <button onclick="createNewProject()" class="text-blue-400 hover:text-blue-300 text-sm mt-1">
                        Create your first project
                    </button>
                </div>
            `;
            return;
        }

        const colors = ['purple', 'cyan', 'orange', 'green', 'blue', 'pink', 'indigo'];
        const icons = [
            'fas fa-laptop-code', 'fas fa-server', 'fas fa-chart-bar',
            'fas fa-cogs', 'fas fa-shield-alt', 'fas fa-database',
            'fas fa-mobile-alt', 'fas fa-cloud', 'fas fa-robot'
        ];

        projects.forEach((project, index) => {
            const color = colors[index % colors.length];
            const icon = icons[index % icons.length];

            const projectElement = document.createElement('div');
            projectElement.className = `flex items-center p-3 rounded-lg hover:bg-white/10 cursor-pointer transition-colors ${window.currentProjectId === project.id ? 'bg-white/20' : ''}`;
            projectElement.onclick = () => window.selectProject(project.id, project.name, project.description);

            projectElement.innerHTML = `
                <div class="w-10 h-10 rounded-lg bg-${color}-500 flex items-center justify-center mr-3 shadow-md">
                    <i class="${icon} text-white"></i>
                </div>
                <div class="flex-1">
                    <div class="font-medium">${project.name}</div>
                    <div class="text-xs opacity-75">${project.description || 'No description'}</div>
                </div>
            `;

            projectsList.appendChild(projectElement);
        });

    } catch (error) {
        console.error('Failed to load projects:', error);
        window.showNotification('Failed to load projects: ' + error.message, 'error');

        // Show offline projects as fallback
        window.loadOfflineProjects();
    }
};

window.selectProject = async function(projectId, projectName, description) {
    window.currentProjectId = projectId;

    // Update UI
    document.getElementById('current-project-name').textContent = projectName;
    document.getElementById('project-description').textContent = description;
    document.getElementById('message-input').disabled = false;
    document.getElementById('send-button').disabled = false;

    // Update project selection in sidebar
    window.loadProjects();

    // Load messages for this project
    await window.loadMessages(projectId);

    window.showNotification(`Switched to ${projectName}`, 'success');
};

window.loadMessages = async function(projectId) {
    try {
        const response = await window.apiClient.getMessages(projectId);

        if (!response.success) {
            throw new Error(response.error || 'Failed to load messages');
        }

        const messages = response.messages || [];
        const messagesList = document.getElementById('messages-list');
        messagesList.innerHTML = '';

        if (messages.length === 0) {
            messagesList.innerHTML = `
                <div class="text-center text-gray-500 py-8">
                    <i class="fas fa-comments text-4xl mb-4 text-gray-400"></i>
                    <h3 class="text-lg font-semibold mb-2">Start the conversation</h3>
                    <p>Send the first message to get your AI agents involved!</p>
                </div>
            `;
            return;
        }

        // Sort messages by timestamp (oldest first)
        messages.sort((a, b) => a.timestamp - b.timestamp);

        messages.forEach(message => {
            window.addMessageToUI(message);
        });

        // Scroll to bottom
        window.scrollToBottom();

    } catch (error) {
        console.error('Failed to load messages:', error);
        window.showNotification('Failed to load messages: ' + error.message, 'error');

        // Show example messages as fallback
        window.loadExampleMessages();
    }
};

window.sendMessage = async function() {
    const messageInput = document.getElementById('message-input');
    const content = messageInput.value.trim();

    if (!content || !window.currentProjectId) return;

    // Disable input while sending
    messageInput.disabled = true;
    document.getElementById('send-button').disabled = true;

    try {
        // Send message to backend
        const response = await window.apiClient.sendMessage(window.currentProjectId, content);

        if (!response.success) {
            throw new Error(response.error || 'Failed to send message');
        }

        // Clear input
        messageInput.value = '';

        // Reload messages to get the new message
        await window.loadMessages(window.currentProjectId);

        window.showNotification('Message sent!', 'success');

    } catch (error) {
        console.error('Failed to send message:', error);
        window.showNotification('Failed to send message: ' + error.message, 'error');

        // Add message locally as fallback
        const message = {
            id: Date.now(),
            agent: 'human_operator',
            role: 'user',
            content: content,
            timestamp: Date.now(),
            is_agent: false
        };
        window.addMessageToUI(message);
        messageInput.value = '';
        window.scrollToBottom();
    } finally {
        // Re-enable input
        messageInput.disabled = false;
        document.getElementById('send-button').disabled = false;
        messageInput.focus();
    }
};

window.refreshAgents = async function() {
    try {
        const response = await window.apiClient.getAgentStatuses();

        if (!response.success) {
            throw new Error(response.error || 'Failed to get agent statuses');
        }

        const agents = response.agents || [];
        const agentsList = document.getElementById('agents-list');
        agentsList.innerHTML = '';

        if (agents.length === 0) {
            agentsList.innerHTML = `
                <div class="text-center text-gray-400 py-4">
                    <i class="fas fa-robot text-2xl mb-2"></i>
                    <p class="text-sm">No active agents</p>
                    <p class="text-xs opacity-75 mt-1">Send a message to wake them up!</p>
                </div>
            `;
            return;
        }

        agents.forEach(agent => {
            const agentElement = document.createElement('div');
            agentElement.className = 'flex items-center p-2 rounded-lg hover:bg-white/10 cursor-pointer transition-colors';

            const statusColor = {
                'active': 'bg-green-400',
                'idle': 'bg-yellow-400',
                'away': 'bg-gray-400'
            }[agent.status] || 'bg-gray-400';

            const lastSeenText = agent.last_seen
                ? window.formatTimestamp(agent.last_seen * 1000)
                : 'unknown';

            agentElement.innerHTML = `
                <div class="relative mr-3">
                    <div class="w-8 h-8 rounded-full bg-gradient-to-br from-purple-400 to-purple-600 flex items-center justify-center">
                        <i class="fas fa-robot text-white text-sm"></i>
                    </div>
                    <div class="absolute bottom-0 right-0 w-3 h-3 ${statusColor} rounded-full border-2 border-[#1e3a5f] ${agent.status === 'active' ? 'online-pulse' : ''}"></div>
                </div>
                <div class="flex-1">
                    <div class="font-medium text-sm">${agent.name}</div>
                    <div class="text-xs opacity-75">${agent.specialization || 'AI Agent'}</div>
                    <div class="text-xs opacity-60">Last seen: ${lastSeenText}</div>
                </div>
            `;

            agentsList.appendChild(agentElement);
        });

    } catch (error) {
        console.error('Failed to refresh agents:', error);
        // Fallback to example agents
        window.loadExampleAgents();
    }
};

window.createProject = async function() {
    const name = document.getElementById('new-project-name').value.trim();
    const description = document.getElementById('new-project-description').value.trim();

    if (!name) {
        window.showNotification('Project name is required', 'error');
        return;
    }

    try {
        const response = await window.apiClient.createProject(name, description);

        if (!response.success) {
            throw new Error(response.error || 'Failed to create project');
        }

        window.showNotification(`Project "${name}" created successfully!`, 'success');
        window.closeCreateProjectModal();
        window.loadProjects();

        // Auto-select the new project
        if (response.project_id) {
            setTimeout(() => {
                window.selectProject(response.project_id, name, description);
            }, 500);
        }

    } catch (error) {
        console.error('Failed to create project:', error);
        window.showNotification('Failed to create project: ' + error.message, 'error');
    }
};

window.searchDocs = async function(query) {
    if (query.length < 2) {
        document.getElementById('docs-results').innerHTML = '';
        return;
    }

    try {
        const response = await window.apiClient.searchDocs(query);

        if (!response.success) {
            throw new Error(response.error || 'Search failed');
        }

        const results = response.results || [];
        const resultsContainer = document.getElementById('docs-results');
        resultsContainer.innerHTML = '';

        if (results.length === 0) {
            resultsContainer.innerHTML = `
                <div class="text-center text-gray-500 py-4">
                    <i class="fas fa-search text-2xl mb-2"></i>
                    <p class="text-sm">No documentation found</p>
                    <p class="text-xs opacity-75">Try different keywords</p>
                </div>
            `;
            return;
        }

        results.forEach(result => {
            const resultElement = document.createElement('div');
            resultElement.className = 'p-3 border border-gray-200 rounded-lg mb-2 cursor-pointer hover:bg-gray-50 transition-colors';
            resultElement.innerHTML = `
                <div class="font-medium text-sm text-purple-700">${result.title}</div>
                <div class="text-xs text-gray-600 mt-1 line-clamp-3">${result.content.substring(0, 150)}...</div>
                <div class="text-xs text-gray-400 mt-2">Relevance: ${Math.round(result.score * 100)}%</div>
            `;

            resultElement.onclick = () => {
                // Insert reference into message input
                const messageInput = document.getElementById('message-input');
                const currentValue = messageInput.value;
                const reference = `📚 Ref: "${result.title}" - `;
                messageInput.value = currentValue + (currentValue ? ' ' : '') + reference;
                messageInput.focus();
            };

            resultsContainer.appendChild(resultElement);
        });

    } catch (error) {
        console.error('Documentation search failed:', error);
        document.getElementById('docs-results').innerHTML = `
            <div class="text-center text-red-500 py-4">
                <i class="fas fa-exclamation-triangle text-2xl mb-2"></i>
                <p class="text-sm">Search failed</p>
                <p class="text-xs">${error.message}</p>
            </div>
        `;
    }
};

window.showProjectSummary = async function() {
    if (!window.currentProjectId) {
        window.showNotification('Please select a project first', 'error');
        return;
    }

    window.showNotification('Generating project summary...', 'info');

    try {
        const response = await window.apiClient.getProjectSummary(window.currentProjectId);

        if (!response.success) {
            throw new Error(response.error || 'Failed to generate summary');
        }

        // Show summary in a modal or notification
        const summary = response.summary || 'No summary available';
        window.showNotification('Summary generated! Check console for details.', 'success');
        console.log('Project Summary:', summary);

    } catch (error) {
        console.error('Failed to generate summary:', error);
        window.showNotification('Failed to generate summary: ' + error.message, 'error');
    }
};

// Fallback functions for offline mode
window.loadOfflineProjects = function() {
    // Implementation from original code
    const projects = [
        { id: 1, name: "Frontend Development", description: "React/Vue components" },
        { id: 2, name: "Backend API", description: "REST API development" },
        { id: 3, name: "Data Analytics", description: "ML and data processing" },
        { id: 4, name: "DevOps Pipeline", description: "CI/CD and deployment" }
    ];

    // Use the same rendering logic as the real loadProjects function
    const projectsList = document.getElementById('projects-list');
    projectsList.innerHTML = '';

    projects.forEach((project, index) => {
        const colors = ['purple', 'cyan', 'orange', 'green'];
        const icons = ['fas fa-laptop-code', 'fas fa-server', 'fas fa-chart-bar', 'fas fa-cogs'];

        const projectElement = document.createElement('div');
        projectElement.className = `flex items-center p-3 rounded-lg hover:bg-white/10 cursor-pointer transition-colors ${window.currentProjectId === project.id ? 'bg-white/20' : ''}`;
        projectElement.onclick = () => window.selectProject(project.id, project.name, project.description);

        projectElement.innerHTML = `
            <div class="w-10 h-10 rounded-lg bg-${colors[index]}-500 flex items-center justify-center mr-3 shadow-md">
                <i class="${icons[index]} text-white"></i>
            </div>
            <div class="flex-1">
                <div class="font-medium">${project.name}</div>
                <div class="text-xs opacity-75">${project.description}</div>
            </div>
        `;

        projectsList.appendChild(projectElement);
    });
};

window.loadExampleMessages = function() {
    const messages = [
        {
            id: 1,
            agent: "APISpecialist",
            role: "assistant",
            content: "I've implemented the user authentication endpoints. The JWT token validation is working correctly.",
            timestamp: Date.now() - 300000,
            is_agent: true
        },
        {
            id: 2,
            agent: "human_operator",
            role: "user",
            content: "Great! Can you also add rate limiting to prevent brute force attacks?",
            timestamp: Date.now() - 180000,
            is_agent: false
        }
    ];

    const messagesList = document.getElementById('messages-list');
    messagesList.innerHTML = '';
    messages.forEach(window.addMessageToUI);
    window.scrollToBottom();
};

window.loadExampleAgents = function() {
    const agents = [
        { name: "APISpecialist", status: "active", specialization: "Backend APIs" },
        { name: "SecurityAuditor", status: "active", specialization: "Security Review" },
        { name: "UIExpert", status: "idle", specialization: "Frontend UI" }
    ];

    const agentsList = document.getElementById('agents-list');
    agentsList.innerHTML = '';

    agents.forEach(agent => {
        const agentElement = document.createElement('div');
        agentElement.className = 'flex items-center p-2 rounded-lg hover:bg-white/10 cursor-pointer transition-colors';

        const statusColor = {
            'active': 'bg-green-400',
            'idle': 'bg-yellow-400',
            'away': 'bg-gray-400'
        }[agent.status];

        agentElement.innerHTML = `
            <div class="relative mr-3">
                <div class="w-8 h-8 rounded-full bg-gradient-to-br from-purple-400 to-purple-600 flex items-center justify-center">
                    <i class="fas fa-robot text-white text-sm"></i>
                </div>
                <div class="absolute bottom-0 right-0 w-3 h-3 ${statusColor} rounded-full border-2 border-[#1e3a5f] ${agent.status === 'active' ? 'online-pulse' : ''}"></div>
            </div>
            <div class="flex-1">
                <div class="font-medium text-sm">${agent.name}</div>
                <div class="text-xs opacity-75">${agent.specialization}</div>
            </div>
        `;

        agentsList.appendChild(agentElement);
    });
};

// Start connection monitoring
setInterval(() => {
    window.apiClient.checkConnection();
}, 30000); // Check every 30 seconds