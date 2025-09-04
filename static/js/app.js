// Self-Focus Management App JavaScript

// Global utilities
window.SelfFocus = {
    // API helpers
    async apiCall(url, options = {}) {
        const defaultOptions = {
            headers: {
                'Content-Type': 'application/json',
            }
        };
        
        const response = await fetch(url, { ...defaultOptions, ...options });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        return response.json();
    },

    // Alert system
    showAlert(type, message, duration = 5000) {
        const alertDiv = document.createElement('div');
        alertDiv.className = `alert alert-${type}`;
        alertDiv.textContent = message;
        
        const container = document.querySelector('.main-content') || document.body;
        container.insertBefore(alertDiv, container.firstChild);
        
        // Auto dismiss
        if (duration > 0) {
            setTimeout(() => {
                if (alertDiv.parentNode) {
                    alertDiv.remove();
                }
            }, duration);
        }
        
        return alertDiv;
    },

    // Loading states
    setLoading(element, loading = true) {
        if (loading) {
            element.disabled = true;
            element.dataset.originalText = element.innerHTML;
            element.innerHTML = '<span class="spinner"></span> Loading...';
            element.classList.add('loading');
        } else {
            element.disabled = false;
            element.innerHTML = element.dataset.originalText || 'Submit';
            element.classList.remove('loading');
        }
    },

    // Form validation
    validateForm(form) {
        const requiredFields = form.querySelectorAll('[required]');
        let isValid = true;
        
        requiredFields.forEach(field => {
            if (!field.value.trim()) {
                field.classList.add('error');
                isValid = false;
            } else {
                field.classList.remove('error');
            }
        });
        
        return isValid;
    },

    // Date formatting
    formatDate(date) {
        return new Date(date).toLocaleDateString('en-US', {
            year: 'numeric',
            month: 'short',
            day: 'numeric'
        });
    },

    // Currency formatting
    formatCurrency(amount) {
        return new Intl.NumberFormat('en-US', {
            style: 'currency',
            currency: 'USD'
        }).format(amount);
    },

    // Progress bar animation
    animateProgress(progressBar, targetPercentage) {
        const startWidth = parseInt(progressBar.style.width) || 0;
        const increment = (targetPercentage - startWidth) / 20;
        let currentWidth = startWidth;
        
        const animate = () => {
            if (currentWidth < targetPercentage) {
                currentWidth += increment;
                progressBar.style.width = Math.min(currentWidth, targetPercentage) + '%';
                requestAnimationFrame(animate);
            }
        };
        
        requestAnimationFrame(animate);
    }
};

// Mobile sidebar toggle
document.addEventListener('DOMContentLoaded', function() {
    const sidebar = document.getElementById('sidebar');
    const toggleBtn = document.getElementById('sidebarToggle');
    
    if (toggleBtn && sidebar) {
        toggleBtn.addEventListener('click', function() {
            sidebar.classList.toggle('open');
        });
        
        // Close sidebar when clicking outside on mobile
        document.addEventListener('click', function(event) {
            if (window.innerWidth <= 768 && 
                !sidebar.contains(event.target) && 
                !toggleBtn.contains(event.target) &&
                sidebar.classList.contains('open')) {
                sidebar.classList.remove('open');
            }
        });
    }
});

// Auto-dismiss alerts
document.addEventListener('DOMContentLoaded', function() {
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(alert => {
        if (!alert.dataset.persist) {
            setTimeout(() => {
                if (alert.parentNode) {
                    alert.style.opacity = '0';
                    alert.style.transition = 'opacity 0.3s';
                    setTimeout(() => alert.remove(), 300);
                }
            }, 5000);
        }
    });
});

// Form enhancements
document.addEventListener('DOMContentLoaded', function() {
    // Add floating labels to forms
    const formControls = document.querySelectorAll('.form-control');
    formControls.forEach(input => {
        if (input.value) {
            input.classList.add('has-value');
        }
        
        input.addEventListener('input', function() {
            if (this.value) {
                this.classList.add('has-value');
            } else {
                this.classList.remove('has-value');
            }
        });
    });
    
    // Form submission handling
    const forms = document.querySelectorAll('form[data-ajax="true"]');
    forms.forEach(form => {
        form.addEventListener('submit', async function(e) {
            e.preventDefault();
            
            if (!SelfFocus.validateForm(this)) {
                SelfFocus.showAlert('error', 'Please fill in all required fields');
                return;
            }
            
            const submitBtn = this.querySelector('button[type="submit"]');
            SelfFocus.setLoading(submitBtn, true);
            
            try {
                const formData = new FormData(this);
                const response = await fetch(this.action, {
                    method: this.method,
                    body: formData
                });
                
                if (response.ok) {
                    SelfFocus.showAlert('success', 'Operation completed successfully');
                    if (this.dataset.redirect) {
                        window.location.href = this.dataset.redirect;
                    }
                } else {
                    throw new Error('Server error');
                }
            } catch (error) {
                SelfFocus.showAlert('error', 'An error occurred. Please try again.');
            } finally {
                SelfFocus.setLoading(submitBtn, false);
            }
        });
    });
});

// Habit tracking functions
window.toggleHabit = async function(habitId, button) {
    try {
        SelfFocus.setLoading(button, true);
        button.innerHTML = '<span class="spinner"></span>';
        
        const response = await SelfFocus.apiCall(`/habits/${habitId}/checkin`, {
            method: 'POST',
            body: JSON.stringify({
                date: new Date().toISOString().split('T')[0]
            })
        });
        
        if (response.success) {
            button.className = 'habit-toggle btn btn-sm btn-success';
            button.innerHTML = '✓';
            
            // Update streak display
            const habitCard = button.closest('.habit-card');
            if (habitCard) {
                const streakText = habitCard.querySelector('.text-sm');
                if (streakText && streakText.textContent.includes('streak:')) {
                    streakText.textContent = `Current streak: ${response.current_streak} days`;
                }
            }
            
            SelfFocus.showAlert('success', response.message);
        } else {
            throw new Error(response.message || 'Failed to update habit');
        }
    } catch (error) {
        button.className = 'habit-toggle btn btn-sm btn-outline';
        button.innerHTML = '○';
        SelfFocus.showAlert('error', error.message || 'Failed to update habit');
    } finally {
        SelfFocus.setLoading(button, false);
    }
};

// Goal management functions
window.updateGoalStatus = async function(goalId, newStatus, button) {
    try {
        SelfFocus.setLoading(button, true);
        
        const response = await SelfFocus.apiCall(`/goals/${goalId}/status`, {
            method: 'POST',
            body: JSON.stringify({ status: newStatus })
        });
        
        if (response.success) {
            SelfFocus.showAlert('success', response.message);
            location.reload(); // Refresh to show updated status
        } else {
            throw new Error(response.message || 'Failed to update goal');
        }
    } catch (error) {
        SelfFocus.showAlert('error', error.message || 'Failed to update goal status');
    } finally {
        SelfFocus.setLoading(button, false);
    }
};

window.completeMilestone = async function(milestoneId, button) {
    try {
        SelfFocus.setLoading(button, true);
        
        const response = await SelfFocus.apiCall(`/goals/milestones/${milestoneId}/complete`, {
            method: 'POST'
        });
        
        if (response.success) {
            button.className = 'btn btn-sm btn-success';
            button.innerHTML = '✓ Completed';
            button.disabled = true;
            
            // Update progress bar if present
            const progressBar = document.querySelector('.progress-bar');
            if (progressBar && response.goal_progress !== undefined) {
                SelfFocus.animateProgress(progressBar, response.goal_progress);
            }
            
            SelfFocus.showAlert('success', response.message);
        } else {
            throw new Error(response.message || 'Failed to complete milestone');
        }
    } catch (error) {
        SelfFocus.showAlert('error', error.message || 'Failed to complete milestone');
    } finally {
        SelfFocus.setLoading(button, false);
    }
};

// Transaction management
window.deleteTransaction = async function(transactionId, button) {
    if (!confirm('Are you sure you want to delete this transaction?')) {
        return;
    }
    
    try {
        SelfFocus.setLoading(button, true);
        
        const response = await fetch(`/transactions/${transactionId}/delete`, {
            method: 'POST'
        });
        
        if (response.ok) {
            SelfFocus.showAlert('success', 'Transaction deleted successfully');
            // Remove the row from the table
            const row = button.closest('tr');
            if (row) {
                row.style.opacity = '0';
                row.style.transition = 'opacity 0.3s';
                setTimeout(() => row.remove(), 300);
            }
        } else {
            throw new Error('Failed to delete transaction');
        }
    } catch (error) {
        SelfFocus.showAlert('error', error.message || 'Failed to delete transaction');
    } finally {
        SelfFocus.setLoading(button, false);
    }
};

// Chart initialization (for dashboard and reports)
window.initCharts = function() {
    // Simple chart implementation without external dependencies
    const chartElements = document.querySelectorAll('[data-chart]');
    
    chartElements.forEach(element => {
        const chartType = element.dataset.chart;
        const data = JSON.parse(element.dataset.chartData || '[]');
        
        if (chartType === 'doughnut') {
            createDoughnutChart(element, data);
        } else if (chartType === 'line') {
            createLineChart(element, data);
        }
    });
};

function createDoughnutChart(element, data) {
    // Simple SVG-based doughnut chart
    const total = data.reduce((sum, item) => sum + item.value, 0);
    let currentAngle = 0;
    
    const svg = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
    svg.setAttribute('width', '200');
    svg.setAttribute('height', '200');
    svg.setAttribute('viewBox', '0 0 200 200');
    
    data.forEach(item => {
        const percentage = (item.value / total) * 100;
        const angle = (percentage / 100) * 360;
        
        // Create path for slice
        const path = createArcPath(100, 100, 70, currentAngle, currentAngle + angle);
        const pathElement = document.createElementNS('http://www.w3.org/2000/svg', 'path');
        pathElement.setAttribute('d', path);
        pathElement.setAttribute('fill', item.color || '#3b82f6');
        pathElement.setAttribute('stroke', 'white');
        pathElement.setAttribute('stroke-width', '2');
        
        svg.appendChild(pathElement);
        currentAngle += angle;
    });
    
    element.appendChild(svg);
}

function createArcPath(cx, cy, radius, startAngle, endAngle) {
    const startAngleRad = (startAngle - 90) * Math.PI / 180;
    const endAngleRad = (endAngle - 90) * Math.PI / 180;
    
    const largeArcFlag = endAngle - startAngle <= 180 ? '0' : '1';
    
    const x1 = cx + radius * Math.cos(startAngleRad);
    const y1 = cy + radius * Math.sin(startAngleRad);
    const x2 = cx + radius * Math.cos(endAngleRad);
    const y2 = cy + radius * Math.sin(endAngleRad);
    
    return `M ${cx} ${cy} L ${x1} ${y1} A ${radius} ${radius} 0 ${largeArcFlag} 1 ${x2} ${y2} Z`;
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', function() {
    if (typeof window.initCharts === 'function') {
        window.initCharts();
    }
});

document.addEventListener('DOMContentLoaded', function() {
    // Add smooth transitions for navigation
    const navLinks = document.querySelectorAll('.sidebar a');
    
    navLinks.forEach(link => {
        link.addEventListener('click', function() {
            // Remove active class from all links
            navLinks.forEach(l => l.classList.remove('active'));
            
            // Add active class to clicked link
            this.classList.add('active');
        });
    });
});