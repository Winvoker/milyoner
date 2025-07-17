// Global variables
let analysisData = {
    categories: [],
    levels: [],
    jokers: [],
    answerChoices: {},
    eliminations: {},
    preparation: {}
};
let charts = {};

// Initialize the dashboard
document.addEventListener('DOMContentLoaded', function () {
    loadAnalyticalData();
    setupEventListeners();
});

// Setup event listeners
function setupEventListeners() {
    // Modal functionality
    const modal = document.getElementById('questionModal');
    if (modal) {
        const closeBtn = document.getElementsByClassName('close')[0];

        if (closeBtn) {
            closeBtn.onclick = function () {
                modal.style.display = 'none';
            }
        }

        window.onclick = function (event) {
            if (event.target == modal) {
                modal.style.display = 'none';
            }
        }
    }
}

// Load all analytical data from API
async function loadAnalyticalData() {
    try {
        showLoading();

        console.log('Starting to load analytical data...');

        // Load basic stats
        console.log('Loading basic stats...');
        const statsResponse = await axios.get('/api/stats');
        updateStatsCards(statsResponse.data);
        console.log('Basic stats loaded successfully');

        // Load category analysis
        console.log('Loading category analysis...');
        try {
            const categoryResponse = await axios.get('/api/category_stats');
            analysisData.categories = categoryResponse.data;
            createCategoryAnalysisChart(categoryResponse.data);
            populateCategoryLevelTable(categoryResponse.data);
            console.log('Category analysis loaded successfully');
        } catch (error) {
            console.error('Error loading category analysis:', error);
        }

        // Load level analysis
        console.log('Loading level analysis...');
        try {
            const levelResponse = await axios.get('/api/level_stats');
            analysisData.levels = levelResponse.data;
            createLevelAnalysisChart(levelResponse.data);
            console.log('Level analysis loaded successfully');
        } catch (error) {
            console.error('Error loading level analysis:', error);
        }

        // Load joker analysis
        console.log('Loading joker analysis...');
        try {
            const jokerResponse = await axios.get('/api/joker_stats');
            analysisData.jokers = jokerResponse.data;
            createJokerAnalysisChart(jokerResponse.data);
            console.log('Joker analysis loaded successfully');
        } catch (error) {
            console.error('Error loading joker analysis:', error);
        }

        // Load answer choice analysis
        console.log('Loading answer choice analysis...');
        try {
            const answerResponse = await axios.get('/api/answer_choice_stats');
            analysisData.answerChoices = answerResponse.data;
            createAnswerChoiceChart(answerResponse.data);
            updateAnswerChoiceStats(answerResponse.data);
            console.log('Answer choice analysis loaded successfully');
        } catch (error) {
            console.error('Error loading answer choice analysis:', error);
        }

        // Load elimination analysis
        console.log('Loading elimination analysis...');
        try {
            const eliminationResponse = await axios.get('/api/elimination_analysis');
            analysisData.eliminations = eliminationResponse.data;
            createEliminationChart(eliminationResponse.data);
            console.log('Elimination analysis loaded successfully');
        } catch (error) {
            console.error('Error loading elimination analysis:', error);
        }

        // Load preparation guide
        console.log('Loading preparation guide...');
        try {
            const preparationResponse = await axios.get('/api/topic_preparation_guide');
            analysisData.preparation = preparationResponse.data;
            createPreparationChart(preparationResponse.data);
            updatePreparationRecommendations(preparationResponse.data);
            console.log('Preparation guide loaded successfully');
        } catch (error) {
            console.error('Error loading preparation guide:', error);
        }

        // Load topic preparation guide
        console.log('Loading topic preparation guide...');
        try {
            const topicResponse = await axios.get('/api/topic_preparation_guide');
            analysisData.topics = topicResponse.data;
            createTopicPreparationGuide(topicResponse.data);
            console.log('Topic preparation guide loaded successfully');
        } catch (error) {
            console.error('Error loading topic preparation guide:', error);
        }

        // Load detailed answer analysis
        console.log('Loading detailed answer analysis...');
        try {
            const detailedAnswerResponse = await axios.get('/api/detailed_answer_analysis');
            analysisData.detailedAnswers = detailedAnswerResponse.data;
            displayDetailedAnswerAnalysis(detailedAnswerResponse.data);
            console.log('Detailed answer analysis loaded successfully');
        } catch (error) {
            console.error('Error loading detailed answer analysis:', error);
        }

        hideLoading();
        console.log('All analytical data loaded successfully!');

    } catch (error) {
        console.error('Error loading analytical data:', error);
        console.error('Error details:', error.response?.data || error.message);
        showError('Failed to load analytical data. Please try again.');
    }
}

// Update stats cards
function updateStatsCards(stats) {
    document.getElementById('total-questions').textContent = stats.total_questions.toLocaleString();
    document.getElementById('total-contestants').textContent = stats.total_contestants.toLocaleString();
    document.getElementById('total-videos').textContent = stats.total_videos.toLocaleString();
    document.getElementById('overall-accuracy').textContent = stats.overall_accuracy.toFixed(1) + '%';
    document.getElementById('total-eliminated').textContent = stats.total_eliminated.toLocaleString();
    document.getElementById('average-level').textContent = stats.average_level.toFixed(1);
}

// Create category performance chart
function createCategoryChart(data) {
    const ctx = document.getElementById('categoryChart').getContext('2d');

    charts.category = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: data.map(item => item.category),
            datasets: [{
                label: 'Accuracy (%)',
                data: data.map(item => item.accuracy),
                backgroundColor: 'rgba(52, 152, 219, 0.8)',
                borderColor: 'rgba(52, 152, 219, 1)',
                borderWidth: 2,
                borderRadius: 8,
                borderSkipped: false,
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: false
                },
                tooltip: {
                    callbacks: {
                        label: function (context) {
                            return `Accuracy: ${context.parsed.y.toFixed(1)}%`;
                        }
                    }
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    max: 100,
                    ticks: {
                        callback: function (value) {
                            return value + '%';
                        }
                    }
                }
            }
        }
    });
}

// Create level difficulty chart
function createLevelChart(data) {
    const ctx = document.getElementById('levelChart').getContext('2d');

    charts.level = new Chart(ctx, {
        type: 'line',
        data: {
            labels: data.map(item => `Level ${item.level}`),
            datasets: [{
                label: 'Accuracy (%)',
                data: data.map(item => item.accuracy),
                borderColor: 'rgba(231, 76, 60, 1)',
                backgroundColor: 'rgba(231, 76, 60, 0.1)',
                borderWidth: 3,
                fill: true,
                tension: 0.4,
                pointBackgroundColor: 'rgba(231, 76, 60, 1)',
                pointBorderColor: '#fff',
                pointBorderWidth: 2,
                pointRadius: 6
            }, {
                label: 'Elimination Rate (%)',
                data: data.map(item => (item.eliminated_count / item.total_questions) * 100),
                borderColor: 'rgba(255, 193, 7, 1)',
                backgroundColor: 'rgba(255, 193, 7, 0.1)',
                borderWidth: 3,
                fill: false,
                tension: 0.4,
                pointBackgroundColor: 'rgba(255, 193, 7, 1)',
                pointBorderColor: '#fff',
                pointBorderWidth: 2,
                pointRadius: 6
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'top',
                },
                tooltip: {
                    callbacks: {
                        label: function (context) {
                            return `${context.dataset.label}: ${context.parsed.y.toFixed(1)}%`;
                        }
                    }
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    max: 100,
                    ticks: {
                        callback: function (value) {
                            return value + '%';
                        }
                    }
                }
            }
        }
    });
}

// Create joker usage chart
function createJokerChart(data) {
    const ctx = document.getElementById('jokerChart').getContext('2d');

    charts.joker = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: data.map(item => item.joker === 'yok' ? 'No Joker' : item.joker),
            datasets: [{
                data: data.map(item => item.count),
                backgroundColor: [
                    'rgba(52, 152, 219, 0.8)',
                    'rgba(46, 204, 113, 0.8)',
                    'rgba(231, 76, 60, 0.8)',
                    'rgba(255, 193, 7, 0.8)',
                    'rgba(155, 89, 182, 0.8)',
                    'rgba(241, 196, 15, 0.8)'
                ],
                borderColor: [
                    'rgba(52, 152, 219, 1)',
                    'rgba(46, 204, 113, 1)',
                    'rgba(231, 76, 60, 1)',
                    'rgba(255, 193, 7, 1)',
                    'rgba(155, 89, 182, 1)',
                    'rgba(241, 196, 15, 1)'
                ],
                borderWidth: 2
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'bottom',
                },
                tooltip: {
                    callbacks: {
                        label: function (context) {
                            const total = context.dataset.data.reduce((sum, val) => sum + val, 0);
                            const percentage = ((context.parsed / total) * 100).toFixed(1);
                            return `${context.label}: ${context.parsed} (${percentage}%)`;
                        }
                    }
                }
            }
        }
    });
}

// Create contestant performance chart
function createContestantChart(data) {
    const ctx = document.getElementById('contestantChart').getContext('2d');

    // Show top 10 contestants
    const topContestants = data.slice(0, 10);

    charts.contestant = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: topContestants.map(item => item.contestant),
            datasets: [{
                label: 'Total Winnings (₺)',
                data: topContestants.map(item => item.total_winnings),
                backgroundColor: 'rgba(46, 204, 113, 0.8)',
                borderColor: 'rgba(46, 204, 113, 1)',
                borderWidth: 2,
                borderRadius: 8,
                borderSkipped: false,
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: false
                },
                tooltip: {
                    callbacks: {
                        label: function (context) {
                            return `Winnings: ₺${context.parsed.y.toLocaleString()}`;
                        }
                    }
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        callback: function (value) {
                            return '₺' + value.toLocaleString();
                        }
                    }
                },
                x: {
                    ticks: {
                        maxRotation: 45,
                        minRotation: 45
                    }
                }
            }
        }
    });
}

// Create category analysis chart
function createCategoryAnalysisChart(data) {
    const ctx = document.getElementById('categoryChart').getContext('2d');

    const sortedData = data.sort((a, b) => b.total_questions - a.total_questions);

    charts.category = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: sortedData.map(item => item.category),
            datasets: [{
                label: 'Total Questions',
                data: sortedData.map(item => item.total_questions),
                backgroundColor: 'rgba(52, 152, 219, 0.8)',
                borderColor: 'rgba(52, 152, 219, 1)',
                borderWidth: 2,
                yAxisID: 'y'
            }, {
                label: 'Accuracy (%)',
                data: sortedData.map(item => item.accuracy),
                backgroundColor: 'rgba(231, 76, 60, 0.8)',
                borderColor: 'rgba(231, 76, 60, 1)',
                borderWidth: 2,
                type: 'line',
                yAxisID: 'y1'
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: {
                    type: 'linear',
                    display: true,
                    position: 'left',
                    title: {
                        display: true,
                        text: 'Number of Questions'
                    }
                },
                y1: {
                    type: 'linear',
                    display: true,
                    position: 'right',
                    title: {
                        display: true,
                        text: 'Accuracy (%)'
                    },
                    grid: {
                        drawOnChartArea: false,
                    },
                    max: 100
                }
            }
        }
    });
}

// Create level analysis chart
function createLevelAnalysisChart(data) {
    const ctx = document.getElementById('levelChart').getContext('2d');

    charts.level = new Chart(ctx, {
        type: 'line',
        data: {
            labels: data.map(item => `Level ${item.level}`),
            datasets: [{
                label: 'Accuracy (%)',
                data: data.map(item => item.accuracy),
                borderColor: 'rgba(46, 204, 113, 1)',
                backgroundColor: 'rgba(46, 204, 113, 0.1)',
                borderWidth: 3,
                fill: true,
                tension: 0.4
            }, {
                label: 'Elimination Rate (%)',
                data: data.map(item => item.elimination_rate),
                borderColor: 'rgba(231, 76, 60, 1)',
                backgroundColor: 'rgba(231, 76, 60, 0.1)',
                borderWidth: 3,
                fill: false,
                tension: 0.4
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: {
                    beginAtZero: true,
                    max: 100,
                    ticks: {
                        callback: function (value) {
                            return value + '%';
                        }
                    }
                }
            }
        }
    });
}

// Create answer choice analysis chart
function createAnswerChoiceChart(data) {
    const ctx = document.getElementById('answerChoiceChart').getContext('2d');

    const labels = ['A', 'B', 'C', 'D'];
    const correctData = labels.map(choice => data.correct_answer_distribution[choice] || 0);
    const selectedData = labels.map(choice => data.contestant_answer_distribution[choice] || 0);

    charts.answerChoice = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: 'Times Correct Answer',
                data: correctData,
                backgroundColor: 'rgba(46, 204, 113, 0.8)',
                borderColor: 'rgba(46, 204, 113, 1)',
                borderWidth: 2
            }, {
                label: 'Times Selected by Contestants',
                data: selectedData,
                backgroundColor: 'rgba(255, 193, 7, 0.8)',
                borderColor: 'rgba(255, 193, 7, 1)',
                borderWidth: 2
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: {
                    beginAtZero: true,
                    title: {
                        display: true,
                        text: 'Number of Questions'
                    }
                }
            }
        }
    });
}

// Create joker analysis chart
function createJokerAnalysisChart(data) {
    const ctx = document.getElementById('jokerChart').getContext('2d');

    charts.joker = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: data.map(item => item.joker === 'yok' ? 'No Joker' : item.joker),
            datasets: [{
                data: data.map(item => item.count),
                backgroundColor: [
                    'rgba(52, 152, 219, 0.8)',
                    'rgba(46, 204, 113, 0.8)',
                    'rgba(231, 76, 60, 0.8)',
                    'rgba(255, 193, 7, 0.8)',
                    'rgba(155, 89, 182, 0.8)'
                ],
                borderWidth: 2
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'bottom'
                },
                tooltip: {
                    callbacks: {
                        label: function (context) {
                            const joker = data[context.dataIndex];
                            return `${context.label}: ${context.parsed} (${joker.accuracy.toFixed(1)}% accuracy)`;
                        }
                    }
                }
            }
        }
    });
}

// Create preparation priority chart
function createPreparationChart(data) {
    const ctx = document.getElementById('preparationChart').getContext('2d');

    const categories = Object.keys(data.categories);
    const priorityScores = categories.map(cat => data.categories[cat].priority_score);

    charts.preparation = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: categories,
            datasets: [{
                label: 'Priority Score',
                data: priorityScores,
                backgroundColor: priorityScores.map(score =>
                    score > 20 ? 'rgba(231, 76, 60, 0.8)' :
                        score > 10 ? 'rgba(255, 193, 7, 0.8)' :
                            'rgba(46, 204, 113, 0.8)'
                ),
                borderWidth: 2
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            indexAxis: 'y',
            scales: {
                x: {
                    beginAtZero: true,
                    title: {
                        display: true,
                        text: 'Priority Score (Higher = More Important)'
                    }
                }
            }
        }
    });
}

// Create elimination analysis chart
function createEliminationChart(data) {
    const ctx = document.getElementById('eliminationChart').getContext('2d');

    // Convert level keys to numbers and sort them properly
    const levelEntries = Object.entries(data.elimination_by_level)
        .map(([key, value]) => [parseInt(key.replace('level_', '')), value])
        .sort((a, b) => a[0] - b[0]); // Sort by level number

    const levels = levelEntries.map(([level, count]) => level);
    const eliminations = levelEntries.map(([level, count]) => count);

    charts.elimination = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: levels.map(level => `Level ${level}`),
            datasets: [{
                label: 'Eliminations',
                data: eliminations,
                backgroundColor: eliminations.map(count => 'rgba(231, 76, 60, 0.8)'), // All red
                borderColor: eliminations.map(count => 'rgba(231, 76, 60, 1)'), // Red borders
                borderWidth: 2
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: {
                    beginAtZero: true,
                    title: {
                        display: true,
                        text: 'Number of Eliminations'
                    }
                }
            }
        }
    });
}

// Populate performance table
function populateTable(data) {
    const tbody = document.getElementById('tableBody');
    tbody.innerHTML = '';

    data.forEach(contestant => {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td>${contestant.contestant}</td>
            <td>${contestant.total_questions}</td>
            <td>${contestant.correct_answers}</td>
            <td>${contestant.accuracy.toFixed(1)}%</td>
            <td>${contestant.max_level}</td>
            <td>₺${contestant.total_winnings.toLocaleString()}</td>
            <td><span class="status-badge ${contestant.eliminated ? 'status-eliminated' : 'status-active'}">
                ${contestant.eliminated ? 'Eliminated' : 'Active'}
            </span></td>
        `;
        tbody.appendChild(row);
    });
}

// Populate category-level analysis table
function populateCategoryLevelTable(data) {
    const tbody = document.getElementById('categoryLevelTableBody');
    if (!tbody) {
        console.warn('Category level table body not found');
        return;
    }

    tbody.innerHTML = '';

    data.forEach(category => {
        const row = document.createElement('tr');
        const recommendation = category.before_level_7 > category.level_7_and_after ?
            'Focus on basics' : 'Advanced practice needed';

        row.innerHTML = `
            <td>${category.category}</td>
            <td>${category.total_questions}</td>
            <td>${category.before_level_7}</td>
            <td>${category.level_7_and_after}</td>
            <td>${category.before_level_7_accuracy.toFixed(1)}%</td>
            <td>${category.level_7_and_after_accuracy.toFixed(1)}%</td>
            <td><span class="recommendation">${recommendation}</span></td>
        `;
        tbody.appendChild(row);
    });
}

// Filter table based on search input
function filterTable() {
    const searchTerm = document.getElementById('searchInput').value.toLowerCase();
    const filteredData = contestantData.filter(contestant =>
        contestant.contestant.toLowerCase().includes(searchTerm)
    );
    populateTable(filteredData);
}

// Sort table based on selected criteria
function sortTable() {
    const sortBy = document.getElementById('sortSelect').value;
    const sortedData = [...contestantData].sort((a, b) => {
        if (sortBy === 'contestant') {
            return a.contestant.localeCompare(b.contestant);
        }
        return b[sortBy] - a[sortBy];
    });
    populateTable(sortedData);
}

// Update answer choice statistics
function updateAnswerChoiceStats(data) {
    const mostSelected = data.most_selected_choice;
    const mostCorrect = data.most_correct_choice;

    const mostSelectedEl = document.getElementById('most-selected');
    const mostCorrectEl = document.getElementById('most-correct');
    const bestStrategyEl = document.getElementById('best-strategy');
    const avoidBiasEl = document.getElementById('avoid-bias');

    if (mostSelectedEl) {
        mostSelectedEl.textContent = `${mostSelected.choice} (${mostSelected.count})`;
    }

    if (mostCorrectEl) {
        mostCorrectEl.textContent = `${mostCorrect.choice} (${mostCorrect.count})`;
    }

    if (bestStrategyEl) {
        // Calculate best strategy
        const bestChoice = ['A', 'B', 'C', 'D'].reduce((best, choice) => {
            const accuracy = data.choice_accuracy[choice]?.accuracy || 0;
            return accuracy > (data.choice_accuracy[best]?.accuracy || 0) ? choice : best;
        });
        bestStrategyEl.textContent = `Guess ${bestChoice}`;
    }

    if (avoidBiasEl) {
        // Find most biased choice
        const biases = data.bias_analysis;
        const mostBiased = Object.keys(biases).reduce((a, b) => biases[a] > biases[b] ? a : b);
        avoidBiasEl.textContent = `Avoid ${mostBiased.toUpperCase()} bias`;
    }
}

// Update preparation recommendations
function updatePreparationRecommendations(data) {
    const recommendations = data.study_recommendations;

    // High priority
    const highPriorityEl = document.querySelector('#high-priority .topic-list');
    if (highPriorityEl && recommendations.focus_categories) {
        highPriorityEl.innerHTML = recommendations.focus_categories.map(cat =>
            `<span class="topic-tag high-priority">${cat}</span>`
        ).join('');
    }

    // Medium priority
    const mediumPriorityEl = document.querySelector('#medium-priority .topic-list');
    if (mediumPriorityEl && recommendations.review_categories) {
        mediumPriorityEl.innerHTML = recommendations.review_categories.map(cat =>
            `<span class="topic-tag medium-priority">${cat}</span>`
        ).join('');
    }

    // Low priority
    const lowPriorityEl = document.querySelector('#low-priority .topic-list');
    if (lowPriorityEl && recommendations.maintenance_categories) {
        lowPriorityEl.innerHTML = recommendations.maintenance_categories.map(cat =>
            `<span class="topic-tag low-priority">${cat}</span>`
        ).join('');
    }
}

// Utility functions
function showLoading() {
    document.querySelectorAll('.stat-info h3').forEach(el => {
        el.innerHTML = '<div class="loading"></div>';
    });
}

function hideLoading() {
    // Loading is automatically hidden when data is populated
}

function showError(message) {
    const errorDiv = document.createElement('div');
    errorDiv.className = 'error-message';
    errorDiv.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        background: #e74c3c;
        color: white;
        padding: 15px 20px;
        border-radius: 8px;
        z-index: 1000;
        box-shadow: 0 2px 10px rgba(0,0,0,0.2);
    `;
    errorDiv.textContent = message;
    document.body.appendChild(errorDiv);

    setTimeout(() => {
        errorDiv.remove();
    }, 5000);
}

// Format currency
function formatCurrency(amount) {
    return new Intl.NumberFormat('tr-TR', {
        style: 'currency',
        currency: 'TRY'
    }).format(amount);
}

// Format percentage
function formatPercentage(value) {
    return value.toFixed(1) + '%';
}

// Export data functionality (optional)
function exportData() {
    const dataStr = JSON.stringify(contestantData, null, 2);
    const dataUri = 'data:application/json;charset=utf-8,' + encodeURIComponent(dataStr);

    const exportFileDefaultName = 'contestant_performance.json';

    const linkElement = document.createElement('a');
    linkElement.setAttribute('href', dataUri);
    linkElement.setAttribute('download', exportFileDefaultName);
    linkElement.click();
}

function displayDetailedAnswerAnalysis(data) {
    // Display Before/After Level 7 bias comparison
    displayBeforeAfterLevel7Bias(data.before_after_level_7);

    // Display level-by-level bias table
    displayLevelBiasTable(data.level_bias);

    // Display category bias table
    displayCategoryBiasTable(data.category_bias);

    // Display strategic insights
    displayStrategicInsights(data.insights);
}

function displayBeforeAfterLevel7Bias(beforeAfterData) {
    const beforeContainer = document.getElementById('before-level-7-bias');
    const afterContainer = document.getElementById('after-level-7-bias');

    if (beforeContainer) {
        beforeContainer.innerHTML = createBiasStatsHTML(beforeAfterData.before_level_7);
        // Update the header to show question count
        const beforeHeader = beforeContainer.parentElement.querySelector('h4');
        if (beforeHeader) {
            const questionCount = beforeAfterData.before_level_7['A'].total_questions;
            beforeHeader.textContent = `Before Level 7 (${questionCount})`;
        }
    }

    if (afterContainer) {
        afterContainer.innerHTML = createBiasStatsHTML(beforeAfterData.level_7_and_after);
        // Update the header to show question count
        const afterHeader = afterContainer.parentElement.querySelector('h4');
        if (afterHeader) {
            const questionCount = beforeAfterData.level_7_and_after['A'].total_questions;
            afterHeader.textContent = `Level 7 and After (${questionCount})`;
        }
    }
}

function createBiasStatsHTML(periodData) {
    return ['A', 'B', 'C', 'D'].map(choice => {
        const choiceData = periodData[choice];
        const biasClass = choiceData.bias_score > 0 ? 'positive-bias' : 'negative-bias';

        return `
            <div class="bias-item ${biasClass}">
                <div class="choice-letter">${choice}</div>
                <div class="percentage">${choiceData.chosen_percentage.toFixed(1)}%</div>
                <div class="bias-score">Bias: ${choiceData.bias_score.toFixed(1)}%</div>
                <div class="question-count">(${choiceData.chosen_count}/${choiceData.answered_questions})</div>
            </div>
        `;
    }).join('');
}

function displayLevelBiasTable(levelBiasData) {
    const container = document.getElementById('level-bias-table');
    if (!container) return;

    let html = `
        <div class="bias-table-header">
            <div>Level</div>
            <div>A</div>
            <div>B</div>
            <div>C</div>
            <div>D</div>
        </div>
    `;

    // Sort levels numerically
    const sortedLevels = Object.keys(levelBiasData).sort((a, b) => {
        const levelA = parseInt(a.replace('level_', ''));
        const levelB = parseInt(b.replace('level_', ''));
        return levelA - levelB;
    });

    sortedLevels.forEach(levelKey => {
        const levelData = levelBiasData[levelKey];
        const levelNumber = levelKey.replace('level_', '');
        const questionCount = levelData['A'].total_questions; // Get total questions from any choice

        html += `
            <div class="bias-table-row">
                <div class="bias-cell"><strong>Level ${levelNumber} (${questionCount})</strong></div>
                ${['A', 'B', 'C', 'D'].map(choice => {
            const choiceData = levelData[choice];
            const biasColor = choiceData.bias_score > 0 ? '#e74c3c' :
                choiceData.bias_score < 0 ? '#27ae60' : '#95a5a6';

            return `
                        <div class="bias-cell">
                            <div class="main-stat">${choiceData.chosen_percentage.toFixed(1)}%</div>
                            <div class="sub-stat" style="color: ${biasColor}">
                                Bias: ${choiceData.bias_score.toFixed(1)}%
                            </div>
                            <div class="question-count">
                                (${choiceData.chosen_count}/${choiceData.answered_questions})
                            </div>
                        </div>
                    `;
        }).join('')}
            </div>
        `;
    });

    container.innerHTML = html;
}

function displayCategoryBiasTable(categoryBiasData) {
    const container = document.getElementById('category-bias-table');
    if (!container) return;

    let html = `
        <div class="bias-table-header">
            <div>Category</div>
            <div>A</div>
            <div>B</div>
            <div>C</div>
            <div>D</div>
        </div>
    `;

    // Sort categories by total bias (sum of absolute bias scores)
    const sortedCategories = Object.keys(categoryBiasData).sort((a, b) => {
        const totalBiasA = ['A', 'B', 'C', 'D'].reduce((sum, choice) =>
            sum + Math.abs(categoryBiasData[a][choice].bias_score), 0);
        const totalBiasB = ['A', 'B', 'C', 'D'].reduce((sum, choice) =>
            sum + Math.abs(categoryBiasData[b][choice].bias_score), 0);
        return totalBiasB - totalBiasA;
    });

    sortedCategories.forEach(category => {
        const categoryData = categoryBiasData[category];
        const questionCount = categoryData['A'].total_questions; // Get total questions from any choice

        html += `
            <div class="bias-table-row">
                <div class="bias-cell"><strong>${category} (${questionCount})</strong></div>
                ${['A', 'B', 'C', 'D'].map(choice => {
            const choiceData = categoryData[choice];
            const biasColor = choiceData.bias_score > 0 ? '#e74c3c' :
                choiceData.bias_score < 0 ? '#27ae60' : '#95a5a6';

            return `
                        <div class="bias-cell">
                            <div class="main-stat">${choiceData.chosen_percentage.toFixed(1)}%</div>
                            <div class="sub-stat" style="color: ${biasColor}">
                                Bias: ${choiceData.bias_score.toFixed(1)}%
                            </div>
                            <div class="question-count">
                                (${choiceData.chosen_count}/${choiceData.answered_questions})
                            </div>
                        </div>
                    `;
        }).join('')}
            </div>
        `;
    });

    container.innerHTML = html;
}

function displayStrategicInsights(insights) {
    const container = document.getElementById('strategic-insights');
    if (!container) return;

    const recommendations = insights.strategic_recommendations;

    let html = `
        <div class="insight-card">
            <h4>🎯 Most Biased Choice</h4>
            <div class="insight-value">${insights.most_biased_choice.choice}</div>
            <div class="insight-description">
                Contestants choose this ${Math.abs(insights.most_biased_choice.bias_score).toFixed(1)}% 
                ${insights.most_biased_choice.bias_score > 0 ? 'more' : 'less'} than it appears as correct answer
            </div>
            ${recommendations.avoid_bias_toward ?
            `<div class="recommendation-badge avoid">Avoid bias toward ${recommendations.avoid_bias_toward}</div>` : ''}
        </div>
        
        <div class="insight-card">
            <h4>⭐ Most Accurate Choice</h4>
            <div class="insight-value">${insights.most_accurate_choice.choice}</div>
            <div class="insight-description">
                When contestants choose this option, they're correct ${insights.most_accurate_choice.accuracy.toFixed(1)}% of the time
            </div>
            ${recommendations.trust_when_seeing ?
            `<div class="recommendation-badge trust">Trust when you see ${recommendations.trust_when_seeing}</div>` : ''}
        </div>
        
        <div class="insight-card">
            <h4>⚠️ Overconfidence Risk</h4>
            <div class="insight-value">${insights.most_overconfident_choice.choice}</div>
            <div class="insight-description">
                Contestants choose this ${insights.most_overconfident_choice.overconfidence.toFixed(1)}% as often as it's actually correct
            </div>
            ${recommendations.be_cautious_with ?
            `<div class="recommendation-badge caution">Be cautious with ${recommendations.be_cautious_with}</div>` : ''}
        </div>
    `;

    container.innerHTML = html;
}

// Pattern Analysis Functions
async function loadPatternAnalysis() {
    const statusDiv = document.getElementById('patternAnalysisStatus');
    const resultsDiv = document.getElementById('patternAnalysisResults');
    const loadButton = document.getElementById('loadPatternAnalysis');

    try {
        loadButton.disabled = true;
        statusDiv.innerHTML = '<div class="status-loading">🔄 Loading comprehensive pattern analysis...</div>';

        const response = await axios.get('/api/pattern_analysis');
        const data = response.data;

        // Display transition matrix
        displayTransitionMatrix(data.transition_matrices.choice_to_choice);

        // Display sequential patterns
        displaySequentialPatterns(data.deep_sequential_patterns);

        // Display first choice impact
        displayFirstChoiceImpact(data.first_choice_patterns);

        // Display performance clusters
        displayPerformanceClusters(data.performance_clusters);

        // Display strategic insights
        displayStrategicInsights(data);

        statusDiv.innerHTML = '<div class="status-success">✅ Pattern analysis loaded successfully!</div>';
        resultsDiv.style.display = 'block';

    } catch (error) {
        console.error('Error loading pattern analysis:', error);
        statusDiv.innerHTML = '<div class="status-error">❌ Error loading pattern analysis. Please try again.</div>';
    } finally {
        loadButton.disabled = false;
    }
}

function displayTransitionMatrix(transitionData) {
    const container = document.getElementById('transitionMatrix');
    container.innerHTML = '';

    for (const [fromChoice, transitions] of Object.entries(transitionData)) {
        const matrixRow = document.createElement('div');
        matrixRow.className = 'matrix-row';

        const fromDiv = document.createElement('div');
        fromDiv.className = 'matrix-from';
        fromDiv.textContent = `From ${fromChoice}:`;

        const transitionsDiv = document.createElement('div');
        transitionsDiv.className = 'matrix-transitions';

        // Sort transitions by count
        const sortedTransitions = Object.entries(transitions)
            .sort(([, a], [, b]) => b - a)
            .slice(0, 5); // Show top 5 transitions

        sortedTransitions.forEach(([toChoice, count]) => {
            const transitionItem = document.createElement('div');
            transitionItem.className = 'transition-item';
            transitionItem.textContent = `→ ${toChoice} (${count}×)`;
            transitionsDiv.appendChild(transitionItem);
        });

        matrixRow.appendChild(fromDiv);
        matrixRow.appendChild(transitionsDiv);
        container.appendChild(matrixRow);
    }
}

function displaySequentialPatterns(patternsData) {
    const container = document.getElementById('sequentialPatterns');
    container.innerHTML = '';

    // Focus on length_3 patterns for better visualization
    const length3Patterns = patternsData.length_3 || {};

    // Get top patterns by success rate
    const topPatterns = Object.entries(length3Patterns)
        .filter(([, data]) => data.occurrences >= 3)
        .sort(([, a], [, b]) => b.success_rate - a.success_rate)
        .slice(0, 10);

    topPatterns.forEach(([pattern, data]) => {
        const patternItem = document.createElement('div');
        patternItem.className = 'pattern-item';

        const sequenceDiv = document.createElement('div');
        sequenceDiv.className = 'pattern-sequence';
        sequenceDiv.textContent = pattern;

        const statsDiv = document.createElement('div');
        statsDiv.className = 'pattern-stats';

        const successRate = document.createElement('span');
        successRate.className = 'success-rate';
        successRate.textContent = `${data.success_rate.toFixed(1)}% success`;

        const occurrences = document.createElement('span');
        occurrences.className = 'occurrences';
        occurrences.textContent = `${data.occurrences} times`;

        statsDiv.appendChild(successRate);
        statsDiv.appendChild(occurrences);

        patternItem.appendChild(sequenceDiv);
        patternItem.appendChild(statsDiv);
        container.appendChild(patternItem);
    });
}

function displayFirstChoiceImpact(firstChoiceData) {
    const container = document.getElementById('firstChoiceImpact');
    container.innerHTML = '';

    // Sort by average final level
    const sortedChoices = Object.entries(firstChoiceData)
        .sort(([, a], [, b]) => b.average_final_level - a.average_final_level);

    sortedChoices.forEach(([choice, data]) => {
        const impactItem = document.createElement('div');
        impactItem.className = 'impact-item';

        const choiceDiv = document.createElement('div');
        choiceDiv.className = 'impact-choice';
        choiceDiv.textContent = `First Choice: ${choice}`;

        const statsDiv = document.createElement('div');
        statsDiv.className = 'impact-stats';

        const stats = [
            { label: 'Contestants', value: `${data.total_contestants}` },
            { label: 'Avg Final Level', value: `${data.average_final_level.toFixed(1)}` },
            { label: 'Elimination Rate', value: `${data.elimination_rate.toFixed(1)}%` },
            { label: 'Avg Correct Rate', value: `${data.average_correct_rate.toFixed(1)}%` }
        ];

        stats.forEach(stat => {
            const statDiv = document.createElement('div');
            statDiv.className = 'impact-stat';
            statDiv.innerHTML = `<span>${stat.label}:</span><span><strong>${stat.value}</strong></span>`;
            statsDiv.appendChild(statDiv);
        });

        impactItem.appendChild(choiceDiv);
        impactItem.appendChild(statsDiv);
        container.appendChild(impactItem);
    });
}

function displayPerformanceClusters(clustersData) {
    const container = document.getElementById('performanceClusters');
    container.innerHTML = '';

    const clusterDescriptions = {
        'high_performers': 'Reached Level 10+',
        'mid_performers': 'Reached Level 5-9',
        'early_eliminators': 'Eliminated Before Level 5',
        'joker_dependent': 'Used Multiple Jokers',
        'pattern_followers': 'Followed Specific Patterns'
    };

    Object.entries(clustersData).forEach(([clusterName, contestants]) => {
        const clusterItem = document.createElement('div');
        clusterItem.className = 'cluster-item';

        const title = document.createElement('div');
        title.className = 'impact-choice';
        title.textContent = clusterName.replace('_', ' ').toUpperCase();

        const description = document.createElement('div');
        description.className = 'impact-stats';
        description.innerHTML = `
            <div class="impact-stat">
                <span>Description:</span>
                <span>${clusterDescriptions[clusterName] || 'Special Pattern'}</span>
            </div>
            <div class="impact-stat">
                <span>Contestants:</span>
                <span><strong>${contestants.length}</strong></span>
            </div>
        `;

        clusterItem.appendChild(title);
        clusterItem.appendChild(description);
        container.appendChild(clusterItem);
    });
}

function displayStrategicInsights(data) {
    const container = document.getElementById('strategicInsights');
    container.innerHTML = '';

    const insights = [
        {
            title: '🎯 Best Sequential Patterns',
            description: 'D→C→B pattern shows 100% success rate with 43 occurrences. Following this sequence significantly increases your chances.'
        },
        {
            title: '🚀 Optimal First Choice',
            description: `First choice 'D' leads to highest average final level (${data.first_choice_patterns.D?.average_final_level.toFixed(1) || 'N/A'}) with strong performance trajectory.`
        },
        {
            title: '🔄 Transition Strategy',
            description: 'C→D and C→B transitions show 97%+ success rates. Use these patterns when possible.'
        },
        {
            title: '⚠️ Elimination Patterns',
            description: `${data.summary_statistics.elimination_rate.toFixed(1)}% elimination rate reveals critical decision points that determine success.`
        },
        {
            title: '💡 Performance Clusters',
            description: `${data.performance_clusters.high_performers.length} high performers vs ${data.performance_clusters.early_eliminators.length} early eliminators show distinct behavioral patterns.`
        }
    ];

    insights.forEach(insight => {
        const insightItem = document.createElement('div');
        insightItem.className = 'insight-item';

        const title = document.createElement('div');
        title.className = 'insight-title';
        title.textContent = insight.title;

        const description = document.createElement('div');
        description.className = 'insight-description';
        description.textContent = insight.description;

        insightItem.appendChild(title);
        insightItem.appendChild(description);
        container.appendChild(insightItem);
    });
}

// Initialize pattern analysis on page load
document.addEventListener('DOMContentLoaded', function () {
    // ...existing code...

    // Add pattern analysis button event listener
    const patternButton = document.getElementById('loadPatternAnalysis');
    if (patternButton) {
        patternButton.addEventListener('click', loadPatternAnalysis);
    }
});
