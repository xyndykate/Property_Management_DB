// Helper to set active tab
function setActiveTab(tabId) {
  document.querySelectorAll('.nav-item').forEach(el => el.classList.remove('active'));
  const tab = document.getElementById(tabId);
  if (tab) tab.classList.add('active');
}

// Dashboard tab click
document.querySelector('[data-page="dashboard"]').addEventListener('click', function(e) {
  e.preventDefault();
  setActiveTab('dashboard-tab');
  document.getElementById('page-title').textContent = 'Dashboard';
  document.getElementById('page-content').innerHTML = document.getElementById('dashboard').outerHTML;
});

// Properties tab click
document.querySelector('[data-page="properties"]').addEventListener('click', function(e) {
  e.preventDefault();
  setActiveTab('properties-tab');
  document.getElementById('page-title').textContent = 'Properties';
  fetch('properties.html')
    .then(response => response.text())
    .then(html => {
      const tempDiv = document.createElement('div');
      tempDiv.innerHTML = html;
      const main = tempDiv.querySelector('main');
      document.getElementById('page-content').innerHTML = main ? main.innerHTML : '<div class="p-6">Could not load properties.</div>';
    })
    .catch(() => {
      document.getElementById('page-content').innerHTML = '<div class="p-6 text-red-600">Failed to load properties page.</div>';
    });
});

document.addEventListener('DOMContentLoaded', function() {
    // Store the initial dashboard content
    const dashboardContent = document.getElementById('main-content').innerHTML;

    // Initialize dashboard
    loadDashboardContent();

    // Navigation configuration
    const navItems = {
        'dashboard-tab': {
            action: () => {
                document.getElementById('main-content').innerHTML = dashboardContent;
                initializeCharts();
            }
        },
        'properties-tab': {
            file: 'properties.html'
        },
        'tenants-tab': {
            file: 'tenants.html'
        },
        'leases-tab': {
            file: 'leases.html'
        },
        'reports-tab': {
            file: 'reports_analytics.html',
            callback: () => {
                // Initialize reports charts after content is loaded
                setTimeout(() => {
                    initializeReportsCharts();
                }, 100);
            }
        },
        'billing-tab': {
            file: 'billing_payments.html'
        },
        'utilities-tab': {
            file: 'utilities.html',
            callback: () => {
                // Initialize utilities charts after content is loaded
                setTimeout(initializeUtilitiesCharts, 100);
            }
        }
    };

    // Add click handlers to nav items
    Object.keys(navItems).forEach(tabId => {
        const element = document.getElementById(tabId);
        if (!element) return;

        element.addEventListener('click', async function(e) {
            e.preventDefault();
            
            // Update active state
            document.querySelectorAll('.nav-item').forEach(el => el.classList.remove('active'));
            this.classList.add('active');

            if (navItems[tabId].action) {
                navItems[tabId].action();
                return;
            }

            try {
                document.getElementById('main-content').innerHTML = 
                    '<div class="p-6">Loading...</div>';

                const response = await fetch(navItems[tabId].file);
                
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
                
                const html = await response.text();
                document.getElementById('main-content').innerHTML = html;
                
            } catch (error) {
                console.error('Error details:', error);
                document.getElementById('main-content').innerHTML = `
                    <div class="p-6">
                        <div class="text-red-600 mb-4">Failed to load page.</div>
                        <div class="text-sm text-gray-600">
                            Error: ${error.message}
                        </div>
                    </div>`;
            }
        });
    });
});

function loadProperties() {
    fetch('properties.html')
        .then(response => response.text())
        .then(html => {
            document.getElementById('main-content').innerHTML = html;
        })
        .catch(error => {
            console.error('Error loading properties:', error);
            document.getElementById('main-content').innerHTML = 
                '<div class="p-6 text-red-600">Failed to load Properties page.</div>';
        });
}

function initializeCharts() {
    // Revenue Chart
    const revenueCtx = document.getElementById('revenueChart').getContext('2d');
    new Chart(revenueCtx, {
        type: 'line',
        data: {
            labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
            datasets: [{
                label: 'Revenue (KSh)',
                data: [650000, 590000, 800000, 810000, 560000, 850000],
                borderColor: 'rgb(59, 130, 246)',
                tension: 0.1
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false
        }
    });

    // Occupancy Chart
    const occupancyCtx = document.getElementById('occupancyChart').getContext('2d');
    new Chart(occupancyCtx, {
        type: 'line',
        data: {
            labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
            datasets: [{
                label: 'Occupancy Rate (%)',
                data: [75, 82, 80, 85, 83, 86],
                borderColor: 'rgb(16, 185, 129)',
                tension: 0.1
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false
        }
    });

    // Utility Chart
    const utilityCtx = document.getElementById('utilityChart').getContext('2d');
    new Chart(utilityCtx, {
        type: 'bar',
        data: {
            labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
            datasets: [
                {
                    label: 'Water (m³)',
                    data: [120, 115, 130, 125, 110, 135],
                    backgroundColor: 'rgba(59, 130, 246, 0.5)'
                },
                {
                    label: 'Electricity (kWh)',
                    data: [450, 420, 480, 460, 440, 490],
                    backgroundColor: 'rgba(245, 158, 11, 0.5)'
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: {
                    beginAtZero: true
                }
            }
        }
    });
}

// Call initializeCharts when loading dashboard content
function loadDashboardContent() {
    // Initialize charts when dashboard loads
    initializeCharts();
}

// Add this function to initialize reports charts
function initializeReportsCharts() {
    // Revenue Chart
    const revenueCtx = document.getElementById('revenueChart')?.getContext('2d');
    if (revenueCtx) {
        new Chart(revenueCtx, {
            type: 'line',
            data: {
                labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
                datasets: [{
                    label: 'Revenue',
                    data: [650000, 590000, 800000, 810000, 560000, 850000],
                    borderColor: 'rgb(59, 130, 246)',
                    tension: 0.1
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false
            }
        });
    }

    // Occupancy Trend Chart
    const occupancyCtx = document.getElementById('occupancyTrendChart')?.getContext('2d');
    if (occupancyCtx) {
        new Chart(occupancyCtx, {
            type: 'bar',
            data: {
                labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
                datasets: [{
                    label: 'Occupancy Rate',
                    data: [85, 82, 88, 90, 85, 92],
                    backgroundColor: 'rgb(16, 185, 129)',
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false
            }
        });
    }

    // Payment Status Chart
    const paymentCtx = document.getElementById('paymentStatusChart')?.getContext('2d');
    if (paymentCtx) {
        new Chart(paymentCtx, {
            type: 'doughnut',
            data: {
                labels: ['Paid', 'Pending', 'Overdue'],
                datasets: [{
                    data: [70, 20, 10],
                    backgroundColor: [
                        'rgb(16, 185, 129)',
                        'rgb(251, 191, 36)',
                        'rgb(239, 68, 68)'
                    ]
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false
            }
        });
    }
}

function initializeUtilitiesCharts() {
    const waterCtx = document.getElementById('waterUsageChart')?.getContext('2d');
    if (waterCtx) {
        new Chart(waterCtx, {
            type: 'line',
            data: {
                labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
                datasets: [{
                    label: 'Water Usage (m³)',
                    data: [2200, 2450, 2300, 2600, 2450, 2300],
                    borderColor: 'rgb(59, 130, 246)',
                    tension: 0.1,
                    fill: true,
                    backgroundColor: 'rgba(59, 130, 246, 0.1)'
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
                            text: 'Water Consumption (m³)'
                        }
                    }
                }
            }
        });
    }
}