// static/js/resume_wizard.js

// Resume preview functionality
function previewResume() {
    // Show the modal
    const modal = document.getElementById('preview-modal');
    if (!modal) {
        console.error('Preview modal not found');
        return;
    }

    modal.classList.remove('hidden');
    document.body.classList.add('overflow-hidden'); // Prevent scrolling

    // Get the current form data
    const form = document.getElementById('resume-form');
    const formData = new FormData(form);
    const modalContent = document.getElementById('preview-modal-content');

    modalContent.innerHTML = '<div class="flex justify-center p-8"><span class="loading loading-spinner loading-lg"></span></div>';

    // Get CSRF token
    const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;

    // Make an AJAX request to the preview URL
    fetch('/resume/preview-current/', {
        method: 'POST',
        body: formData,
        headers: {
            'X-CSRFToken': csrfToken,
            'X-Requested-With': 'XMLHttpRequest'
        }
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        return response.text();
    })
    .then(html => {
        if (modalContent) {
            modalContent.innerHTML = html;
        }
    })
    .catch(error => {
        console.error('Error fetching preview:', error);
        if (modalContent) {
            modalContent.innerHTML = '<div class="alert alert-error p-4">Error loading preview. Please try again.</div>';
        }
    });
}

// Close preview modal
function closePreviewModal() {
    const modal = document.getElementById('preview-modal');
    if (modal) {
        modal.classList.add('hidden');
    }
    document.body.classList.remove('overflow-hidden');
}

// Function to toggle more profiles section
function toggleMoreProfiles() {
    const moreProfiles = document.getElementById('more-profiles');
    const button = document.getElementById('add-more-profiles');

    if (!moreProfiles || !button) return;

    if (moreProfiles.classList.contains('hidden')) {
        // Show more profiles
        moreProfiles.classList.remove('hidden');
        moreProfiles.classList.add('animate-fade-in');
        button.innerHTML = '<i class="fa-solid fa-minus mr-2"></i> Show fewer profiles';
    } else {
        // Hide more profiles
        moreProfiles.classList.add('hidden');
        button.innerHTML = '<i class="fa-solid fa-plus mr-2"></i> Add more profiles';
    }
}

// Add form row (for multiple entries like skills, experiences, etc.)
function addFormRow(type, containerId, countFieldId) {
    // Get current count
    const countField = document.getElementById(countFieldId);
    if (!countField) return;

    const currentIndex = parseInt(countField.value);

    // Increment the count
    countField.value = currentIndex + 1;

    const container = document.getElementById(containerId);
    if (!container) return;

    // Show loading state
    const loadingRow = document.createElement('div');
    loadingRow.className = 'flex justify-center p-4';
    loadingRow.innerHTML = '<span class="loading loading-spinner loading-md"></span>';
    container.appendChild(loadingRow);

    // Use AJAX to fetch the new row template
    fetch(`/resume/add-form-row/?form_type=${type}&index=${currentIndex}`, {
        headers: {
            'X-Requested-With': 'XMLHttpRequest'
        }
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        return response.text();
    })
    .then(html => {
        // Remove loading state
        if (loadingRow && loadingRow.parentNode) {
            loadingRow.remove();
        }

        // If this is the first item, clear any empty state
        if (currentIndex === 0 && container.querySelector('.text-center')) {
            container.innerHTML = '';
        }

        // Insert the new row
        container.insertAdjacentHTML('beforeend', html);

        // Scroll to the new row
        const newRow = container.lastElementChild;
        if (newRow) {
            newRow.scrollIntoView({ behavior: 'smooth', block: 'center' });

            // Add highlight effect
            newRow.classList.add('ring-2', 'ring-primary', 'ring-offset-2');
            setTimeout(() => {
                newRow.classList.remove('ring-2', 'ring-primary', 'ring-offset-2');
            }, 1500);
        }
    })
    .catch(error => {
        console.error('Error adding form row:', error);

        // Remove loading state
        if (loadingRow && loadingRow.parentNode) {
            loadingRow.remove();
        }

        // Show error message
        const errorMsg = document.createElement('div');
        errorMsg.className = 'alert alert-error my-3';
        errorMsg.textContent = 'Error adding new entry. Please try again.';
        container.appendChild(errorMsg);

        // Remove error after 3 seconds
        setTimeout(() => {
            if (errorMsg && errorMsg.parentNode) {
                errorMsg.remove();
            }
        }, 3000);
    });
}

// Remove form row
function removeFormRow(button, containerId, countFieldId) {
    const container = document.getElementById(containerId);
    if (!container) return;

    const row = button.closest('.form-row');
    if (!row) return;

    // Animation for removal
    row.style.transition = 'all 0.3s ease';
    row.style.opacity = '0';
    row.style.maxHeight = '0';
    row.style.overflow = 'hidden';

    setTimeout(() => {
        if (row.parentNode) {
            row.remove();
        }

        // Update the counter
        const countField = document.getElementById(countFieldId);
        if (countField) {
            countField.value = parseInt(countField.value) - 1;
        }

        // Show empty state if no rows left
        if (container.children.length === 0) {
            // Fetch the empty state template or use a default
            const emptyState = `
                <div class="bg-base-100 border border-gray-100 dark:border-gray-700 rounded-xl shadow p-8 text-center">
                    <div class="w-16 h-16 rounded-full bg-primary/10 flex items-center justify-center mx-auto mb-4">
                        <i class="fa-solid fa-plus text-primary text-2xl"></i>
                    </div>
                    <h3 class="text-lg font-medium mb-2">No Items Added Yet</h3>
                    <p class="text-gray-500 max-w-md mx-auto mb-6">
                        Add items to continue building your resume.
                    </p>
                    <button type="button" class="btn btn-primary" 
                            onclick="addFormRow('${containerId.replace('_container', '')}', '${containerId}', '${countFieldId}')">
                        <i class="fa-solid fa-plus mr-2"></i> Add Your First Item
                    </button>
                </div>
            `;
            container.innerHTML = emptyState;
        }
    }, 300);
}

// Add bullet point
function addBulletPoint(parentIndex) {
    const container = document.getElementById(`bullet_points_container_${parentIndex}`);
    if (!container) return;

    const bulletCount = container.querySelectorAll('.bullet-point-row').length;

    // Update hidden field
    const countField = document.getElementById(`bullet_count_${parentIndex}`);
    if (countField) {
        countField.value = bulletCount + 1;
    }

    // Create new bullet point row
    const newRow = document.createElement('div');
    newRow.className = 'bullet-point-row flex items-start gap-3 group p-2 rounded-md transition-colors';

    newRow.innerHTML = `
        <div class="mt-3 text-primary">•</div>
        <div class="form-control flex-1">
            <textarea class="textarea textarea-bordered w-full min-h-24"
                id="bullet_${parentIndex}_${bulletCount}"
                name="bullet_${parentIndex}_${bulletCount}"
                placeholder="Describe your achievement with action verbs and measurable results"></textarea>
        </div>
        <button type="button" class="btn btn-circle btn-outline btn-error btn-sm mt-3 opacity-70 hover:opacity-100"
                onclick="removeBulletPoint(this, '${parentIndex}')">
            <i class="fa-solid fa-times"></i>
        </button>
    `;

    // Add to container
    container.appendChild(newRow);

    // Add entrance animation
    newRow.style.opacity = '0';
    newRow.style.transform = 'translateY(10px)';

    setTimeout(() => {
        newRow.style.transition = 'all 0.3s ease';
        newRow.style.opacity = '1';
        newRow.style.transform = 'translateY(0)';

        // Focus on new textarea
        const textarea = document.getElementById(`bullet_${parentIndex}_${bulletCount}`);
        if (textarea) {
            textarea.focus();
        }
    }, 10);
}

// Remove bullet point
function removeBulletPoint(button, parentIndex) {
    const container = document.getElementById(`bullet_points_container_${parentIndex}`);
    if (!container) return;

    const row = button.closest('.bullet-point-row');
    if (!row) return;

    // Don't remove if it's the last one
    if (container.querySelectorAll('.bullet-point-row').length <= 1) {
        const textarea = row.querySelector('textarea');
        if (textarea) {
            textarea.value = '';
            textarea.focus();
        }
        return;
    }

    // Animation
    row.style.transition = 'all 0.2s ease';
    row.style.opacity = '0';
    row.style.transform = 'translateX(10px)';

    setTimeout(() => {
        if (row.parentNode) {
            row.remove();
        }

        // Renumber bullets
        container.querySelectorAll('.bullet-point-row').forEach((bullet, idx) => {
            const textarea = bullet.querySelector('textarea');
            if (textarea) {
                textarea.id = `bullet_${parentIndex}_${idx}`;
                textarea.name = `bullet_${parentIndex}_${idx}`;
            }
        });

        // Update count
        const countField = document.getElementById(`bullet_count_${parentIndex}`);
        if (countField) {
            countField.value = container.querySelectorAll('.bullet-point-row').length;
        }
    }, 200);
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', function() {
    // Set up modal close actions
    const modal = document.getElementById('preview-modal');
    if (modal) {
        // Close modal when clicking outside content
        modal.addEventListener('click', function(e) {
            if (e.target === this) {
                closePreviewModal();
            }
        });
    }

    // Close modal with escape key
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape' && modal && !modal.classList.contains('hidden')) {
            closePreviewModal();
        }
    });

    // Initialize character counters
    document.querySelectorAll('textarea[data-count]').forEach(textarea => {
        const countDisplay = document.getElementById(textarea.dataset.count);
        if (countDisplay) {
            updateCharCount(textarea, countDisplay);
            textarea.addEventListener('input', () => updateCharCount(textarea, countDisplay));
        }
    });
});

// Update character count
function updateCharCount(textarea, countDisplay) {
    if (!textarea || !countDisplay) return;

    const count = textarea.value.length;
    const minCount = parseInt(textarea.dataset.minCount || 0);

    countDisplay.textContent = count;

    if (minCount > 0) {
        if (count < minCount) {
            countDisplay.classList.add('text-error');
            countDisplay.classList.remove('text-success');
        } else {
            countDisplay.classList.add('text-success');
            countDisplay.classList.remove('text-error');
        }
    }
}