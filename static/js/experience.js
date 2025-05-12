/**
 * Complete JavaScript for Resume Experience Section
 * With enhanced bullet point functionality
 */

// Store skills data globally for modals
let userSkillsData = [];
// Store formset prefix globally
const formsetPrefix = 'experience_set'; // Make sure this matches your Django formset prefix

document.addEventListener('DOMContentLoaded', function() {
    console.log("Document loaded, initializing event handlers");

    // Parse skills data
    const skillsJsonInput = document.getElementById('skills-data-json');
    if (skillsJsonInput && skillsJsonInput.value) {
        try {
            let skillsJson = skillsJsonInput.value;
            if (skillsJson.startsWith('"') && skillsJson.endsWith('"')) {
                skillsJson = skillsJson.substring(1, skillsJson.length - 1).replace(/\\"/g, '"');
            }
            userSkillsData = JSON.parse(skillsJson);
            console.log("Parsed skills data:", userSkillsData.length);
        } catch (e) {
            console.error("Error parsing skills JSON:", e, "Raw value:", skillsJsonInput.value);
            userSkillsData = [];
        }
    } else {
        console.warn("Skills data JSON input not found or empty.");
    }

    // Initialize 'is_current' checkbox state for all experience forms rendered on page load
    document.querySelectorAll('.experience-entry input[name$="-is_current"]').forEach(function(checkbox) {
        toggleEndDate(checkbox); // Initialize on page load
    });

    // Initialize bullet quality checks for all existing textareas
    document.querySelectorAll('.bullet-point-row textarea').forEach(textarea => {
        updateBulletQualityUI(textarea);
    });

    // Attach event listeners to AI Generate buttons
    attachAIGenerateButtonListeners();

    // Attach event listeners to enhance buttons
    attachEnhanceButtonListeners();

    // Set up modal buttons
    setupModalButtons();

    // Move modals to body to avoid nesting issues
    moveModalToBody('bullet-generation-modal');
    moveModalToBody('bullet-enhancement-modal');
});

function attachAIGenerateButtonListeners() {
    document.querySelectorAll('.open-experience-ai-modal').forEach(button => {
        const parentIndex = button.getAttribute('data-parent-index');
        if (parentIndex !== null) {
            console.log("Attaching AI Generate listener to button index:", parentIndex);
            button.addEventListener('click', function(e) {
                e.preventDefault();
                e.stopPropagation();
                console.log("AI Generate button clicked for index:", parentIndex);
                openBulletGenerationModal(parentIndex);
            });
        } else {
            console.warn("AI Generate button found without data-parent-index:", button);
        }
    });
}

function attachEnhanceButtonListeners() {
    document.querySelectorAll('.enhance-main-form-bullet-btn').forEach(button => {
        const parentIndex = button.getAttribute('data-experience-index');
        const textareaId = button.getAttribute('data-textarea-id');

        if (parentIndex !== null && textareaId) {
            button.addEventListener('click', function(e) {
                e.preventDefault();
                e.stopPropagation();
                console.log("Enhance button clicked for experience:", parentIndex, "textarea:", textareaId);

                // Get the textarea element directly by ID
                const bulletTextarea = document.getElementById(textareaId);
                if (!bulletTextarea) {
                    console.error("Could not find textarea with ID:", textareaId);
                    return;
                }

                // Get the bullet text directly from the textarea
                const bulletText = bulletTextarea.value.trim();
                if (!bulletText) {
                    alert("Please write something in the bullet point first.");
                    return;
                }

                openBulletEnhancementModal(bulletTextarea);
            });
        } else {
            console.warn("Enhance button found with missing attributes:", button);
        }
    });
}

function setupModalButtons() {
    // Setup Generation Modal Buttons
    const generateBulletsBtn = document.getElementById('generate-bullets-btn');
    if (generateBulletsBtn) {
        generateBulletsBtn.addEventListener('click', function(e) {
            e.preventDefault();
            generateBullets();
        });
    } else {
        console.error("Button #generate-bullets-btn not found");
    }

    const applyBulletsBtn = document.getElementById('apply-bullets-btn');
    if (applyBulletsBtn) {
        applyBulletsBtn.addEventListener('click', function(e) {
            e.preventDefault();
            applyGeneratedBullets();
        });
    } else {
        console.error("Button #apply-bullets-btn not found");
    }

    const cancelGenerationBtn = document.getElementById('cancel-generation-btn');
    if (cancelGenerationBtn) {
        cancelGenerationBtn.addEventListener('click', function(e) {
            e.preventDefault();
            closeBulletGenerationModal();
        });
    } else {
        console.error("Button #cancel-generation-btn not found");
    }

    // Setup Enhancement Modal Buttons
    const enhanceBulletBtn = document.getElementById('enhance-bullet-btn');
    if (enhanceBulletBtn) {
        enhanceBulletBtn.addEventListener('click', function(e) {
            e.preventDefault();
            enhanceBullet();
        });
    } else {
        console.error("Button #enhance-bullet-btn not found");
    }

    const applyEnhancementBtn = document.getElementById('apply-enhancement-btn');
    if (applyEnhancementBtn) {
        applyEnhancementBtn.addEventListener('click', function(e) {
            e.preventDefault();
            applyEnhancement();
        });
    } else {
        console.error("Button #apply-enhancement-btn not found");
    }

    const cancelEnhancementBtn = document.getElementById('cancel-enhancement-btn');
    if (cancelEnhancementBtn) {
        cancelEnhancementBtn.addEventListener('click', function(e) {
            e.preventDefault();
            closeBulletEnhancementModal();
        });
    } else {
        console.error("Button #cancel-enhancement-btn not found");
    }

    // Setup Modal Backdrops
    const bulletModalBackdrop = document.getElementById('bullet-modal-backdrop');
    if (bulletModalBackdrop) {
        bulletModalBackdrop.addEventListener('click', function(e) {
            e.preventDefault();
            closeBulletGenerationModal();
        });
    } else {
        console.error("#bullet-modal-backdrop not found");
    }

    const enhanceModalBackdrop = document.getElementById('enhance-modal-backdrop');
    if (enhanceModalBackdrop) {
        enhanceModalBackdrop.addEventListener('click', function(e) {
            e.preventDefault();
            closeBulletEnhancementModal();
        });
    } else {
        console.error("#enhance-modal-backdrop not found");
    }

    // Radio button listeners for job description toggle
    const enhancementAtsRadio = document.getElementById('enhancement-ats');
    const enhancementGeneralRadio = document.getElementById('enhancement-general');
    const jobDescriptionContainer = document.getElementById('job-description-container');

    function toggleJobDescription() {
        if (jobDescriptionContainer) {
            jobDescriptionContainer.classList.toggle('hidden', !enhancementAtsRadio?.checked);
        }
    }

    if (enhancementAtsRadio) enhancementAtsRadio.addEventListener('change', toggleJobDescription);
    if (enhancementGeneralRadio) enhancementGeneralRadio.addEventListener('change', toggleJobDescription);
    toggleJobDescription();
}

function moveModalToBody(modalId) {
    const modal = document.getElementById(modalId);
    if (modal && modal.parentElement && !modal.parentElement.isSameNode(document.body)) {
        document.body.appendChild(modal);
    }
}

// ======= Bullet Quality Check ======
function checkBulletQuality(textarea) {
    const text = textarea.value.trim();
    let score = 0;
    const feedback = [];
    const actionVerbs = ["Achieved", "Analyzed", "Built", "Coordinated", "Created", "Delivered",
                      "Designed", "Developed", "Established", "Generated", "Implemented",
                      "Improved", "Led", "Managed", "Optimized", "Reduced", "Spearheaded",
                      "Launched", "Executed", "Streamlined", "Transformed", "Increased"];

    if (text) {
        // Action Verb Check
        const firstWord = text.split(' ')[0];
        if (firstWord) {
            const startsWithAction = actionVerbs.some(verb =>
                firstWord.toLowerCase() === verb.toLowerCase()
            );
            if (startsWithAction) {
                score += 2;
            } else {
                feedback.push("Start with a strong action verb");
            }
        } else {
            feedback.push("Start with a strong action verb");
        }

        // Metrics Check
        const hasNumbers = /\d/.test(text);
        const hasPercentOrMoney = /%|\$|€|£|¥|₹/.test(text);
        if (hasNumbers) {
            score += 1;
            if (hasPercentOrMoney) { score += 1; }
        } else {
            feedback.push("Add measurable results (numbers, %, $)");
        }

        // Length Check
        if (text.length >= 80 && text.length <= 150) {
            score += 2;
        } else if (text.length > 0 && text.length < 80) {
            feedback.push("Consider adding more detail/context");
            score += 1;
        } else if (text.length > 150) {
            feedback.push("Try to be more concise");
            score += 1;
        }
    }

    // Prepare UI data
    let resultHtml = '';
    if (score >= 5) {
        resultHtml = '<span class="text-green-600 font-semibold">Excellent! ★★★★★</span>';
    } else if (score >= 4) {
        resultHtml = '<span class="text-lime-600 font-medium">Good ★★★★☆</span>';
    } else if (score >= 3) {
        resultHtml = '<span class="text-yellow-600">Average ★★★☆☆</span>';
    } else if (score >= 2) {
        resultHtml = '<span class="text-yellow-600">Average ★★☆☆☆</span>';
    } else {
        resultHtml = '<span class="text-red-500">Needs Improvement ★☆☆☆☆</span>';
    }

    if (feedback.length > 0 && text) {
        resultHtml += ` <span class="text-gray-500 italic ml-1">Tip: ${feedback[0]}</span>`;
    }

    const len = textarea.value.length;
    let charCounterClass = 'current';
    let charMaxClass = 'max';

    if (len >= 80 && len <= 150) {
        charCounterClass = 'current text-green-600';
        charMaxClass = 'max text-green-600';
    } else if (len > 0 && len < 80) {
        charCounterClass = 'current text-yellow-600';
        charMaxClass = 'max text-yellow-600';
    } else if (len > 150) {
        charCounterClass = 'current text-red-600';
        charMaxClass = 'max text-red-600';
    }

    return {
        score: score,
        qualityHtml: resultHtml,
        charCount: len,
        charCounterClass: charCounterClass,
        charMaxClass: charMaxClass
    };
}

function updateBulletQualityUI(textarea) {
    if (!textarea) return;

    const qualityInfo = checkBulletQuality(textarea);
    const bulletRow = textarea.closest('.bullet-point-row');
    if (!bulletRow) {
        console.warn("Could not find parent .bullet-point-row for textarea", textarea);
        return;
    }

    const qualityDiv = bulletRow.querySelector('.bullet-quality');
    if (qualityDiv) {
        qualityDiv.innerHTML = qualityInfo.qualityHtml;
    } else {
        console.warn("Could not find .bullet-quality in row");
    }

    const charCounterSpan = bulletRow.querySelector('.char-counter .current');
    const charMaxSpan = bulletRow.querySelector('.char-counter .max');

    if (charCounterSpan) {
        charCounterSpan.textContent = qualityInfo.charCount;
        charCounterSpan.className = qualityInfo.charCounterClass;
    } else {
        console.warn("Could not find .char-counter .current in row");
    }

    if (charMaxSpan) {
        charMaxSpan.className = qualityInfo.charMaxClass;
    } else {
        console.warn("Could not find .char-counter .max in row");
    }
}

// ======= Bullet Generation Modal Functions =======
// These are your existing functions for bullet generation
// You mentioned not to change them since they're working fine
function openBulletGenerationModal(parentIndex) {
    // Your existing code
    console.log("Opening bullet generation modal for index:", parentIndex);
    // ... rest of your existing function
}

function closeBulletGenerationModal() {
    // Your existing code
    const modal = document.getElementById('bullet-generation-modal');
    if (modal) {
        modal.classList.add('hidden');
        modal.style.display = 'none';
        document.body.classList.remove('overflow-hidden');
    }
}

function resetBulletGenerationModal() {
    // Your existing code
    // ... rest of your existing function
}

function generateBullets() {
    // Your existing code for bullet generation
    // ... rest of your existing function
}

function applyGeneratedBullets() {
    // Your existing code for applying generated bullets
    // ... rest of your existing function
}

// ======= Bullet Enhancement Modal Functions =======
function openBulletEnhancementModal(bulletTextarea) {
    console.log("Opening enhancement modal for bullet textarea:", bulletTextarea.id);
    const modal = document.getElementById('bullet-enhancement-modal');
    if (!modal) {
        console.error("Enhancement modal not found!");
        return;
    }

    const bulletText = bulletTextarea.value.trim();
    if (!bulletText) {
        alert('Please write something in the bullet point first.');
        return;
    }

    // Store the textarea ID directly in the modal for later use
    document.getElementById('bullet-textarea-id').value = bulletTextarea.id;
    document.getElementById('original-bullet').value = bulletText;

    // Reset modal state
    document.getElementById('enhancement-general').checked = true;
    document.getElementById('enhance-engine-chatgpt').checked = true;
    document.getElementById('job-description-container').classList.add('hidden');
    document.getElementById('job-description').value = '';
    document.getElementById('enhancement-loading').classList.add('hidden');
    document.getElementById('enhancement-result').classList.add('hidden');
    document.getElementById('enhanced-bullet').value = '';
    document.getElementById('enhancement-quality').innerHTML = '';
    document.getElementById('apply-enhancement-btn').classList.add('hidden');
    document.getElementById('enhance-bullet-btn').classList.remove('hidden');
    document.getElementById('enhance-bullet-btn').disabled = false;

    // Show the modal
    modal.classList.remove('hidden');
    modal.style.display = 'block';
    document.body.classList.add('overflow-hidden');
}

function closeBulletEnhancementModal() {
    const modal = document.getElementById('bullet-enhancement-modal');
    if (modal) {
        modal.classList.add('hidden');
        modal.style.display = 'none';
        document.body.classList.remove('overflow-hidden');
    }
}

function enhanceBullet() {
    console.log("Enhancing bullet point...");
    const loadingEl = document.getElementById('enhancement-loading');
    const resultEl = document.getElementById('enhancement-result');
    const enhanceBtn = document.getElementById('enhance-bullet-btn');
    const applyBtn = document.getElementById('apply-enhancement-btn');
    const enhancedBulletTextarea = document.getElementById('enhanced-bullet');

    if(loadingEl) loadingEl.classList.remove('hidden');
    if(resultEl) resultEl.classList.add('hidden');
    if(enhanceBtn) enhanceBtn.disabled = true;

    const originalBullet = document.getElementById('original-bullet').value;
    const enhancementType = document.querySelector('input[name="enhancement-type"]:checked').value;
    const aiEngine = document.querySelector('input[name="enhance-engine"]:checked').value;
    const jobDescription = document.getElementById('job-description').value;

    // Prepare request parameters
    const requestData = {
        bullet_text: originalBullet,
        enhancement_type: enhancementType,
        ai_engine: aiEngine,
        job_description: jobDescription
    };

    // Build the URL with query parameters
    const url = "/job/ai/enhance-bullet/"; // Update with the correct URL
    const params = new URLSearchParams(requestData).toString();

    // Get the CSRF token
    const csrftoken = getCookie('csrftoken');

    // Use fetch for the AJAX request instead of htmx
    console.log("Sending enhancement request:", requestData);

    fetch(`${url}?${params}`, {
        method: 'GET',
        headers: {
            'X-Requested-With': 'XMLHttpRequest',
            'X-CSRFToken': csrftoken
        }
    })
    .then(response => {
        if (!response.ok) {
            throw new Error(`HTTP error! Status: ${response.status}`);
        }
        return response.text();
    })
    .then(enhancedText => {
        console.log("Enhancement request successful. Response:", enhancedText);

        // Update the textarea value
        if (enhancedBulletTextarea) {
            enhancedBulletTextarea.value = enhancedText;
        }

        // Update UI state
        if (enhancedText && enhancedText.trim() !== "") {
            if(resultEl) resultEl.classList.remove('hidden');
            if(applyBtn) applyBtn.classList.remove('hidden');

            // Update quality display
            const tempTextarea = document.createElement('textarea');
            tempTextarea.value = enhancedText;
            const quality = checkBulletQuality(tempTextarea);
            document.getElementById('enhancement-quality').innerHTML = quality.qualityHtml;
        } else {
            document.getElementById('enhancement-quality').innerHTML =
                '<span class="text-orange-500">Enhancement returned empty result.</span>';
            if(resultEl) resultEl.classList.remove('hidden');
            if(applyBtn) applyBtn.classList.add('hidden');
        }

        if(enhanceBtn) enhanceBtn.disabled = false;
        if(loadingEl) loadingEl.classList.add('hidden');
    })
    .catch(error => {
        console.error("Enhancement request failed:", error);
        if(enhancedBulletTextarea) {
            enhancedBulletTextarea.value = `Error enhancing bullet: ${error.message}. Please try again.`;
        }
        document.getElementById('enhancement-quality').innerHTML = '<span class="text-red-500">Error</span>';
        if(loadingEl) loadingEl.classList.add('hidden');
        if(resultEl) resultEl.classList.remove('hidden');
        if(applyBtn) applyBtn.classList.add('hidden');
        if(enhanceBtn) enhanceBtn.disabled = false;
    });
}

function applyEnhancement() {
    console.log("Applying enhancement to form");
    const textareaId = document.getElementById('bullet-textarea-id').value;
    const enhancedBullet = document.getElementById('enhanced-bullet').value;
    const bulletTextarea = document.getElementById(textareaId);

    if (bulletTextarea && enhancedBullet) {
        bulletTextarea.value = enhancedBullet;

        // Find the closest bullet-point-row for visual feedback
        const bulletRow = bulletTextarea.closest('.bullet-point-row');
        if (bulletRow) {
            bulletRow.classList.add('bg-green-50', 'border', 'border-green-300');
            setTimeout(() => {
                bulletRow.classList.remove('bg-green-50', 'border', 'border-green-300');
            }, 1500);
        }

        closeBulletEnhancementModal();
        console.log("Enhancement applied successfully");
    } else {
        console.error("Could not find bullet textarea or enhanced text");
        alert("Error applying enhancement: could not find target field or enhancement text.");
    }
}

// Function to add a new bullet point
function addBulletPoint(parentIndex) {
    console.log("Adding bullet point for parent:", parentIndex);
    const container = document.getElementById(`bullet_points_container_experience_set-${parentIndex}`);

    if (!container) {
        console.error("Bullet container not found:", `bullet_points_container_experience_set-${parentIndex}`);
        return;
    }

    // Get the current count of bullet points
    const totalFormsInput = document.getElementById(`id_experience_set-${parentIndex}-bullet_points-TOTAL_FORMS`);
    if (!totalFormsInput) {
        console.error("TOTAL_FORMS input not found");
        return;
    }

    const bulletIndex = parseInt(totalFormsInput.value);

    // Create a new bullet point with the correct naming scheme
    const bulletHtml = `
    <div class="bullet-point-row flex items-center gap-x-2 group p-1 rounded-md mb-1">
        <div class="mt-1 text-blue-600 dark:text-blue-400 font-bold text-lg">•</div>
        <div class="flex-1 min-w-0">
            <textarea 
                class="block w-full px-3 py-1.5 border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm min-h-[50px]" 
                placeholder="e.g., Led a team of 5 to..." 
                id="id_experience_set-${parentIndex}-bullet_points-${bulletIndex}-text" 
                name="experience_set-${parentIndex}-bullet_points-${bulletIndex}-text"
            ></textarea>
            <div class="hidden">
                <input type="checkbox" name="experience_set-${parentIndex}-bullet_points-${bulletIndex}-DELETE" id="id_experience_set-${parentIndex}-bullet_points-${bulletIndex}-DELETE">
            </div>
        </div>
        <div class="flex flex-col space-y-1 items-center ml-2">
            <button type="button"
                class="enhance-main-form-bullet-btn p-1 h-7 w-7 flex items-center justify-center border border-indigo-500 dark:border-indigo-600 text-indigo-500 dark:text-indigo-400 rounded-full hover:bg-indigo-500 dark:hover:bg-indigo-600 hover:text-white dark:hover:text-gray-100 transition-colors opacity-70 group-hover:opacity-100 focus:outline-none focus:ring-2 focus:ring-indigo-500"
                title="Enhance with AI"
                data-textarea-id="id_experience_set-${parentIndex}-bullet_points-${bulletIndex}-text"
                data-experience-index="${parentIndex}">
                <i class="fa-solid fa-wand-magic-sparkles text-xs"></i>
            </button>
            <button type="button"
                class="p-1 h-7 w-7 flex items-center justify-center border border-red-500 dark:border-red-600 text-red-500 dark:text-red-400 rounded-full hover:bg-red-500 dark:hover:bg-red-600 hover:text-white dark:hover:text-gray-100 transition-colors opacity-70 group-hover:opacity-100 focus:outline-none focus:ring-2 focus:ring-red-500"
                onclick="removeManualBulletPoint(this, 'experience_set-${parentIndex}-bullet_points-${bulletIndex}')">
                <i class="fa-solid fa-times text-xs"></i>
            </button>
        </div>
    </div>
    `;

    // Add the bullet to the container
    container.insertAdjacentHTML('beforeend', bulletHtml);

    // Update the total form count
    totalFormsInput.value = (bulletIndex + 1).toString();

    // Get the newly added elements
    const newRow = container.lastElementChild;
    const textarea = newRow.querySelector('textarea');
    const enhanceBtn = newRow.querySelector('.enhance-main-form-bullet-btn');

    // Add event listener to the enhance button
    if (enhanceBtn) {
        enhanceBtn.addEventListener('click', function(e) {
            e.preventDefault();
            const textareaId = this.getAttribute('data-textarea-id');
            const bulletTextarea = document.getElementById(textareaId);
            if (bulletTextarea) {
                openBulletEnhancementModal(bulletTextarea);
            }
        });
    }

    // Focus the new textarea
    if (textarea) {
        textarea.focus();
    }

    // Visual feedback
    newRow.classList.add('bg-green-50');
    setTimeout(() => {
        newRow.classList.remove('bg-green-50');
    }, 1500);
}

// Function to remove a bullet point
function removeManualBulletPoint(button, formPrefix) {
    console.log("Removing bullet point:", formPrefix);

    // Find the bullet row
    const bulletRow = button.closest('.bullet-point-row');
    if (!bulletRow) {
        console.error("Could not find bullet row parent");
        return;
    }

    // Mark for deletion if this is an existing bullet (has an ID)
    const deleteCheckbox = bulletRow.querySelector(`input[name="${formPrefix}-DELETE"]`);
    if (deleteCheckbox) {
        deleteCheckbox.checked = true;

        // Hide the row
        bulletRow.style.display = 'none';
    } else {
        // Just remove from DOM if it's a new bullet
        bulletRow.remove();
    }

    // Reindex remaining bullets would go here if needed
}

// Function to toggle the end date field based on "currently work here" checkbox
function toggleEndDate(checkboxElement) {
    const parentExperienceEntry = checkboxElement.closest('.experience-entry');
    if (!parentExperienceEntry) return;

    const endDateContainer = parentExperienceEntry.querySelector('.end-date-container');
    if (!endDateContainer) return;

    const endDateInput = endDateContainer.querySelector('input[type="date"]');
    if (endDateInput) {
        if (checkboxElement.checked) {
            endDateInput.disabled = true;
            endDateInput.value = '';
            endDateInput.classList.add('bg-gray-100', 'dark:bg-gray-800', 'text-gray-500', 'dark:text-gray-400', 'cursor-not-allowed');
        } else {
            endDateInput.disabled = false;
            endDateInput.classList.remove('bg-gray-100', 'dark:bg-gray-800', 'text-gray-500', 'dark:text-gray-400', 'cursor-not-allowed');
        }
    }
}

// Helper function to get CSRF token from cookies
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}