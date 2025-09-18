DASHBOARD_HTML = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>GitHub Actions Analytics Dashboard</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/axios/dist/axios.min.js"></script>
    <style>
        .stat-card {
            @apply bg-white rounded-lg shadow-md p-6 hover:shadow-lg transition-shadow;
        }
        .loading {
            animation: pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite;
        }
        @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: .5; }
        }
        .chart-container {
            position: relative;
            height: 300px;
            width: 100%;
        }
    </style>
</head>
<body class="bg-gray-100">
    <!-- Header -->
    <header class="bg-gradient-to-r from-gray-800 to-gray-900 text-white">
        <div class="container mx-auto px-4 py-6">
            <div class="flex items-center justify-between">
                <div>
                    <h1 class="text-3xl font-bold">GitHub Actions Analytics</h1>
                    <p class="text-gray-300 mt-1">Organization Pipeline Intelligence</p>
                </div>
                <button onclick="refreshData()" class="bg-blue-600 hover:bg-blue-700 px-4 py-2 rounded-lg transition-colors">
                    🔄 Refresh
                </button>
            </div>
        </div>
    </header>

    <!-- Main Content -->
    <div class="container mx-auto px-4 py-8">
        <!-- Repository Overview Cards -->
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
            <div class="stat-card">
                <div class="flex items-center justify-between">
                    <div>
                        <p class="text-gray-500 text-sm">Total Repositories</p>
                        <p class="text-3xl font-bold text-gray-800" id="total-repos">-</p>
                    </div>
                    <span class="text-4xl">📦</span>
                </div>
            </div>
            
            <div class="stat-card">
                <div class="flex items-center justify-between">
                    <div>
                        <p class="text-gray-500 text-sm">Public / Private</p>
                        <p class="text-2xl font-bold">
                            <span class="text-green-600" id="public-repos">-</span> / 
                            <span class="text-blue-600" id="private-repos">-</span>
                        </p>
                    </div>
                    <span class="text-4xl">🔓</span>
                </div>
            </div>
            
            <div class="stat-card">
                <div class="flex items-center justify-between">
                    <div>
                        <p class="text-gray-500 text-sm">Archived</p>
                        <p class="text-3xl font-bold text-orange-600" id="archived-repos">-</p>
                    </div>
                    <span class="text-4xl">📚</span>
                </div>
            </div>
            
            <div class="stat-card">
                <div class="flex items-center justify-between">
                    <div>
                        <p class="text-gray-500 text-sm">Total Workflows</p>
                        <p class="text-3xl font-bold text-purple-600" id="total-workflows">-</p>
                    </div>
                    <span class="text-4xl">⚙️</span>
                </div>
            </div>
        </div>

        <!-- Charts Row -->
        <div class="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
            <!-- Language Distribution -->
            <div class="bg-white rounded-lg shadow-md p-6">
                <h2 class="text-xl font-bold mb-4 text-gray-800">Language Distribution</h2>
                <div class="chart-container">
                    <canvas id="languageChart"></canvas>
                </div>
            </div>
            
            <!-- Top Actions -->
            <div class="bg-white rounded-lg shadow-md p-6">
                <h2 class="text-xl font-bold mb-4 text-gray-800">Most Used Actions</h2>
                <div class="chart-container">
                    <canvas id="actionsChart"></canvas>
                </div>
            </div>
        </div>

        <!-- Action Usage Analysis -->
        <div class="bg-white rounded-lg shadow-md p-6 mb-8">
            <h2 class="text-xl font-bold mb-4 text-gray-800">Action Usage Analysis</h2>
            
            <div class="mb-4">
                <label class="block text-sm font-medium text-gray-700 mb-2">Search Action:</label>
                <div class="flex gap-2">
                    <input 
                        type="text" 
                        id="actionSearch" 
                        placeholder="e.g., actions/checkout"
                        class="flex-1 px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                    >
                    <button 
                        onclick="searchAction()"
                        class="bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700 transition-colors"
                    >
                        Search
                    </button>
                </div>
            </div>
            
            <div id="actionResults" class="hidden">
                <div class="grid grid-cols-1 md:grid-cols-2 gap-6 mt-6">
                    <div>
                        <h3 class="font-semibold mb-2 text-green-700">✅ Repositories Using (<span id="using-count">0</span>)</h3>
                        <div id="repos-using" class="max-h-64 overflow-y-auto bg-green-50 rounded p-3">
                            <!-- List will be populated -->
                        </div>
                    </div>
                    <div>
                        <h3 class="font-semibold mb-2 text-red-700">❌ Repositories Not Using (<span id="not-using-count">0</span>)</h3>
                        <div id="repos-not-using" class="max-h-64 overflow-y-auto bg-red-50 rounded p-3">
                            <!-- List will be populated -->
                        </div>
                    </div>
                </div>
                
                <div class="mt-4 p-4 bg-gray-100 rounded-lg">
                    <p class="text-sm text-gray-600">
                        Coverage: <span class="font-bold text-lg" id="coverage-percentage">0%</span>
                        <span id="coverage-badge" class="ml-2 px-2 py-1 rounded text-white text-xs"></span>
                    </p>
                </div>
            </div>
        </div>

        <!-- Tables Row -->
        <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <!-- Top Starred Repos -->
            <div class="bg-white rounded-lg shadow-md p-6">
                <div class="flex items-center justify-between mb-4">
                    <h2 class="text-xl font-bold text-gray-800">⭐ Top Starred Repositories</h2>
                    <span class="text-xs text-gray-500">Click repository names to visit</span>
                </div>
                <div class="overflow-x-auto">
                    <table class="w-full text-sm">
                        <thead class="text-xs text-gray-700 uppercase bg-gray-50">
                            <tr>
                                <th class="px-3 py-2 text-left">Repository</th>
                                <th class="px-3 py-2 text-center">Stars</th>
                                <th class="px-3 py-2 text-center">Forks</th>
                            </tr>
                        </thead>
                        <tbody id="topStarredTable" class="divide-y divide-gray-200">
                            <!-- Will be populated -->
                        </tbody>
                    </table>
                </div>
            </div>
            
            <!-- Top Forked Repos -->
            <div class="bg-white rounded-lg shadow-md p-6">
                <div class="flex items-center justify-between mb-4">
                    <h2 class="text-xl font-bold text-gray-800">🔀 Top Forked Repositories</h2>
                    <span class="text-xs text-gray-500">Click repository names to visit</span>
                </div>
                <div class="overflow-x-auto">
                    <table class="w-full text-sm">
                        <thead class="text-xs text-gray-700 uppercase bg-gray-50">
                            <tr>
                                <th class="px-3 py-2 text-left">Repository</th>
                                <th class="px-3 py-2 text-center">Forks</th>
                                <th class="px-3 py-2 text-center">Stars</th>
                            </tr>
                        </thead>
                        <tbody id="topForkedTable" class="divide-y divide-gray-200">
                            <!-- Will be populated -->
                        </tbody>
                    </table>
                </div>
            </div>
        </div>

        <!-- Runner Distribution -->
        <div class="bg-white rounded-lg shadow-md p-6 mt-8">
            <h2 class="text-xl font-bold mb-4 text-gray-800">🏃 Runner Distribution</h2>
            <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <!-- Runner Types Chart -->
                <div>
                    <h3 class="text-lg font-semibold mb-2 text-gray-700">Runner Types</h3>
                    <div class="chart-container" style="height: 250px;">
                        <canvas id="runnerChart"></canvas>
                    </div>
                </div>
                <!-- Top Runners Table -->
                <div>
                    <h3 class="text-lg font-semibold mb-2 text-gray-700">Most Used Runners</h3>
                    <div class="overflow-x-auto max-h-64">
                        <table class="w-full text-sm">
                            <thead class="text-xs text-gray-700 uppercase bg-gray-50 sticky top-0">
                                <tr>
                                    <th class="px-3 py-2 text-left">Runner</th>
                                    <th class="px-3 py-2 text-center">Usage</th>
                                    <th class="px-3 py-2 text-center">Workflows</th>
                                </tr>
                            </thead>
                            <tbody id="topRunnersTable" class="divide-y divide-gray-200">
                                <!-- Will be populated -->
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>
        </div>

        <!-- Action Adoption Trends -->
        <div class="bg-white rounded-lg shadow-md p-6 mt-8">
            <h2 class="text-xl font-bold mb-4 text-gray-800">📈 Action Adoption Trends</h2>
            <div id="adoptionTrends" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                <!-- Will be populated -->
            </div>
        </div>
    </div>

    <script>
        const API_URL = 'http://localhost:8000';
        let languageChart = null;
        let actionsChart = null;
        let runnerChart = null;

        // Initialize dashboard on load
        document.addEventListener('DOMContentLoaded', () => {
            refreshData();
        });

        async function refreshData() {
            showLoading();
            try {
                // Fetch dashboard data
                const response = await axios.get(`${API_URL}/api/dashboard`);
                const data = response.data;
                
                // Update stats
                updateStats(data.repository_stats);
                
                // Update charts
                updateLanguageChart(data.language_distribution);
                
                // Update tables
                updateTopStarredTable(data.top_starred);
                updateTopForkedTable(data.top_forked);
                
                // Update workflow stats
                document.getElementById('total-workflows').textContent = data.workflow_stats.total_workflows;
                
                // Fetch and update actions chart
                await updateActionsChart();
                
                // Fetch and update adoption trends
                await updateAdoptionTrends();
                
                // Fetch and update runner data
                await updateRunnerData();
                
            } catch (error) {
                console.error('Error fetching data:', error);
                showError('Failed to load dashboard data');
            } finally {
                hideLoading();
            }
        }

        function updateStats(stats) {
            document.getElementById('total-repos').textContent = stats.total_repos;
            document.getElementById('public-repos').textContent = stats.public_repos;
            document.getElementById('private-repos').textContent = stats.private_repos;
            document.getElementById('archived-repos').textContent = stats.archived_repos;
        }

        function updateLanguageChart(languages) {
            const ctx = document.getElementById('languageChart').getContext('2d');
            
            if (languageChart) {
                languageChart.destroy();
            }
            
            languageChart = new Chart(ctx, {
                type: 'doughnut',
                data: {
                    labels: languages.map(l => l.language),
                    datasets: [{
                        data: languages.map(l => l.count),
                        backgroundColor: [
                            '#3B82F6', '#10B981', '#F59E0B', '#EF4444', '#8B5CF6',
                            '#EC4899', '#06B6D4', '#84CC16', '#F97316', '#6366F1'
                        ]
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            position: 'right',
                            labels: {
                                padding: 10,
                                font: { size: 11 }
                            }
                        }
                    }
                }
            });
        }

        async function updateActionsChart() {
            try {
                const response = await axios.get(`${API_URL}/api/actions/all?limit=20`);
                const actions = response.data;
                
                const ctx = document.getElementById('actionsChart').getContext('2d');
                
                if (actionsChart) {
                    actionsChart.destroy();
                }
                
                actionsChart = new Chart(ctx, {
                    type: 'bar',
                    data: {
                        labels: actions.map(a => {
                            const name = a.action.split('@')[0].split('/').slice(-2).join('/');
                            return name.length > 20 ? name.substring(0, 20) + '...' : name;
                        }),
                        datasets: [{
                            label: 'Usage Count',
                            data: actions.map(a => a.usage_count),
                            backgroundColor: '#3B82F6',
                            borderColor: '#2563EB',
                            borderWidth: 1
                        }]
                    },
                    options: {
                        responsive: true,
                        maintainAspectRatio: false,
                        plugins: {
                            legend: { display: false }
                        },
                        scales: {
                            y: {
                                beginAtZero: true,
                                ticks: { precision: 0 }
                            },
                            x: {
                                ticks: {
                                    autoSkip: false,
                                    maxRotation: 45,
                                    minRotation: 45,
                                    font: { size: 10 }
                                }
                            }
                        }
                    }
                });
            } catch (error) {
                console.error('Error updating actions chart:', error);
            }
        }

        function updateTopStarredTable(repos) {
            const tbody = document.getElementById('topStarredTable');
            tbody.innerHTML = repos.map(repo => `
                <tr class="hover:bg-gray-50">
                    <td class="px-3 py-2 font-medium">
                        <a href="${repo.url}" target="_blank" class="text-blue-600 hover:text-blue-800 hover:underline flex items-center gap-1">
                            ${repo.name}
                            <svg class="w-3 h-3 opacity-50 hover:opacity-100" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14"></path>
                            </svg>
                        </a>
                    </td>
                    <td class="px-3 py-2 text-center">⭐ ${repo.stars}</td>
                    <td class="px-3 py-2 text-center">🔀 ${repo.forks}</td>
                </tr>
            `).join('');
        }

        function updateTopForkedTable(repos) {
            const tbody = document.getElementById('topForkedTable');
            tbody.innerHTML = repos.map(repo => `
                <tr class="hover:bg-gray-50">
                    <td class="px-3 py-2 font-medium">
                        <a href="${repo.url}" target="_blank" class="text-blue-600 hover:text-blue-800 hover:underline flex items-center gap-1">
                            ${repo.name}
                            <svg class="w-3 h-3 opacity-50 hover:opacity-100" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14"></path>
                            </svg>
                        </a>
                    </td>
                    <td class="px-3 py-2 text-center">🔀 ${repo.forks}</td>
                    <td class="px-3 py-2 text-center">⭐ ${repo.stars}</td>
                </tr>
            `).join('');
        }

        async function searchAction() {
            const actionName = document.getElementById('actionSearch').value.trim();
            if (!actionName) {
                alert('Please enter an action name');
                return;
            }
            
            try {
                // Usar query parameter em vez de path parameter para suportar /
                const response = await axios.get(`${API_URL}/api/actions/usage`, {
                    params: { action: actionName }
                });
                const data = response.data;
                
                // Show results section
                document.getElementById('actionResults').classList.remove('hidden');
                
                // Update using repos with clickable links to workflow files
                const usingList = document.getElementById('repos-using');
                usingList.innerHTML = data.repos_using.length > 0 
                    ? data.repos_using.map(repo => `
                        <div class="py-1 px-2 hover:bg-green-100 rounded flex items-center justify-between group">
                            <a href="${repo.url}" target="_blank" class="text-sm text-blue-600 hover:text-blue-800 hover:underline flex items-center gap-1">
                                <span>📦</span>
                                <span>${repo.name}</span>
                                <svg class="w-3 h-3 opacity-0 group-hover:opacity-100 transition-opacity" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14"></path>
                                </svg>
                            </a>
                            <span class="text-xs text-gray-500 opacity-0 group-hover:opacity-100 transition-opacity">View workflow</span>
                        </div>
                    `).join('')
                    : '<p class="text-gray-500 text-sm">No repositories using this action</p>';
                
                document.getElementById('using-count').textContent = data.repos_using.length;
                
                // Update not using repos with clickable links to repository
                const notUsingList = document.getElementById('repos-not-using');
                notUsingList.innerHTML = data.repos_not_using.length > 0
                    ? data.repos_not_using.map(repo => `
                        <div class="py-1 px-2 hover:bg-red-100 rounded flex items-center justify-between group">
                            <a href="${repo.url}" target="_blank" class="text-sm text-blue-600 hover:text-blue-800 hover:underline flex items-center gap-1">
                                <span>📦</span>
                                <span>${repo.name}</span>
                                <svg class="w-3 h-3 opacity-0 group-hover:opacity-100 transition-opacity" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14"></path>
                                </svg>
                            </a>
                            <span class="text-xs text-gray-500 opacity-0 group-hover:opacity-100 transition-opacity">View repo</span>
                        </div>
                    `).join('')
                    : '<p class="text-gray-500 text-sm">All repositories are using this action</p>';
                
                document.getElementById('not-using-count').textContent = data.repos_not_using.length;
                
                // Calculate and show coverage
                const totalRepos = data.repos_using.length + data.repos_not_using.length;
                const coverage = totalRepos > 0 ? (data.repos_using.length / totalRepos * 100).toFixed(1) : 0;
                
                document.getElementById('coverage-percentage').textContent = `${coverage}%`;
                
                const badge = document.getElementById('coverage-badge');
                if (coverage > 75) {
                    badge.textContent = 'High Coverage';
                    badge.className = 'ml-2 px-2 py-1 rounded text-white text-xs bg-green-600';
                } else if (coverage > 25) {
                    badge.textContent = 'Medium Coverage';
                    badge.className = 'ml-2 px-2 py-1 rounded text-white text-xs bg-yellow-600';
                } else {
                    badge.textContent = 'Low Coverage';
                    badge.className = 'ml-2 px-2 py-1 rounded text-white text-xs bg-red-600';
                }
                
            } catch (error) {
                console.error('Error searching action:', error);
                alert('Failed to search action. Please try again.');
            }
        }

        async function updateRunnerData() {
            try {
                // Get runner distribution
                const distResponse = await axios.get(`${API_URL}/api/runners/distribution`);
                const distribution = distResponse.data;
                
                // Update runner chart
                const ctx = document.getElementById('runnerChart').getContext('2d');
                
                if (runnerChart) {
                    runnerChart.destroy();
                }
                
                runnerChart = new Chart(ctx, {
                    type: 'pie',
                    data: {
                        labels: Object.keys(distribution.distribution).map(k => 
                            k.replace('_', ' ').charAt(0).toUpperCase() + k.slice(1).replace('_', ' ')
                        ),
                        datasets: [{
                            data: Object.values(distribution.distribution),
                            backgroundColor: [
                                '#FF9800', // Ubuntu - Orange
                                '#2196F3', // Windows - Blue  
                                '#9E9E9E', // macOS - Gray
                                '#4CAF50', // Self-hosted - Green
                                '#E91E63'  // Other - Pink
                            ]
                        }]
                    },
                    options: {
                        responsive: true,
                        maintainAspectRatio: false,
                        plugins: {
                            legend: {
                                position: 'right',
                                labels: {
                                    padding: 10,
                                    font: { size: 11 },
                                    generateLabels: function(chart) {
                                        const data = chart.data;
                                        if (data.labels.length && data.datasets.length) {
                                            return data.labels.map((label, i) => {
                                                const dataset = data.datasets[0];
                                                const value = dataset.data[i];
                                                const percentage = distribution.percentages[label.toLowerCase().replace(' ', '_')];
                                                return {
                                                    text: `${label} (${percentage}%)`,
                                                    fillStyle: dataset.backgroundColor[i],
                                                    hidden: false,
                                                    index: i
                                                };
                                            });
                                        }
                                        return [];
                                    }
                                }
                            },
                            tooltip: {
                                callbacks: {
                                    label: function(context) {
                                        const label = context.label || '';
                                        const value = context.parsed || 0;
                                        const key = label.toLowerCase().replace(' ', '_');
                                        const percentage = distribution.percentages[key];
                                        return `${label}: ${value} (${percentage}%)`;
                                    }
                                }
                            }
                        }
                    }
                });
                
                // Get top runners
                const runnersResponse = await axios.get(`${API_URL}/api/runners/usage`);
                const runners = runnersResponse.data;
                
                // Update top runners table
                const tbody = document.getElementById('topRunnersTable');
                tbody.innerHTML = runners.slice(0, 50).map(runner => `
                    <tr class="hover:bg-gray-50">
                        <td class="px-3 py-2 font-mono text-xs">${runner.runner}</td>
                        <td class="px-3 py-2 text-center">${runner.usage_count}</td>
                        <td class="px-3 py-2 text-center">${runner.workflow_count}</td>
                    </tr>
                `).join('');
                
            } catch (error) {
                console.error('Error updating runner data:', error);
            }
        }

        async function updateAdoptionTrends() {
            try {
                const response = await axios.get(`${API_URL}/api/trends/adoption`);
                const trends = response.data;
                
                const container = document.getElementById('adoptionTrends');
                container.innerHTML = trends.map(trend => {
                    // Extrair o nome da action e gerar o link
                    const actionName = trend.action.split('@')[0]; // Remove versão se houver
                    const actionShortName = actionName.split('/').slice(-2).join('/');
                    
                    // Gerar URL da action no GitHub
                    // Se for uma action do GitHub (ex: actions/checkout), usa direto
                    // Se for de terceiros (ex: docker/login), também funciona
                    const actionUrl = `https://github.com/${actionName}`;
                    
                    const badgeColor = trend.adoption_level === 'High' ? 'bg-green-100 text-green-800' :
                                     trend.adoption_level === 'Medium' ? 'bg-yellow-100 text-yellow-800' :
                                     'bg-red-100 text-red-800';
                    
                    return `
                        <div class="border rounded-lg p-4 hover:shadow-md transition-shadow">
                            <h3 class="font-semibold text-sm mb-2 truncate" title="${trend.action}">
                                <a href="${actionUrl}" target="_blank" class="text-blue-600 hover:text-blue-800 hover:underline flex items-center gap-1">
                                    <span>${actionShortName}</span>
                                    <svg class="w-3 h-3 opacity-50 hover:opacity-100 transition-opacity flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14"></path>
                                    </svg>
                                </a>
                            </h3>
                            <div class="space-y-2">
                                <div class="flex justify-between text-xs">
                                    <span class="text-gray-600">Coverage:</span>
                                    <span class="font-bold">${trend.coverage_percentage}%</span>
                                </div>
                                <div class="flex justify-between text-xs">
                                    <span class="text-gray-600">Using:</span>
                                    <span>${trend.repos_using}/${trend.total_repos}</span>
                                </div>
                                <div class="flex justify-between text-xs">
                                    <span class="text-gray-600">Total Uses:</span>
                                    <span>${trend.total_usage}</span>
                                </div>
                                <span class="inline-block px-2 py-1 text-xs rounded-full ${badgeColor}">
                                    ${trend.adoption_level}
                                </span>
                            </div>
                            <div class="mt-3 pt-3 border-t border-gray-100">
                                <button 
                                    onclick="searchActionFromTrend('${actionName}')"
                                    class="text-xs text-blue-600 hover:text-blue-800 hover:underline w-full text-center"
                                >
                                    View usage details →
                                </button>
                            </div>
                        </div>
                    `;
                }).join('');
            } catch (error) {
                console.error('Error updating adoption trends:', error);
            }
        }

        // Função helper para buscar action a partir do card de tendências
        function searchActionFromTrend(actionName) {
            document.getElementById('actionSearch').value = actionName;
            searchAction();
            // Scroll para a seção de análise
            document.getElementById('actionSearch').scrollIntoView({ behavior: 'smooth', block: 'center' });
        }

        function showLoading() {
            // Add loading states to elements
            document.querySelectorAll('.stat-card').forEach(card => {
                card.classList.add('loading');
            });
        }

        function hideLoading() {
            document.querySelectorAll('.stat-card').forEach(card => {
                card.classList.remove('loading');
            });
        }

        function showError(message) {
            console.error(message);
            // You can implement a toast notification here
        }
    </script>
</body>
</html>
'''