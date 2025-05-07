// project_enhancement.js - Add to your static/js directory

/**
 * Opens the project enhancement modal and populates it with data
 *
 * @param {string} parentIndex - The parent index of the bullet point
 * @param {string} bulletIndex - The index of the bullet point
 * @param {string} projectName - The name of the project
 * @param {string} projectTitle - The title/role of the project (optional)
 * @param {string} projectSummary - The summary of the project (optional)
 */
function openProjectEnhanceModal(parentIndex, bulletIndex, projectName, projectTitle = "", projectSummary = "") {
    console.log("Opening project enhancement modal for bullet:", parentIndex, bulletIndex);
    const modal = document.getElementById('project-enhancement-modal');
    if (!modal) {
        console.error("Enhancement modal not found!");
        return;
    }

    // Get the bullet text
    const bulletTextarea = document.getElementById(`bullet_${parentIndex}_${bulletIndex}`);
    if (!bulletTextarea) {
        console.error("Bullet textarea not found:", `bullet_${parentIndex}_${bulletIndex}`);
        return;
    }

    const bulletText = bulletTextarea.value.trim();
    if (!bulletText) {
        alert('Please enter some text in the bullet point first.');
        return;
    }

    // Set hidden fields and original bullet text
    document.getElementById('parent_index_modal').value = parentIndex;
    document.getElementById('bullet_index_modal').value = bulletIndex;
    document.getElementById('original_bullet_modal').value = bulletText;

    // Set project context fields
    document.getElementById('project_name_modal').value = projectName;
    document.getElementById('project_title_modal').value = projectTitle || "";
    document.getElementById('project_summary_modal').value = projectSummary || "";

    // Update display text
    document.getElementById('project_name_display').textContent = projectName;
    document.getElementById('project_title_display').textContent = projectTitle || "(Not specified)";
    document.getElementById('project_summary_display').textContent = projectSummary || "(No summary provided)";

    // Reset enhancement options and results
    document.getElementById('enhancement-general').checked = true;
    document.getElementById('enhance-engine-chatgpt').checked = true;
    document.getElementById('enhancement_in_progress').classList.add('hidden');
    document.getElementById('enhanced_bullet_result').innerHTML = '<p class="text-gray-400 italic">Enhanced bullet point will appear here</p>';
    document.getElementById('apply_enhancement_btn').disabled = true;

    // Show the modal
    modal.classList.remove('hidden');
    modal.style.display = 'block';
    document.body.classList.add('overflow-hidden');
}

/**
 * Closes the project enhancement modal
 */
function closeProjectEnhanceModal() {
    const modal = document.getElementById('project-enhancement-modal');
    if (modal) {
        modal.classList.add('hidden');
        modal.style.display = 'none';
        document.body.classList.remove('overflow-hidden');
    }
}

/**
 * Apply the enhanced bullet point back to the form
 */
function applyProjectEnhancement() {
    console.log("Applying project enhancement");
    const parentIndex = document.getElementById('parent_index_modal').value;
    const bulletIndex = document.getElementById('bullet_index_modal').value;
    const enhancedBullet = document.getElementById('enhanced_bullet_result').textContent.trim();

    // Find the textarea to update
    const bulletTextarea = document.getElementById(`bullet_${parentIndex}_${bulletIndex}`);
    if (bulletTextarea && enhancedBullet && enhancedBullet !== "Enhanced bullet point will appear here") {
        // Update the textarea
        bulletTextarea.value = enhancedBullet;

        // Update the bullet quality display if that function exists
        if (typeof checkBulletQuality === 'function') {
            checkBulletQuality(bulletTextarea);
        }

        // Add a highlight effect
        bulletTextarea.classList.add('bg-green-50', 'border-green-300');
        setTimeout(() => {
            bulletTextarea.classList.remove('bg-green-50', 'border-green-300');
        }, 1500);

        // Close the modal
        closeProjectEnhanceModal();

        // Show success message (if you have a toast system)
        if (typeof showToast === 'function') {
            showToast("Bullet point enhanced successfully!", "success");
        }
    } else {
        console.error("Could not find bullet textarea or enhanced text");
        if (typeof showToast === 'function') {
            showToast("Error applying enhancement", "error");
        } else {
            alert("Error applying enhancement. Please try again.");
        }
    }
}

// Handle successful enhancement result
document.addEventListener('htmx:afterSwap', function(evt) {
    if (evt.detail.target.id === 'enhanced_bullet_result') {
        // Enable the apply button
        const applyBtn = document.getElementById('apply_enhancement_btn');
        if (applyBtn) {
            applyBtn.disabled = false;
        }

        // Check the content length and provide feedback
        const resultText = evt.detail.target.textContent.trim();
        const resultLength = resultText.length;
        let qualityClass = '';
        let qualityMessage = '';

        if (resultLength >= 80 && resultLength <= 150) {
            qualityClass = 'text-success';
            qualityMessage = 'Excellent length and impact';
        } else if (resultLength > 150) {
            qualityClass = 'text-warning';
            qualityMessage = 'Good but slightly long';
        } else {
            qualityClass = 'text-warning';
            qualityMessage = 'Good but could be more detailed';
        }

        // Add quality indicator if it doesn't exist
        const qualityIndicator = document.createElement('div');
        qualityIndicator.id = 'quality_indicator';
        qualityIndicator.className = `mt-2 text-sm ${qualityClass}`;
        qualityIndicator.textContent = qualityMessage;

        // Replace existing indicator or add new one
        const existingIndicator = document.getElementById('quality_indicator');
        if (existingIndicator) {
            existingIndicator.replaceWith(qualityIndicator);
        } else {
            evt.detail.target.appendChild(qualityIndicator);
        }
    }
});

// Document ready handler to bind events
document.addEventListener('DOMContentLoaded', function() {
    // If project-enhancement-form exists outside of HTMX requests, set up form submission
    const enhancementForm = document.getElementById('project-enhancement-form');
    if (enhancementForm) {
        enhancementForm.addEventListener('submit', function(e) {
            // Let HTMX handle the form submission
            console.log("Project enhancement form submitted via HTMX");
        });
    }

    // Set up event listeners for any enhance buttons already in the DOM
    const enhanceButtons = document.querySelectorAll('.project-enhance-btn');
    enhanceButtons.forEach(btn => {
        const parentIndex = btn.getAttribute('data-parent');
        const bulletIndex = btn.getAttribute('data-index');
        const projectName = btn.getAttribute('data-project-name');
        const projectTitle = btn.getAttribute('data-project-title');
        const projectSummary = btn.getAttribute('data-project-summary');

        if (parentIndex && bulletIndex && projectName) {
            btn.addEventListener('click', function() {
                openProjectEnhanceModal(parentIndex, bulletIndex, projectName, projectTitle, projectSummary);
            });
        }
    });
});