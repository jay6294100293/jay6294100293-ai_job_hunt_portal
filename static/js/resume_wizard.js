// static/js/resume_wizard.js

// --- CSRF Token Helper ---
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
const csrftoken = getCookie('csrftoken'); // Make it globally available if needed by other scripts

// --- Generic Modal Control (if using Alpine.js events from base_authenticated.html) ---
window.addEventListener('open-modal', event => {
    const modalId = event.detail;
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.classList.remove('hidden');
        // Optional: Add body overflow hidden, focus trapping for accessibility
        document.body.classList.add('overflow-hidden');

        // Auto-focus on the first focusable element in the modal
        const focusableElements = modal.querySelectorAll(
            'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
        );
        if (focusableElements.length > 0) {
            focusableElements[0].focus();
        }
    }
});

window.addEventListener('close-modal', event => {
    const modalId = event.detail;
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.classList.add('hidden');
        document.body.classList.remove('overflow-hidden');
    }
});

// --- Generic Simple Formset Management ---
// (For Skills, Education, Certifications, Languages, Custom Sections)
function initializeSimpleFormset(options) {
    const formsetContainer = document.getElementById(options.formsetContainerId);
    if (!formsetContainer) return;

    const formsContainer = document.getElementById(options.formsContainerId);
    const addButton = document.getElementById(options.addButtonId);
    const emptyFormHtml = document.getElementById(options.emptyFormTemplateId)?.innerHTML;
    const totalFormsInput = formsetContainer.querySelector(`input[name="${options.formsetPrefix}-TOTAL_FORMS"]`);

    if (!formsContainer || !addButton || !emptyFormHtml || !totalFormsInput) {
        console.error(`Formset ${options.formsetPrefix}: Missing elements.`);
        return;
    }

    addButton.addEventListener('click', function () {
        const newIndex = parseInt(totalFormsInput.value);
        let newFormWrappedHtml = emptyFormHtml.replace(/__prefix__/g, newIndex);
        // Replace any custom index placeholders like {{ skill_index }} if used in x-data
        if(options.itemIndexPlaceholder) {
             newFormWrappedHtml = newFormWrappedHtml.replace(new RegExp(options.itemIndexPlaceholder, 'g'), newIndex);
        }


        const tempDiv = document.createElement('div');
        tempDiv.innerHTML = newFormWrappedHtml;
        const newFormElement = tempDiv.firstElementChild;

        if (newFormElement) {
            newFormElement.classList.remove('hidden');
            if(options.itemDataAttributePrefix) {
                newFormElement.setAttribute(`data-${options.itemDataAttributePrefix}-form-index`, newIndex);
            }

            const counterSpan = newFormElement.querySelector(`.${options.itemCounterClass}`);
            if(counterSpan) counterSpan.textContent = newIndex + 1;

            formsContainer.appendChild(newFormElement);
            totalFormsInput.value = newIndex + 1;

            if (window.Alpine && newFormElement.querySelector('[x-data]')) {
                // Refresh Alpine for the new element
                // This is a bit more involved as direct re-init of a tree part can be tricky.
                // Often, it's better if Alpine can react to new DOM elements being added
                // or if x-data is on the form element itself and initTree is called.
                // For unique x-data states like in skill_form_row, ensure the x-data attribute
                // string itself is updated with the newIndex before Alpine initializes it.

                // A simple re-evaluation if Alpine is expected to pick it up
                 newFormElement.querySelectorAll('[x-data]').forEach(el => {
                    let xDataVal = el.getAttribute('x-data');
                    xDataVal = xDataVal.replace(/__prefix__/g, newIndex);
                    if(options.itemIndexPlaceholder) {
                         xDataVal = xDataVal.replace(new RegExp(options.itemIndexPlaceholder, 'g'), newIndex);
                    }
                    el.setAttribute('x-data', xDataVal);
                    window.Alpine.initTree(el); // Initialize Alpine for this new element
                });
            }
            if (options.onFormAddedCallback && typeof options.onFormAddedCallback === 'function') {
                options.onFormAddedCallback(newFormElement, newIndex);
            }
        } else {
            console.error(`Failed to create new form for ${options.formsetPrefix} from template.`);
        }
    });

    formsContainer.addEventListener('click', function (e) {
        const removeButton = e.target.closest(`.${options.removeButtonClass}`);
        if (removeButton) {
            const formToRemove = removeButton.closest(`.${options.itemContainerClass}`);
            const deleteCheckbox = formToRemove.querySelector('input[type="checkbox"][name$="-DELETE"]');
            if (deleteCheckbox) {
                deleteCheckbox.checked = true;
                formToRemove.style.display = 'none';
                 let feedback = formToRemove.querySelector('.deletion-feedback');
                if (!feedback) {
                    feedback = document.createElement('p');
                    feedback.className = 'deletion-feedback text-xs text-red-700 dark:text-red-300 p-2 text-center font-semibold';
                    formToRemove.appendChild(feedback);
                }
                feedback.textContent = `This ${options.itemDataAttributePrefix || 'item'} will be deleted upon saving.`;
            } else {
                formToRemove.remove();
            }
        }
    });

    // Initialize for existing forms
     formsContainer.querySelectorAll(`.${options.itemContainerClass}`).forEach((formElement) => {
        const index = formElement.dataset[`${options.itemDataAttributePrefix}FormIndex`] ||
                      (formElement.querySelector('input[name$="-id"]') ?
                       formElement.querySelector('input[name$="-id"]').name.match(/-(\d+)-/)[1] :
                       '0'); // Fallback logic for index might be needed

        if (options.onFormAddedCallback && typeof options.onFormAddedCallback === 'function') {
            options.onFormAddedCallback(formElement, index);
        }
        // Initialize Alpine for existing complex forms (like skill with conditional fields)
        if (window.Alpine && formElement.querySelector('[x-data]')) {
             formElement.querySelectorAll('[x-data]').forEach(el => {
                let xDataVal = el.getAttribute('x-data');
                // Check if the index part of x-data (e.g., skillCategory_0) needs to be set if not already
                // This is tricky if it was rendered by Django with correct index.
                // The main concern is for __prefix__ forms being cloned.
                window.Alpine.initTree(el);
            });
        }
    });
}


// --- Character Count (Example, if used from your original resume_wizard.js) ---
function updateCharCount(textarea, targetElementId) {
    const target = document.getElementById(targetElementId);
    if (textarea && target) {
        const currentLength = textarea.value.length;
        // You might want to define min/max via data attributes on the textarea
        // For now, just display current length
        target.textContent = `${currentLength} characters`;
    }
}

// --- Preview Resume (Example, if used from your original resume_wizard.js) ---
// This would require a backend endpoint to render a temporary preview
function previewResume(previewUrl, formId) {
    const form = document.getElementById(formId);
    if (!form) {
        console.error('Form not found for preview:', formId);
        return;
    }
    const formData = new FormData(form);
    const modal = document.getElementById('preview-modal'); // Assuming you have a modal with this ID
    const modalContent = document.getElementById('preview-modal-content');

    if (!modal || !modalContent) {
        console.error('Preview modal or content area not found.');
        return;
    }

    modalContent.innerHTML = '<div class="p-8 text-center"><i class="fas fa-spinner fa-spin text-3xl text-primary-500"></i><p class="mt-2 text-sm text-slate-500">Loading preview...</p></div>';
    openModal('preview-modal');

    fetch(previewUrl, {
        method: 'POST',
        headers: {
            'X-CSRFToken': csrftoken, // Ensure csrftoken is available
            // 'Content-Type': 'application/x-www-form-urlencoded', // For FormData, browser sets it with boundary
        },
        body: formData
    })
    .then(response => {
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        return response.text();
    })
    .then(html => {
        modalContent.innerHTML = html;
    })
    .catch(error => {
        console.error('Error fetching resume preview:', error);
        modalContent.innerHTML = `<div class="p-4 text-red-600">Error loading preview: ${error.message}</div>`;
    });
}

// Event listeners for any character count textareas (if used)
// document.querySelectorAll('textarea[data-char-count-target]').forEach(textarea => {
//    const targetId = textarea.dataset.charCountTarget;
//    updateCharCount(textarea, targetId); // Initial count
//    textarea.addEventListener('input', () => updateCharCount(textarea, targetId));
// });

// Add event listener for preview button if it exists
// const previewButton = document.getElementById('preview-resume-button');
// if (previewButton) {
//    previewButton.addEventListener('click', function() {
//        const previewUrl = this.dataset.previewUrl; // e.g., data-preview-url="{% url '...' %}"
//        const formId = this.dataset.formId;       // e.g., data-form-id="experience-formset-container"
//        if (previewUrl && formId) {
//            previewResume(previewUrl, formId);
//        }
//    });
// }

// // static/js/resume_wizard.js
//
// // Resume preview functionality
// function previewResume() {
//     const modal = document.getElementById('preview-modal');
//     if (!modal) {
//         console.error('Preview modal not found');
//         return;
//     }
//     modal.classList.remove('hidden');
//     document.body.classList.add('overflow-hidden');
//
//     const form = document.getElementById('resume-form');
//     if (!form) {
//         console.error('Resume form (#resume-form) not found.');
//         if (modal) modal.classList.add('hidden');
//         document.body.classList.remove('overflow-hidden');
//         return;
//     }
//     const formData = new FormData(form);
//     const modalContent = document.getElementById('preview-modal-content');
//
//     modalContent.innerHTML = `<div class="flex justify-center items-center p-8">
//         <div class="border-gray-300 h-12 w-12 animate-spin rounded-full border-4 border-t-blue-600"></div>
//     </div>`;
//
//     const csrfTokenElement = document.querySelector('[name=csrfmiddlewaretoken]');
//     if (!csrfTokenElement) {
//         console.error('CSRF token not found');
//         modalContent.innerHTML = '<div class="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded relative" role="alert"><strong class="font-bold">Error:</strong><span class="block sm:inline"> CSRF token missing.</span></div>';
//         return;
//     }
//     const csrfToken = csrfTokenElement.value;
//
//     fetch('/job/preview-current-resume/', { // URL from your job_portal_url.py
//         method: 'POST',
//         body: formData,
//         headers: {
//             'X-CSRFToken': csrfToken,
//             'X-Requested-With': 'XMLHttpRequest'
//         }
//     })
//     .then(response => {
//         if (!response.ok) {
//             throw new Error(`Network response was not ok: ${response.statusText}`);
//         }
//         return response.text();
//     })
//     .then(html => {
//         if (modalContent) {
//             modalContent.innerHTML = html;
//         }
//     })
//     .catch(error => {
//         console.error('Error fetching preview:', error);
//         if (modalContent) {
//             modalContent.innerHTML = `<div class="bg-red-100 border-l-4 border-red-500 text-red-700 p-4" role="alert"><p class="font-bold">Error Loading Preview</p><p>${error.message}. Please try again.</p></div>`;
//         }
//     });
// }
//
// function closePreviewModal() {
//     const modal = document.getElementById('preview-modal');
//     if (modal) {
//         modal.classList.add('hidden');
//     }
//     document.body.classList.remove('overflow-hidden');
// }
//
// function toggleMoreProfiles() {
//     const moreProfiles = document.getElementById('more-profiles');
//     const button = document.getElementById('add-more-profiles');
//     if (!moreProfiles || !button) return;
//
//     if (moreProfiles.classList.contains('hidden')) {
//         moreProfiles.classList.remove('hidden');
//         moreProfiles.classList.add('animate-fade-in'); // Ensure this animation is defined in your CSS
//         button.innerHTML = '<i class="fa-solid fa-minus mr-2"></i> Show fewer profiles';
//     } else {
//         moreProfiles.classList.add('hidden');
//         button.innerHTML = '<i class="fa-solid fa-plus mr-2"></i> Add more profiles';
//     }
// }
//
// // Add form row (e.g., for experiences, education etc.)
// function addFormRow(type, containerId, countFieldId) { // countFieldId is the ID of the TOTAL_FORMS input
//     const totalFormsInput = document.getElementById(countFieldId);
//     if (!totalFormsInput) {
//         console.error(`Total forms input field '${countFieldId}' not found.`);
//         return;
//     }
//     let currentIndex = parseInt(totalFormsInput.value);
//
//     const container = document.getElementById(containerId);
//     if (!container) {
//         console.error(`Container '${containerId}' not found.`);
//         return;
//     }
//
//     const loadingRow = document.createElement('div');
//     loadingRow.className = 'flex justify-center p-4 form-row-loading';
//     loadingRow.innerHTML = '<div class="border-gray-300 h-8 w-8 animate-spin rounded-full border-4 border-t-blue-600"></div>';
//     container.appendChild(loadingRow);
//
//     fetch(`/job/htmx/add-form-row/?form_type=${type}&index=${currentIndex}`, { // URL from your job_portal_url.py
//         headers: { 'X-Requested-With': 'XMLHttpRequest' }
//     })
//     .then(response => {
//         loadingRow.remove();
//         if (!response.ok) {
//             throw new Error(`Network response was not ok for addFormRow: ${response.statusText}`);
//         }
//         return response.text();
//     })
//     .then(html => {
//         const emptyStateMsg = container.querySelector('.empty-state-message');
//         if (emptyStateMsg) emptyStateMsg.remove();
//
//         container.insertAdjacentHTML('beforeend', html); // HTML for the new form row from server
//         totalFormsInput.value = currentIndex + 1; // Increment TOTAL_FORMS
//
//         const newRow = container.lastElementChild;
//         if (newRow && typeof newRow.scrollIntoView === 'function') {
//             newRow.scrollIntoView({ behavior: 'smooth', block: 'center' });
//             newRow.classList.add('ring-2', 'ring-blue-500', 'ring-offset-2', 'transition-all', 'duration-300');
//             setTimeout(() => newRow.classList.remove('ring-2', 'ring-blue-500', 'ring-offset-2'), 1500);
//
//             // If the newly added row is an experience form, its buttons will be handled by event delegation
//             // Ensure the HTML returned by the server for the new row includes data-index attribute for .experience-entry
//             // and .open-experience-ai-modal / .enhance-main-form-bullet-btn buttons with their data attributes.
//             if (type === 'experience' && newRow.classList.contains('experience-entry')) {
//                  // If newRow HTML doesn't set data-index from server, set it here:
//                  if (!newRow.hasAttribute('data-index')) {
//                     newRow.dataset.index = currentIndex;
//                  }
//                  // Enhance buttons within this new row will be handled by the delegated listener
//             }
//         }
//     })
//     .catch(error => {
//         console.error('Error adding form row:', error);
//         if (loadingRow.parentElement) loadingRow.remove();
//         const errorMsg = document.createElement('div');
//         errorMsg.className = 'bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded relative my-3';
//         errorMsg.textContent = `Error adding new entry: ${error.message}. Please try again.`;
//         container.appendChild(errorMsg);
//         setTimeout(() => errorMsg.remove(), 3000);
//     });
// }
//
// // Remove form row (e.g., an entire experience block)
// function removeFormRow(button) {
//     const row = button.closest('.experience-entry'); // Class from your experience.html
//     if (!row) {
//         console.error("Could not find '.experience-entry' to remove.");
//         return;
//     }
//     const deleteCheckbox = row.querySelector('input[type="checkbox"][name$="-DELETE"]');
//     if (deleteCheckbox) {
//         deleteCheckbox.checked = true;
//         row.classList.add('hidden');
//     } else {
//         row.style.transition = 'all 0.3s ease';
//         row.style.opacity = '0';
//         row.style.maxHeight = '0px';
//         row.style.paddingTop = '0px';
//         row.style.paddingBottom = '0px';
//         row.style.marginTop = '0px';
//         row.style.marginBottom = '0px';
//         row.style.overflow = 'hidden';
//         setTimeout(() => {
//             row.remove();
//         }, 300);
//     }
// }
//
// // Add bullet point manually to an experience
// // Called by inline onclick="addBulletPoint('{{ forloop.counter0 }}')" in experience.html
// function addBulletPoint(parentExperienceIndex) {
//     const container = document.getElementById(`bullet_points_container_experience_set-${parentExperienceIndex}`);
//     if (!container) {
//         console.error(`Bullet container (bullet_points_container_experience_set-${parentExperienceIndex}) not found.`);
//         return;
//     }
//     const bulletTotalFormsInput = document.getElementById(`id_experience_set-${parentExperienceIndex}-bullet_points-TOTAL_FORMS`);
//     if (!bulletTotalFormsInput) {
//         console.error(`TOTAL_FORMS input for bullets (id_experience_set-${parentExperienceIndex}-bullet_points-TOTAL_FORMS) not found.`);
//         return;
//     }
//     let bulletIndex = parseInt(bulletTotalFormsInput.value);
//
//     const newRow = document.createElement('div');
//     newRow.className = 'bullet-point-row flex items-center gap-x-2 group p-1 rounded-md transition-colors mb-2'; // items-center
//     const textareaId = `id_experience_set-${parentExperienceIndex}-bullet_points-${bulletIndex}-text`;
//     newRow.innerHTML = `
//         <div class="mt-1 text-blue-600 font-bold text-lg">•</div>
//         <div class="flex-1 min-w-0">
//             <input type="hidden" name="experience_set-${parentExperienceIndex}-bullet_points-${bulletIndex}-id" id="id_experience_set-${parentExperienceIndex}-bullet_points-${bulletIndex}-id">
//             <textarea class="block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm min-h-[50px]"
//                 id="${textareaId}"
//                 name="experience_set-${parentExperienceIndex}-bullet_points-${bulletIndex}-text"
//                 placeholder="Describe your achievement..."></textarea>
//             <input type="hidden" name="experience_set-${parentExperienceIndex}-bullet_points-${bulletIndex}-DELETE" id="id_experience_set-${parentExperienceIndex}-bullet_points-${bulletIndex}-DELETE" class="hidden">
//         </div>
//         <div class="flex flex-col space-y-1 items-center ml-2">
//             <button type="button" class="enhance-main-form-bullet-btn p-1 h-7 w-7 flex items-center justify-center border border-indigo-500 text-indigo-500 rounded-full hover:bg-indigo-500 hover:text-white transition-colors opacity-70 group-hover:opacity-100 focus:outline-none focus:ring-2 focus:ring-indigo-500"
//                     title="Enhance with AI"
//                     data-textarea-id="${textareaId}"
//                     data-experience-index="${parentExperienceIndex}">
//                 <i class="fa-solid fa-wand-magic-sparkles text-xs"></i>
//             </button>
//             <button type="button" class="p-1 h-7 w-7 flex items-center justify-center border border-red-500 text-red-500 rounded-full hover:bg-red-500 hover:text-white transition-colors opacity-70 group-hover:opacity-100 focus:outline-none focus:ring-2 focus:ring-red-500"
//                     onclick="removeManualBulletPoint(this, 'experience_set-${parentExperienceIndex}-bullet_points-${bulletIndex}')"> {/* Pass full prefix of this bullet */}
//                 <i class="fa-solid fa-times text-xs"></i>
//             </button>
//         </div>
//     `;
//     container.appendChild(newRow);
//     bulletTotalFormsInput.value = bulletIndex + 1;
//     const textarea = newRow.querySelector('textarea');
//     if (textarea) textarea.focus();
// }
//
// // Remove bullet point (manually added)
// function removeManualBulletPoint(button, bulletFormPrefix) { // bulletFormPrefix is e.g., experience_set-0-bullet_points-0
//     const row = button.closest('.bullet-point-row');
//     if (!row) return;
//     const idInput = row.querySelector(`input[name="${bulletFormPrefix}-id"]`);
//     const deleteCheckbox = row.querySelector(`input[name="${bulletFormPrefix}-DELETE"]`);
//     if (idInput && idInput.value && deleteCheckbox) { // Existing bullet, mark for deletion
//         deleteCheckbox.checked = true;
//         row.classList.add('hidden');
//     } else { // New bullet, just remove from DOM
//         row.remove();
//     }
// }
//
// function updateCharCount(textarea, countDisplay) {
//     if (!textarea || !countDisplay) return;
//     const count = textarea.value.length;
//     const minCount = parseInt(textarea.dataset.minCount || "0");
//     countDisplay.textContent = count;
//     if (minCount > 0) {
//         countDisplay.classList.toggle('text-red-600', count < minCount);
//         countDisplay.classList.toggle('text-green-600', count >= minCount);
//     }
// }
//
// // ===== AI BULLET GENERATION FUNCTIONS (No Employer) =====
//
// function openAiBulletModal(event) {
//     const button = event.currentTarget;
//     const parentExperienceForm = button.closest('.experience-entry');
//     if (!parentExperienceForm) {
//         console.error("Could not find parent experience form (.experience-entry) for AI modal.");
//         return;
//     }
//     const experienceIndex = parentExperienceForm.dataset.index;
//     if (experienceIndex === undefined) {
//         console.error("Could not determine experience index (data-index attribute missing on .experience-entry).");
//         return;
//     }
//
//     const modal = document.getElementById('bullet-generation-modal'); // ID from your modal HTML file
//     if (!modal) {
//         console.error("AI Bullet Generation Modal (#bullet-generation-modal) not found.");
//         return;
//     }
//     modal.dataset.parentExperienceIndex = experienceIndex;
//
//     const errorMessageDiv = modal.querySelector('.error-message');
//     const loadingSpinnerContainer = modal.querySelector('.loading-spinner-container');
//     const generatedBulletsDiv = modal.querySelector('#generatedExperienceBulletsContainer');
//
//     if (errorMessageDiv) {
//         errorMessageDiv.textContent = '';
//         errorMessageDiv.classList.add('hidden');
//     }
//     if (loadingSpinnerContainer) loadingSpinnerContainer.classList.add('hidden');
//     if (generatedBulletsDiv) generatedBulletsDiv.innerHTML = '';
//
//     // Populate modal fields
//     const jobTitleInput = parentExperienceForm.querySelector(`input[name="experience_set-${experienceIndex}-job_title"]`);
//     const modalJobTitleField = modal.querySelector('#ai-experience-job-title');
//     if (jobTitleInput && modalJobTitleField) {
//         modalJobTitleField.value = jobTitleInput.value;
//     } else {
//         console.warn(`Job title input not found for experience ${experienceIndex}`);
//         if (modalJobTitleField) modalJobTitleField.value = '';
//     }
//
//     const targetJobTitleGlobalInput = document.getElementById('target-job-title-for-ai'); // A global hidden input on your page
//     const modalTargetJobTitleField = modal.querySelector('#ai-experience-target-job-title');
//     if (modalTargetJobTitleField) {
//         modalTargetJobTitleField.value = targetJobTitleGlobalInput ? targetJobTitleGlobalInput.value : "";
//     }
//
//     const skillsDataInput = document.getElementById('skills-data-json'); // From experience.html
//     const modalSkillsField = modal.querySelector('#ai-experience-skills');
//     if (modalSkillsField) {
//         if (skillsDataInput && skillsDataInput.value) {
//             try {
//                 const skillsArray = JSON.parse(skillsDataInput.value);
//                 modalSkillsField.value = skillsArray.join(', ');
//             } catch (e) {
//                 console.warn("Could not parse skills-data-json from #skills-data-json input.", e);
//                 modalSkillsField.value = '';
//             }
//         } else {
//             let allSkills = [];
//             // Fallback: try to find skill inputs from a Django formset named 'skills_set'
//             document.querySelectorAll('input[name^="skills_set-"][name$="-name"]').forEach(input => {
//                 if (input.value.trim()) allSkills.push(input.value.trim());
//             });
//             modalSkillsField.value = allSkills.join(', ');
//         }
//     }
//
//     const responsibilitiesTextarea = parentExperienceForm.querySelector(`textarea[name="experience_set-${experienceIndex}-description"]`);
//     const modalResponsibilitiesField = modal.querySelector('#ai-experience-responsibilities');
//     if (responsibilitiesTextarea && modalResponsibilitiesField) {
//          modalResponsibilitiesField.value = responsibilitiesTextarea.value;
//     } else {
//         if (modalResponsibilitiesField) modalResponsibilitiesField.value = '';
//     }
//
//     modal.classList.remove('hidden');
//     document.body.classList.add('overflow-hidden');
// }
//
// function handleGenerateExperienceBullets() {
//     const modal = document.getElementById('bullet-generation-modal');
//     if (!modal) return;
//
//     const parentExperienceIndex = modal.dataset.parentExperienceIndex;
//     const jobTitle = modal.querySelector('#ai-experience-job-title').value;
//     const targetJobTitle = modal.querySelector('#ai-experience-target-job-title').value;
//     const skills = modal.querySelector('#ai-experience-skills').value;
//     const responsibilities = modal.querySelector('#ai-experience-responsibilities').value;
//     const bulletCount = modal.querySelector('#ai-experience-bullet-count').value;
//     const aiEngine = modal.querySelector('#ai-experience-engine-select').value;
//
//     const loadingSpinnerContainer = modal.querySelector('.loading-spinner-container');
//     const errorMessageDiv = modal.querySelector('.error-message');
//     const generatedBulletsDiv = modal.querySelector('#generatedExperienceBulletsContainer');
//
//     if(errorMessageDiv) {
//         errorMessageDiv.textContent = '';
//         errorMessageDiv.classList.add('hidden');
//     }
//
//     if (!jobTitle.trim()) {
//         if(errorMessageDiv) {
//             errorMessageDiv.textContent = 'Job Title is required to generate bullets.';
//             errorMessageDiv.classList.remove('hidden');
//         }
//         return;
//     }
//
//     if(loadingSpinnerContainer) {
//         loadingSpinnerContainer.classList.remove('hidden');
//         loadingSpinnerContainer.innerHTML = `<div class="flex flex-col items-center justify-center">
//             <div class="border-gray-300 h-8 w-8 animate-spin rounded-full border-4 border-t-blue-600"></div>
//             <p class="text-sm text-gray-600 mt-2">Generating bullets...</p>
//         </div>`;
//     }
//     if(generatedBulletsDiv) generatedBulletsDiv.innerHTML = '';
//
//     const queryParams = new URLSearchParams({
//         job_title: jobTitle,
//         target_job_title: targetJobTitle,
//         skills: skills,
//         responsibilities: responsibilities,
//         bullet_count: bulletCount,
//         ai_engine: aiEngine,
//         parent_index: parentExperienceIndex
//     }).toString();
//
//     fetch(`/job/ai/generate-bullets/?${queryParams}`) // URL from your job_portal_url.py
//         .then(response => {
//             if(loadingSpinnerContainer) loadingSpinnerContainer.classList.add('hidden');
//             if (!response.ok) {
//                 return response.text().then(text => {
//                     const errorText = text || response.statusText;
//                     if(errorMessageDiv) {
//                         errorMessageDiv.textContent = `Error: ${errorText} (Status: ${response.status})`;
//                         errorMessageDiv.classList.remove('hidden');
//                     }
//                     throw new Error(`Server error: ${response.status} - ${errorText}`);
//                 });
//             }
//             return response.text();
//         })
//         .then(html => {
//             if (generatedBulletsDiv) {
//                 if (html.trim() === "") {
//                     generatedBulletsDiv.innerHTML = '<p class="text-sm text-gray-500 p-4 text-center">No bullets generated. Try different inputs or AI engine.</p>';
//                 } else {
//                     generatedBulletsDiv.innerHTML = html;
//                     attachAddGeneratedBulletListeners(generatedBulletsDiv, parentExperienceIndex);
//                 }
//             }
//         })
//         .catch(error => {
//             if(loadingSpinnerContainer) loadingSpinnerContainer.classList.add('hidden');
//             console.error('Error generating experience bullets:', error);
//             if(errorMessageDiv && (!errorMessageDiv.textContent || !errorMessageDiv.textContent.includes('Error:'))) {
//                 errorMessageDiv.textContent = 'An unexpected error occurred. Please check console and try again.';
//             }
//             if(errorMessageDiv) errorMessageDiv.classList.remove('hidden');
//         });
// }
//
// function attachAddGeneratedBulletListeners(container, parentExperienceIndex) {
//     // Assumes HTML from your 'experience_bullet_point_form_row.html' (template for AI bullets) has:
//     // - root div with class="generated-bullet-item"
//     // - data-text="The bullet text" attribute on the root div
//     // - a button with class="add-generated-bullet-button"
//     container.querySelectorAll('.add-generated-bullet-button').forEach(button => {
//         button.addEventListener('click', function() {
//             const bulletItemDiv = this.closest('.generated-bullet-item');
//             if (!bulletItemDiv) return;
//             const bulletText = bulletItemDiv.dataset.text;
//
//             if (bulletText) {
//                 addGeneratedBulletToForm(bulletText, parentExperienceIndex);
//                 this.textContent = 'Added';
//                 this.disabled = true;
//                 // Tailwind classes for "Added" state
//                 this.classList.remove('bg-green-500', 'hover:bg-green-600');
//                 this.classList.add('bg-gray-400', 'text-gray-700', 'cursor-not-allowed', 'opacity-75');
//                 bulletItemDiv.classList.add('opacity-60');
//             }
//         });
//     });
// }
//
// function addGeneratedBulletToForm(bulletText, parentExperienceIndex) {
//     const bulletPointsContainer = document.getElementById(`bullet_points_container_experience_set-${parentExperienceIndex}`);
//     if (!bulletPointsContainer) {
//         console.error(`Bullet points container (bullet_points_container_experience_set-${parentExperienceIndex}) not found.`);
//         return;
//     }
//     const bulletTotalFormsInput = document.getElementById(`id_experience_set-${parentExperienceIndex}-bullet_points-TOTAL_FORMS`);
//     if (!bulletTotalFormsInput) {
//         console.error(`TOTAL_FORMS input for bullets (id_experience_set-${parentExperienceIndex}-bullet_points-TOTAL_FORMS) not found.`);
//         return;
//     }
//     let bulletIndex = parseInt(bulletTotalFormsInput.value);
//
//     const newRow = document.createElement('div');
//     newRow.className = 'bullet-point-row flex items-center gap-x-2 group p-1 rounded-md transition-colors mb-2'; // items-center
//     const textareaId = `id_experience_set-${parentExperienceIndex}-bullet_points-${bulletIndex}-text`;
//     // This HTML includes the "Enhance" button
//     newRow.innerHTML = `
//         <div class="mt-1 text-blue-600 font-bold text-lg">•</div>
//         <div class="flex-1 min-w-0">
//             <input type="hidden" name="experience_set-${parentExperienceIndex}-bullet_points-${bulletIndex}-id" id="id_experience_set-${parentExperienceIndex}-bullet_points-${bulletIndex}-id">
//             <textarea class="block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm min-h-[50px]"
//                 id="${textareaId}"
//                 name="experience_set-${parentExperienceIndex}-bullet_points-${bulletIndex}-text">${bulletText}</textarea>
//             <input type="hidden" name="experience_set-${parentExperienceIndex}-bullet_points-${bulletIndex}-DELETE" id="id_experience_set-${parentExperienceIndex}-bullet_points-${bulletIndex}-DELETE" class="hidden">
//         </div>
//         <div class="flex flex-col space-y-1 items-center ml-2">
//             <button type="button" class="enhance-main-form-bullet-btn p-1 h-7 w-7 flex items-center justify-center border border-indigo-500 text-indigo-500 rounded-full hover:bg-indigo-500 hover:text-white transition-colors opacity-70 group-hover:opacity-100 focus:outline-none focus:ring-2 focus:ring-indigo-500"
//                     title="Enhance with AI"
//                     data-textarea-id="${textareaId}"
//                     data-experience-index="${parentExperienceIndex}">
//                 <i class="fa-solid fa-wand-magic-sparkles text-xs"></i>
//             </button>
//             <button type="button" class="p-1 h-7 w-7 flex items-center justify-center border border-red-500 text-red-500 rounded-full hover:bg-red-500 hover:text-white transition-colors opacity-70 group-hover:opacity-100 focus:outline-none focus:ring-2 focus:ring-red-500"
//                     onclick="removeManualBulletPoint(this, 'experience_set-${parentExperienceIndex}-bullet_points-${bulletIndex}')">
//                 <i class="fa-solid fa-times text-xs"></i>
//             </button>
//         </div>
//     `;
//     bulletPointsContainer.appendChild(newRow);
//     bulletTotalFormsInput.value = bulletIndex + 1;
//     const textarea = newRow.querySelector('textarea');
//     if (textarea) textarea.focus();
// }
//
// function closeAiBulletModal() {
//     const modal = document.getElementById('bullet-generation-modal');
//     if (modal) {
//         modal.classList.add('hidden');
//     }
//     document.body.classList.remove('overflow-hidden');
// }
//
// // ===== Function to handle enhancing a bullet from the main form =====
// function handleEnhanceMainFormBullet(buttonElement) {
//     const textareaId = buttonElement.dataset.textareaId;
//     const experienceIndex = buttonElement.dataset.experienceIndex;
//     const textarea = document.getElementById(textareaId);
//
//     if (!textarea) {
//         console.error("Textarea to enhance not found with ID:", textareaId);
//         alert("Error: Could not find the bullet point text area.");
//         return;
//     }
//     const originalBulletText = textarea.value;
//     if (!originalBulletText.trim()) {
//         alert("Bullet point is empty. Nothing to enhance.");
//         return;
//     }
//
//     const parentExperienceForm = document.querySelector(`.experience-entry[data-index="${experienceIndex}"]`);
//     let jobTitleContext = "";
//     if (parentExperienceForm) {
//         const jobTitleInput = parentExperienceForm.querySelector(`input[name="experience_set-${experienceIndex}-job_title"]`);
//         if (jobTitleInput) {
//             jobTitleContext = jobTitleInput.value;
//         }
//     }
//
//     const aiEngine = 'chatgpt'; // Default or get from a user setting / modal if you add one
//     const jobDescriptionForEnhancement = ""; // Placeholder; populate if available
//
//     const originalButtonContent = buttonElement.innerHTML; // Save current content (icon)
//     // Show loading spinner in button
//     buttonElement.innerHTML = `<svg class="animate-spin h-4 w-4 text-indigo-700" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path></svg>`;
//     buttonElement.disabled = true;
//
//     const queryParams = new URLSearchParams({
//         bullet_text: originalBulletText,
//         enhancement_type: 'general',
//         ai_engine: aiEngine,
//         job_description: jobDescriptionForEnhancement,
//         job_title_context: jobTitleContext,
//         bullet_id_on_form: textareaId // For backend logging or if needed
//     }).toString();
//
//     fetch(`/job/ai/enhance-bullet/?${queryParams}`) // URL from your job_portal_url.py
//         .then(response => {
//             buttonElement.innerHTML = originalButtonContent; // Restore original button icon/text
//             buttonElement.disabled = false;
//             if (!response.ok) {
//                 return response.text().then(text => {
//                     throw new Error(`Server error ${response.status}: ${text || response.statusText}`);
//                 });
//             }
//             return response.text(); // Your Django view returns plain text (the enhanced bullet)
//         })
//         .then(enhancedText => {
//             if (enhancedText.toLowerCase().includes("error") ||
//                 enhancedText.toLowerCase().includes("blocked by gemini") ||
//                 enhancedText.toLowerCase().includes("api key not configured")) {
//                 alert("AI Enhancement Error: " + enhancedText); // Show AI-specific error to user
//             } else if (enhancedText.trim()) {
//                 textarea.value = enhancedText.trim(); // <<< KEY: UPDATE THE TEXTAREA
//                 // Optional: Visual feedback for update
//                 textarea.classList.add('bg-green-50', 'ring-1', 'ring-green-500', 'transition-all', 'duration-300');
//                 setTimeout(() => {
//                     textarea.classList.remove('bg-green-50', 'ring-1', 'ring-green-500');
//                 }, 2000);
//             } else {
//                 alert("AI Enhancement returned empty text. The original bullet point was not changed.");
//             }
//         })
//         .catch(error => {
//             buttonElement.innerHTML = originalButtonContent; // Restore button on fetch error
//             buttonElement.disabled = false;
//             console.error('Error enhancing bullet:', error);
//             alert('Failed to enhance bullet: ' + error.message);
//         });
// }
//
//
// // Consolidated DOMContentLoaded event listeners
// document.addEventListener('DOMContentLoaded', function() {
//     // Preview Modal listeners
//     const previewModal = document.getElementById('preview-modal');
//     if (previewModal) {
//         previewModal.addEventListener('click', function(e) {
//             if (e.target === this) closePreviewModal();
//         });
//         const closePreviewBtn = previewModal.querySelector('.close-preview-modal-btn'); // Ensure this class exists on your preview modal close button
//         if(closePreviewBtn) closePreviewBtn.addEventListener('click', closePreviewModal);
//     }
//
//     document.addEventListener('keydown', function(e) { // Consolidated Escape key handler
//         if (e.key === 'Escape') {
//             const activePreviewModal = document.getElementById('preview-modal');
//             if (activePreviewModal && !activePreviewModal.classList.contains('hidden')) {
//                 closePreviewModal();
//             }
//             const activeAiBulletModal = document.getElementById('bullet-generation-modal');
//             if (activeAiBulletModal && !activeAiBulletModal.classList.contains('hidden')) {
//                 closeAiBulletModal();
//             }
//         }
//     });
//
//     // Character counter listeners
//     document.querySelectorAll('textarea[data-count]').forEach(textarea => {
//         const countDisplay = document.getElementById(textarea.dataset.count);
//         if (countDisplay) {
//             updateCharCount(textarea, countDisplay);
//             textarea.addEventListener('input', () => updateCharCount(textarea, countDisplay));
//         }
//     });
//
//     // Event delegation for dynamically added/static elements
//     // Using a common ancestor for experience forms that exists on page load.
//     // Your experience.html has <div id="experiences_container" ...>
//     const experiencesContainer = document.getElementById('experiences_container');
//     if (experiencesContainer) {
//         experiencesContainer.addEventListener('click', function(event) {
//             // AI Bullet Generation Modal Opener
//             const openModalButton = event.target.closest('.open-experience-ai-modal');
//             if (openModalButton) {
//                 event.preventDefault();
//                 openAiBulletModal({ currentTarget: openModalButton }); // Pass an object that mimics event.currentTarget
//             }
//
//             // Enhance button for bullets in the main form
//             const enhanceMainBulletButton = event.target.closest('.enhance-main-form-bullet-btn');
//             if (enhanceMainBulletButton) {
//                 event.preventDefault();
//                 handleEnhanceMainFormBullet(enhanceMainBulletButton); // Pass the button element itself
//             }
//
//             // Remove Experience Row button (if you have a specific class for it)
//             const removeExpButton = event.target.closest('.remove-experience-row-btn'); // Example class
//             if (removeExpButton) {
//                removeFormRow(removeExpButton); // Pass the button itself
//             }
//         });
//     } else {
//         console.warn("Element with ID 'experiences_container' not found for event delegation.");
//         // Fallback to document.body if specific container not found, less efficient.
//         document.body.addEventListener('click', function(event) {
//             const openModalButton = event.target.closest('.open-experience-ai-modal');
//             if (openModalButton && openModalButton.closest('#experiences_container')) {
//                 event.preventDefault();
//                 openAiBulletModal({ currentTarget: openModalButton });
//             }
//             const enhanceMainBulletButton = event.target.closest('.enhance-main-form-bullet-btn');
//             if (enhanceMainBulletButton && enhanceMainBulletButton.closest('#experiences_container')) {
//                 event.preventDefault();
//                 handleEnhanceMainFormBullet(enhanceMainBulletButton);
//             }
//         });
//     }
//
//
//     // Event listeners for buttons INSIDE the AI Bullet Generation modal (which is static in the base HTML)
//     const aiBulletModal = document.getElementById('bullet-generation-modal');
//     if (aiBulletModal) {
//         const generateBtn = aiBulletModal.querySelector('#generateExperienceBulletsBtn');
//         if (generateBtn) {
//             generateBtn.addEventListener('click', handleGenerateExperienceBullets);
//         }
//
//         // Close buttons in AI modal (using class)
//         aiBulletModal.querySelectorAll('.close-experience-ai-modal').forEach(closeBtn => { // Class from your modal HTML
//             closeBtn.addEventListener('click', closeAiBulletModal);
//         });
//
//         // Backdrop click to close AI modal (ID from your modal HTML)
//         const backdrop = aiBulletModal.querySelector('#bullet-modal-backdrop');
//         if (backdrop) {
//             backdrop.addEventListener('click', (event) => {
//                 if (event.target === backdrop) { // Ensure click is on backdrop itself
//                     closeAiBulletModal();
//                 }
//             });
//         }
//     }
//
//     // Initialize existing manual bullet point remove buttons (if rendered by Django on page load)
//     // This is just to mark them if needed, as onclick is already in HTML.
//     document.querySelectorAll('.bullet-point-row button[onclick^="removeManualBulletPoint"]').forEach(button => {
//         if (!button.classList.contains('js-initialized')) {
//             button.classList.add('js-initialized');
//         }
//     });
// });
//
//
// // // static/js/resume_wizard.js
// //
// // // Resume preview functionality
// // function previewResume() {
// //     const modal = document.getElementById('preview-modal');
// //     if (!modal) {
// //         console.error('Preview modal not found');
// //         return;
// //     }
// //     modal.classList.remove('hidden');
// //     document.body.classList.add('overflow-hidden');
// //
// //     const form = document.getElementById('resume-form');
// //     if (!form) {
// //         console.error('Resume form (#resume-form) not found.');
// //         if (modal) modal.classList.add('hidden');
// //         document.body.classList.remove('overflow-hidden');
// //         return;
// //     }
// //     const formData = new FormData(form);
// //     const modalContent = document.getElementById('preview-modal-content');
// //
// //     modalContent.innerHTML = `<div class="flex justify-center items-center p-8">
// //         <div class="border-gray-300 h-12 w-12 animate-spin rounded-full border-4 border-t-blue-600"></div>
// //     </div>`;
// //
// //     const csrfTokenElement = document.querySelector('[name=csrfmiddlewaretoken]');
// //     if (!csrfTokenElement) {
// //         console.error('CSRF token not found');
// //         modalContent.innerHTML = '<div class="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded relative" role="alert"><strong class="font-bold">Error:</strong><span class="block sm:inline"> CSRF token missing.</span></div>';
// //         return;
// //     }
// //     const csrfToken = csrfTokenElement.value;
// //
// //     fetch('/job/preview-current-resume/', { // Ensure this URL is correct as per your job_portal_url.py
// //         method: 'POST',
// //         body: formData,
// //         headers: {
// //             'X-CSRFToken': csrfToken,
// //             'X-Requested-With': 'XMLHttpRequest'
// //         }
// //     })
// //     .then(response => {
// //         if (!response.ok) {
// //             throw new Error(`Network response was not ok: ${response.statusText}`);
// //         }
// //         return response.text();
// //     })
// //     .then(html => {
// //         if (modalContent) {
// //             modalContent.innerHTML = html;
// //         }
// //     })
// //     .catch(error => {
// //         console.error('Error fetching preview:', error);
// //         if (modalContent) {
// //             modalContent.innerHTML = `<div class="bg-red-100 border-l-4 border-red-500 text-red-700 p-4" role="alert"><p class="font-bold">Error Loading Preview</p><p>${error.message}. Please try again.</p></div>`;
// //         }
// //     });
// // }
// //
// // function closePreviewModal() {
// //     const modal = document.getElementById('preview-modal');
// //     if (modal) {
// //         modal.classList.add('hidden');
// //     }
// //     document.body.classList.remove('overflow-hidden');
// // }
// //
// // function toggleMoreProfiles() {
// //     const moreProfiles = document.getElementById('more-profiles');
// //     const button = document.getElementById('add-more-profiles');
// //     if (!moreProfiles || !button) return;
// //
// //     if (moreProfiles.classList.contains('hidden')) {
// //         moreProfiles.classList.remove('hidden');
// //         moreProfiles.classList.add('animate-fade-in'); // Ensure this animation is defined
// //         button.innerHTML = '<i class="fa-solid fa-minus mr-2"></i> Show fewer profiles';
// //     } else {
// //         moreProfiles.classList.add('hidden');
// //         button.innerHTML = '<i class="fa-solid fa-plus mr-2"></i> Add more profiles';
// //     }
// // }
// //
// // // Add form row (e.g., for experiences)
// // // Assumes your backend '/job/htmx/add-form-row/' returns Tailwind-styled HTML for the new form row
// // function addFormRow(type, containerId, countFieldId) { // countFieldId is the ID of the TOTAL_FORMS input
// //     const totalFormsInput = document.getElementById(countFieldId);
// //     if (!totalFormsInput) {
// //         console.error(`Total forms input field '${countFieldId}' not found.`);
// //         return;
// //     }
// //     let currentIndex = parseInt(totalFormsInput.value);
// //
// //     const container = document.getElementById(containerId);
// //     if (!container) {
// //         console.error(`Container '${containerId}' not found.`);
// //         return;
// //     }
// //
// //     const loadingRow = document.createElement('div');
// //     loadingRow.className = 'flex justify-center p-4 form-row-loading';
// //     loadingRow.innerHTML = '<div class="border-gray-300 h-8 w-8 animate-spin rounded-full border-4 border-t-blue-600"></div>';
// //     container.appendChild(loadingRow);
// //
// //     fetch(`/job/htmx/add-form-row/?form_type=${type}&index=${currentIndex}`, {
// //         headers: { 'X-Requested-With': 'XMLHttpRequest' }
// //     })
// //     .then(response => {
// //         loadingRow.remove();
// //         if (!response.ok) {
// //             throw new Error(`Network response was not ok for addFormRow: ${response.statusText}`);
// //         }
// //         return response.text();
// //     })
// //     .then(html => {
// //         const emptyStateMsg = container.querySelector('.empty-state-message'); // Assuming empty state has this class
// //         if (emptyStateMsg) emptyStateMsg.remove();
// //
// //         container.insertAdjacentHTML('beforeend', html);
// //         totalFormsInput.value = currentIndex + 1;
// //
// //         const newRow = container.lastElementChild;
// //         if (newRow && typeof newRow.scrollIntoView === 'function') {
// //             newRow.scrollIntoView({ behavior: 'smooth', block: 'center' });
// //             newRow.classList.add('ring-2', 'ring-blue-500', 'ring-offset-2', 'transition-all', 'duration-300');
// //             setTimeout(() => newRow.classList.remove('ring-2', 'ring-blue-500', 'ring-offset-2'), 1500);
// //
// //             // If the newly added row is an experience form, attach event listener for its AI button
// //             // The HTML returned from server for the new row must include data-index attribute
// //             // and the .open-experience-ai-modal button.
// //             if (type === 'experience' && newRow.classList.contains('experience-entry')) {
// //                 const aiButton = newRow.querySelector('.open-experience-ai-modal');
// //                 if (aiButton) {
// //                     // Pass an object that mimics event, with currentTarget being the button
// //                     aiButton.addEventListener('click', (event) => openAiBulletModal({ currentTarget: event.currentTarget }));
// //                 }
// //                 // Also initialize manual "Add Bullet Point" button for this new experience form
// //                 // This assumes your server-rendered HTML for new experience row includes the necessary
// //                 // onclick="addBulletPoint('{{new_form.index}}')" or similar.
// //                 // If not, you'd need to find and attach JS listener here.
// //             }
// //         }
// //     })
// //     .catch(error => {
// //         console.error('Error adding form row:', error);
// //         if (loadingRow.parentElement) loadingRow.remove();
// //         const errorMsg = document.createElement('div');
// //         errorMsg.className = 'bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded relative my-3';
// //         errorMsg.textContent = `Error adding new entry: ${error.message}. Please try again.`;
// //         container.appendChild(errorMsg);
// //         setTimeout(() => errorMsg.remove(), 3000);
// //     });
// // }
// //
// // // Remove form row (e.g., an experience entry)
// // function removeFormRow(button) {
// //     const row = button.closest('.experience-entry'); // Using .experience-entry from your experience.html
// //     if (!row) {
// //         console.error("Could not find '.experience-entry' to remove.");
// //         return;
// //     }
// //     const deleteCheckbox = row.querySelector('input[type="checkbox"][name$="-DELETE"]');
// //     if (deleteCheckbox) {
// //         deleteCheckbox.checked = true;
// //         row.classList.add('hidden'); // Hide if it's an existing form to be deleted by Django
// //     } else {
// //         // For new forms not yet saved, animate and remove
// //         row.style.transition = 'all 0.3s ease';
// //         row.style.opacity = '0';
// //         row.style.maxHeight = '0px';
// //         row.style.paddingTop = '0px';
// //         row.style.paddingBottom = '0px';
// //         row.style.marginTop = '0px';
// //         row.style.marginBottom = '0px';
// //         row.style.overflow = 'hidden';
// //         setTimeout(() => {
// //             row.remove();
// //             // Optionally, update TOTAL_FORMS if needed, though Django handles non-contiguous forms.
// //         }, 300);
// //     }
// // }
// //
// // // Add bullet point manually to an experience
// // // Called by inline onclick="addBulletPoint('{{ forloop.counter0 }}')" in experience.html
// // function addBulletPoint(parentExperienceIndex) {
// //     const container = document.getElementById(`bullet_points_container_experience_set-${parentExperienceIndex}`);
// //     if (!container) {
// //         console.error(`Bullet container (bullet_points_container_experience_set-${parentExperienceIndex}) not found.`);
// //         return;
// //     }
// //     const bulletTotalFormsInput = document.getElementById(`id_experience_set-${parentExperienceIndex}-bullet_points-TOTAL_FORMS`);
// //     if (!bulletTotalFormsInput) {
// //         console.error(`TOTAL_FORMS input for bullets (id_experience_set-${parentExperienceIndex}-bullet_points-TOTAL_FORMS) not found.`);
// //         return;
// //     }
// //     let bulletIndex = parseInt(bulletTotalFormsInput.value);
// //
// //     const newRow = document.createElement('div');
// //     newRow.className = 'bullet-point-row flex items-start gap-x-2 group p-1 rounded-md transition-colors mb-2';
// //     newRow.innerHTML = `
// //         <div class="mt-1 text-blue-600 font-bold text-lg">•</div>
// //         <div class="flex-1 min-w-0">
// //             <input type="hidden" name="experience_set-${parentExperienceIndex}-bullet_points-${bulletIndex}-id" id="id_experience_set-${parentExperienceIndex}-bullet_points-${bulletIndex}-id">
// //             <textarea class="block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm min-h-[50px]"
// //                 id="id_experience_set-${parentExperienceIndex}-bullet_points-${bulletIndex}-text"
// //                 name="experience_set-${parentExperienceIndex}-bullet_points-${bulletIndex}-text"
// //                 placeholder="Describe your achievement..."></textarea>
// //             <input type="hidden" name="experience_set-${parentExperienceIndex}-bullet_points-${bulletIndex}-DELETE" id="id_experience_set-${parentExperienceIndex}-bullet_points-${bulletIndex}-DELETE" class="hidden">
// //         </div>
// //         <button type="button" class="mt-1 p-1 h-7 w-7 flex items-center justify-center border border-red-500 text-red-500 rounded-full hover:bg-red-500 hover:text-white transition-colors opacity-70 group-hover:opacity-100 focus:outline-none focus:ring-2 focus:ring-red-500"
// //                 onclick="removeManualBulletPoint(this, 'experience_set-${parentExperienceIndex}-bullet_points-${bulletIndex}')">
// //             <i class="fa-solid fa-times text-xs"></i>
// //         </button>
// //     `;
// //     container.appendChild(newRow);
// //     bulletTotalFormsInput.value = bulletIndex + 1;
// //     const textarea = newRow.querySelector('textarea');
// //     if (textarea) textarea.focus();
// // }
// //
// // // Remove bullet point (manually added)
// // function removeManualBulletPoint(button, bulletFormPrefix) {
// //     const row = button.closest('.bullet-point-row');
// //     if (!row) return;
// //     const idInput = row.querySelector(`input[name="${bulletFormPrefix}-id"]`);
// //     const deleteCheckbox = row.querySelector(`input[name="${bulletFormPrefix}-DELETE"]`);
// //     if (idInput && idInput.value && deleteCheckbox) {
// //         deleteCheckbox.checked = true;
// //         row.classList.add('hidden');
// //     } else {
// //         row.remove();
// //     }
// // }
// //
// // function updateCharCount(textarea, countDisplay) {
// //     if (!textarea || !countDisplay) return;
// //     const count = textarea.value.length;
// //     const minCount = parseInt(textarea.dataset.minCount || "0");
// //     countDisplay.textContent = count;
// //     if (minCount > 0) {
// //         countDisplay.classList.toggle('text-red-600', count < minCount);
// //         countDisplay.classList.toggle('text-green-600', count >= minCount);
// //     }
// // }
// //
// // // ===== AI BULLET GENERATION FUNCTIONS (Tailwind Styled & No Employer) =====
// //
// // function openAiBulletModal(event) {
// //     const button = event.currentTarget; // The "Generate with AI" button
// //     const parentExperienceForm = button.closest('.experience-entry'); // Class from your experience.html
// //     if (!parentExperienceForm) {
// //         console.error("Could not find parent experience form (.experience-entry) for AI modal.");
// //         return;
// //     }
// //     const experienceIndex = parentExperienceForm.dataset.index; // data-index from .experience-entry
// //     if (experienceIndex === undefined) {
// //         console.error("Could not determine experience index (data-index attribute missing on .experience-entry).");
// //         return;
// //     }
// //
// //     const modal = document.getElementById('bullet-generation-modal'); // Correct modal ID
// //     if (!modal) {
// //         console.error("AI Bullet Generation Modal (#bullet-generation-modal) not found.");
// //         return;
// //     }
// //     modal.dataset.parentExperienceIndex = experienceIndex; // Store for later use
// //
// //     const errorMessageDiv = modal.querySelector('.error-message');
// //     const loadingSpinnerContainer = modal.querySelector('.loading-spinner-container');
// //     const generatedBulletsDiv = modal.querySelector('#generatedExperienceBulletsContainer');
// //
// //     if (errorMessageDiv) {
// //         errorMessageDiv.textContent = '';
// //         errorMessageDiv.classList.add('hidden');
// //     }
// //     if (loadingSpinnerContainer) loadingSpinnerContainer.classList.add('hidden');
// //     if (generatedBulletsDiv) generatedBulletsDiv.innerHTML = '';
// //
// //     // Populate modal fields
// //     const jobTitleInput = parentExperienceForm.querySelector(`input[name="experience_set-${experienceIndex}-job_title"]`);
// //     const modalJobTitleField = modal.querySelector('#ai-experience-job-title');
// //     if (jobTitleInput && modalJobTitleField) {
// //         modalJobTitleField.value = jobTitleInput.value;
// //     } else {
// //         console.warn(`Job title input not found for experience ${experienceIndex}`);
// //         if (modalJobTitleField) modalJobTitleField.value = ''; // Clear if not found
// //     }
// //
// //     // REMOVED: No employer/company fetching for the modal's internal state
// //     // modal.dataset.currentCompany = ""; // No longer needed
// //
// //     const targetJobTitleGlobalInput = document.getElementById('target-job-title-for-ai'); // Global hidden input on page
// //     const modalTargetJobTitleField = modal.querySelector('#ai-experience-target-job-title');
// //     if (modalTargetJobTitleField) {
// //         modalTargetJobTitleField.value = targetJobTitleGlobalInput ? targetJobTitleGlobalInput.value : "";
// //     }
// //
// //     const skillsDataInput = document.getElementById('skills-data-json'); // From experience.html
// //     const modalSkillsField = modal.querySelector('#ai-experience-skills');
// //     if (modalSkillsField) {
// //         if (skillsDataInput && skillsDataInput.value) {
// //             try {
// //                 const skillsArray = JSON.parse(skillsDataInput.value);
// //                 modalSkillsField.value = skillsArray.join(', ');
// //             } catch (e) {
// //                 console.warn("Could not parse skills-data-json from #skills-data-json input.", e);
// //                 modalSkillsField.value = ''; // Default to empty if parsing fails
// //             }
// //         } else {
// //              // Fallback if skills-data-json is not present or empty: try to find skill inputs from a formset
// //             let allSkills = [];
// //             // Adjust selector if your skills are not in a formset named 'skills_set'
// //             document.querySelectorAll('input[name^="skills_set-"][name$="-name"]').forEach(input => {
// //                 if (input.value.trim()) allSkills.push(input.value.trim());
// //             });
// //             modalSkillsField.value = allSkills.join(', ');
// //         }
// //     }
// //
// //     const responsibilitiesTextarea = parentExperienceForm.querySelector(`textarea[name="experience_set-${experienceIndex}-description"]`);
// //     const modalResponsibilitiesField = modal.querySelector('#ai-experience-responsibilities');
// //     if (responsibilitiesTextarea && modalResponsibilitiesField) {
// //          modalResponsibilitiesField.value = responsibilitiesTextarea.value;
// //     } else {
// //         if (modalResponsibilitiesField) modalResponsibilitiesField.value = ''; // Clear if not found
// //     }
// //
// //
// //     modal.classList.remove('hidden');
// //     document.body.classList.add('overflow-hidden');
// // }
// //
// // function handleGenerateExperienceBullets() {
// //     const modal = document.getElementById('bullet-generation-modal');
// //     if (!modal) return;
// //
// //     const parentExperienceIndex = modal.dataset.parentExperienceIndex;
// //     // REMOVED: employer is no longer part of the data sent to backend
// //     // const employer = modal.dataset.currentCompany || "";
// //
// //     const jobTitle = modal.querySelector('#ai-experience-job-title').value;
// //     const targetJobTitle = modal.querySelector('#ai-experience-target-job-title').value;
// //     const skills = modal.querySelector('#ai-experience-skills').value;
// //     const responsibilities = modal.querySelector('#ai-experience-responsibilities').value;
// //     const bulletCount = modal.querySelector('#ai-experience-bullet-count').value;
// //     const aiEngine = modal.querySelector('#ai-experience-engine-select').value;
// //
// //     const loadingSpinnerContainer = modal.querySelector('.loading-spinner-container');
// //     const errorMessageDiv = modal.querySelector('.error-message');
// //     const generatedBulletsDiv = modal.querySelector('#generatedExperienceBulletsContainer');
// //
// //     if(errorMessageDiv) {
// //         errorMessageDiv.textContent = '';
// //         errorMessageDiv.classList.add('hidden');
// //     }
// //
// //     // MODIFIED: Client-side validation now only checks for jobTitle
// //     if (!jobTitle.trim()) {
// //         if(errorMessageDiv) {
// //             errorMessageDiv.textContent = 'Job Title is required to generate bullets.';
// //             errorMessageDiv.classList.remove('hidden');
// //         }
// //         return;
// //     }
// //
// //     if(loadingSpinnerContainer) {
// //         loadingSpinnerContainer.classList.remove('hidden');
// //         loadingSpinnerContainer.innerHTML = `<div class="flex flex-col items-center justify-center">
// //             <div class="border-gray-300 h-8 w-8 animate-spin rounded-full border-4 border-t-blue-600"></div>
// //             <p class="text-sm text-gray-600 mt-2">Generating bullets...</p>
// //         </div>`;
// //     }
// //     if(generatedBulletsDiv) generatedBulletsDiv.innerHTML = '';
// //
// //     const queryParams = new URLSearchParams({
// //         job_title: jobTitle,
// //         // employer: employer, // REMOVED employer from parameters
// //         target_job_title: targetJobTitle,
// //         skills: skills,
// //         responsibilities: responsibilities,
// //         bullet_count: bulletCount,
// //         ai_engine: aiEngine,
// //         parent_index: parentExperienceIndex // Still useful for template rendering context if needed
// //     }).toString();
// //
// //     fetch(`/job/ai/generate-bullets/?${queryParams}`) // URL from your job_portal_url.py
// //         .then(response => {
// //             if(loadingSpinnerContainer) loadingSpinnerContainer.classList.add('hidden');
// //             if (!response.ok) { // Check for 4xx/5xx errors
// //                 return response.text().then(text => { // Try to get error text from server
// //                     const errorText = text || response.statusText;
// //                     if(errorMessageDiv) {
// //                         errorMessageDiv.textContent = `Error: ${errorText} (Status: ${response.status})`;
// //                         errorMessageDiv.classList.remove('hidden');
// //                     }
// //                     throw new Error(`Server error: ${response.status} - ${errorText}`);
// //                 });
// //             }
// //             return response.text(); // Expecting HTML response from your Django view
// //         })
// //         .then(html => {
// //             if (generatedBulletsDiv) {
// //                 if (html.trim() === "") {
// //                     generatedBulletsDiv.innerHTML = '<p class="text-sm text-gray-500 p-4 text-center">No bullets generated. Try different inputs or AI engine.</p>';
// //                 } else {
// //                     generatedBulletsDiv.innerHTML = html; // Insert HTML from server
// //                     attachAddGeneratedBulletListeners(generatedBulletsDiv, parentExperienceIndex);
// //                 }
// //             }
// //         })
// //         .catch(error => {
// //             if(loadingSpinnerContainer) loadingSpinnerContainer.classList.add('hidden');
// //             console.error('Error generating experience bullets:', error);
// //             if(errorMessageDiv && (!errorMessageDiv.textContent || !errorMessageDiv.textContent.includes('Error:'))) {
// //                 errorMessageDiv.textContent = 'An unexpected error occurred. Please check console and try again.';
// //             }
// //             if(errorMessageDiv) errorMessageDiv.classList.remove('hidden');
// //         });
// // }
// //
// // function attachAddGeneratedBulletListeners(container, parentExperienceIndex) {
// //     // Assumes HTML from your 'experience_bullet_point_form_row.html' partial has:
// //     // - root div with class="generated-bullet-item"
// //     // - data-text="The bullet text" attribute on the root div
// //     // - a button with class="add-generated-bullet-button"
// //     container.querySelectorAll('.add-generated-bullet-button').forEach(button => {
// //         button.addEventListener('click', function() {
// //             const bulletItemDiv = this.closest('.generated-bullet-item');
// //             if (!bulletItemDiv) return;
// //             const bulletText = bulletItemDiv.dataset.text;
// //
// //             if (bulletText) {
// //                 addGeneratedBulletToForm(bulletText, parentExperienceIndex);
// //                 this.textContent = 'Added';
// //                 this.disabled = true;
// //                 // Tailwind classes for "Added" state
// //                 this.classList.remove('bg-green-500', 'hover:bg-green-600');
// //                 this.classList.add('bg-gray-400', 'text-gray-700', 'cursor-not-allowed', 'opacity-75');
// //                 bulletItemDiv.classList.add('opacity-60');
// //             }
// //         });
// //     });
// // }
// //
// // function addGeneratedBulletToForm(bulletText, parentExperienceIndex) {
// //     const bulletPointsContainer = document.getElementById(`bullet_points_container_experience_set-${parentExperienceIndex}`);
// //     if (!bulletPointsContainer) {
// //         console.error(`Bullet points container (bullet_points_container_experience_set-${parentExperienceIndex}) not found.`);
// //         return;
// //     }
// //     const bulletTotalFormsInput = document.getElementById(`id_experience_set-${parentExperienceIndex}-bullet_points-TOTAL_FORMS`);
// //     if (!bulletTotalFormsInput) {
// //         console.error(`TOTAL_FORMS input for bullets (id_experience_set-${parentExperienceIndex}-bullet_points-TOTAL_FORMS) not found.`);
// //         return;
// //     }
// //     let bulletIndex = parseInt(bulletTotalFormsInput.value);
// //
// //     const newRow = document.createElement('div');
// //     newRow.className = 'bullet-point-row flex items-start gap-x-2 group p-1 rounded-md transition-colors mb-2';
// //     // Structure matches manual addBulletPoint, ensuring compatibility with Django formsets
// //     newRow.innerHTML = `
// //         <div class="mt-1 text-blue-600 font-bold text-lg">•</div>
// //         <div class="flex-1 min-w-0">
// //             <input type="hidden" name="experience_set-${parentExperienceIndex}-bullet_points-${bulletIndex}-id" id="id_experience_set-${parentExperienceIndex}-bullet_points-${bulletIndex}-id">
// //             <textarea class="block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm min-h-[50px]"
// //                 id="id_experience_set-${parentExperienceIndex}-bullet_points-${bulletIndex}-text"
// //                 name="experience_set-${parentExperienceIndex}-bullet_points-${bulletIndex}-text">${bulletText}</textarea>
// //             <input type="hidden" name="experience_set-${parentExperienceIndex}-bullet_points-${bulletIndex}-DELETE" id="id_experience_set-${parentExperienceIndex}-bullet_points-${bulletIndex}-DELETE" class="hidden">
// //         </div>
// //         <button type="button" class="mt-1 p-1 h-7 w-7 flex items-center justify-center border border-red-500 text-red-500 rounded-full hover:bg-red-500 hover:text-white transition-colors opacity-70 group-hover:opacity-100 focus:outline-none focus:ring-2 focus:ring-red-500"
// //                 onclick="removeManualBulletPoint(this, 'experience_set-${parentExperienceIndex}-bullet_points-${bulletIndex}')">
// //             <i class="fa-solid fa-times text-xs"></i>
// //         </button>
// //     `;
// //     bulletPointsContainer.appendChild(newRow); // Appends to the main list of bullets for that experience
// //     bulletTotalFormsInput.value = bulletIndex + 1;
// //     const textarea = newRow.querySelector('textarea');
// //     if (textarea) textarea.focus();
// // }
// //
// // function closeAiBulletModal() {
// //     const modal = document.getElementById('bullet-generation-modal'); // Use correct modal ID
// //     if (modal) {
// //         modal.classList.add('hidden');
// //     }
// //     document.body.classList.remove('overflow-hidden');
// // }
// //
// // // Consolidated DOMContentLoaded event listeners
// // document.addEventListener('DOMContentLoaded', function() {
// //     // Preview Modal listeners
// //     const previewModal = document.getElementById('preview-modal');
// //     if (previewModal) {
// //         previewModal.addEventListener('click', function(e) {
// //             if (e.target === this) closePreviewModal();
// //         });
// //         const closePreviewBtn = previewModal.querySelector('.close-preview-modal-btn'); // Add this class to your close button in preview modal
// //         if(closePreviewBtn) closePreviewBtn.addEventListener('click', closePreviewModal);
// //     }
// //
// //     document.addEventListener('keydown', function(e) { // Consolidated Escape key handler
// //         if (e.key === 'Escape') {
// //             const activePreviewModal = document.getElementById('preview-modal');
// //             if (activePreviewModal && !activePreviewModal.classList.contains('hidden')) {
// //                 closePreviewModal();
// //             }
// //             const activeAiBulletModal = document.getElementById('bullet-generation-modal');
// //             if (activeAiBulletModal && !activeAiBulletModal.classList.contains('hidden')) {
// //                 closeAiBulletModal();
// //             }
// //         }
// //     });
// //
// //     // Character counter listeners
// //     document.querySelectorAll('textarea[data-count]').forEach(textarea => {
// //         const countDisplay = document.getElementById(textarea.dataset.count);
// //         if (countDisplay) {
// //             updateCharCount(textarea, countDisplay);
// //             textarea.addEventListener('input', () => updateCharCount(textarea, countDisplay));
// //         }
// //     });
// //
// //     // Event delegation for AI Modal Opener and other dynamic elements if needed.
// //     // Using a common ancestor for experience forms that exists on page load.
// //     const experiencesContainer = document.getElementById('experiences_container'); // From your experience.html
// //     if (experiencesContainer) {
// //         experiencesContainer.addEventListener('click', function(event) {
// //             const openModalButton = event.target.closest('.open-experience-ai-modal');
// //             if (openModalButton) {
// //                 event.preventDefault();
// //                 openAiBulletModal({ currentTarget: openModalButton });
// //             }
// //             // Add other delegated events here if needed, e.g., for removeFormRow for experiences
// //             const removeExpButton = event.target.closest('.remove-experience-row-btn'); // Ensure your remove exp button has this class
// //             if (removeExpButton) {
// //                 removeFormRow(removeExpButton); // Pass the button itself
// //             }
// //         });
// //     } else {
// //         // Fallback if 'experiences_container' is not found - less efficient but works
// //         document.body.addEventListener('click', function(event) {
// //             const openModalButton = event.target.closest('.open-experience-ai-modal');
// //             if (openModalButton && openModalButton.closest('#experiences_container')) { // Ensure it's within the intended area
// //                 event.preventDefault();
// //                 openAiBulletModal({ currentTarget: openModalButton });
// //             }
// //         });
// //     }
// //
// //
// //     // Event listeners for buttons INSIDE the AI modal (which is static in the base HTML)
// //     const aiBulletModal = document.getElementById('bullet-generation-modal');
// //     if (aiBulletModal) {
// //         const generateBtn = aiBulletModal.querySelector('#generateExperienceBulletsBtn');
// //         if (generateBtn) {
// //             generateBtn.addEventListener('click', handleGenerateExperienceBullets);
// //         }
// //
// //         // Close buttons in AI modal
// //         aiBulletModal.querySelectorAll('.close-experience-ai-modal').forEach(closeBtn => {
// //             closeBtn.addEventListener('click', closeAiBulletModal);
// //         });
// //
// //         // Backdrop click to close AI modal
// //         const backdrop = aiBulletModal.querySelector('#bullet-modal-backdrop'); // ID from your modal HTML
// //         if (backdrop) {
// //             backdrop.addEventListener('click', (event) => {
// //                 // Ensure click is on backdrop itself, not on modal content bubbling up
// //                 if (event.target === backdrop) {
// //                     closeAiBulletModal();
// //                 }
// //             });
// //         }
// //     }
// //
// //     // Initialize existing manual bullet point remove buttons (if rendered by Django on page load)
// //     document.querySelectorAll('.bullet-point-row button[onclick^="removeManualBulletPoint"]').forEach(button => {
// //         if (!button.classList.contains('js-initialized')) {
// //             // The onclick is already in HTML. This is just to mark it if needed for other logic.
// //             button.classList.add('js-initialized');
// //         }
// //     });
// // });
// //
// //
// //
// // // // static/js/resume_wizard.js
// // //
// // // // Resume preview functionality
// // // function previewResume() {
// // //     // Show the modal
// // //     const modal = document.getElementById('preview-modal');
// // //     if (!modal) {
// // //         console.error('Preview modal not found');
// // //         return;
// // //     }
// // //
// // //     modal.classList.remove('hidden');
// // //     document.body.classList.add('overflow-hidden'); // Prevent scrolling
// // //
// // //     // Get the current form data
// // //     const form = document.getElementById('resume-form');
// // //     const formData = new FormData(form);
// // //     const modalContent = document.getElementById('preview-modal-content');
// // //
// // //     modalContent.innerHTML = '<div class="flex justify-center p-8"><span class="loading loading-spinner loading-lg"></span></div>';
// // //
// // //     // Get CSRF token
// // //     const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
// // //
// // //     // Make an AJAX request to the preview URL
// // //     fetch('/resume/preview-current/', {
// // //         method: 'POST',
// // //         body: formData,
// // //         headers: {
// // //             'X-CSRFToken': csrfToken,
// // //             'X-Requested-With': 'XMLHttpRequest'
// // //         }
// // //     })
// // //     .then(response => {
// // //         if (!response.ok) {
// // //             throw new Error('Network response was not ok');
// // //         }
// // //         return response.text();
// // //     })
// // //     .then(html => {
// // //         if (modalContent) {
// // //             modalContent.innerHTML = html;
// // //         }
// // //     })
// // //     .catch(error => {
// // //         console.error('Error fetching preview:', error);
// // //         if (modalContent) {
// // //             modalContent.innerHTML = '<div class="alert alert-error p-4">Error loading preview. Please try again.</div>';
// // //         }
// // //     });
// // // }
// // //
// // // // Close preview modal
// // // function closePreviewModal() {
// // //     const modal = document.getElementById('preview-modal');
// // //     if (modal) {
// // //         modal.classList.add('hidden');
// // //     }
// // //     document.body.classList.remove('overflow-hidden');
// // // }
// // //
// // // // Function to toggle more profiles section
// // // function toggleMoreProfiles() {
// // //     const moreProfiles = document.getElementById('more-profiles');
// // //     const button = document.getElementById('add-more-profiles');
// // //
// // //     if (!moreProfiles || !button) return;
// // //
// // //     if (moreProfiles.classList.contains('hidden')) {
// // //         // Show more profiles
// // //         moreProfiles.classList.remove('hidden');
// // //         moreProfiles.classList.add('animate-fade-in');
// // //         button.innerHTML = '<i class="fa-solid fa-minus mr-2"></i> Show fewer profiles';
// // //     } else {
// // //         // Hide more profiles
// // //         moreProfiles.classList.add('hidden');
// // //         button.innerHTML = '<i class="fa-solid fa-plus mr-2"></i> Add more profiles';
// // //     }
// // // }
// // //
// // // // Add form row (for multiple entries like skills, experiences, etc.)
// // // function addFormRow(type, containerId, countFieldId) {
// // //     // Get current count
// // //     const countField = document.getElementById(countFieldId);
// // //     if (!countField) return;
// // //
// // //     const currentIndex = parseInt(countField.value);
// // //
// // //     // Increment the count
// // //     countField.value = currentIndex + 1;
// // //
// // //     const container = document.getElementById(containerId);
// // //     if (!container) return;
// // //
// // //     // Show loading state
// // //     const loadingRow = document.createElement('div');
// // //     loadingRow.className = 'flex justify-center p-4';
// // //     loadingRow.innerHTML = '<span class="loading loading-spinner loading-md"></span>';
// // //     container.appendChild(loadingRow);
// // //
// // //     // Use AJAX to fetch the new row template
// // //     fetch(`/resume/add-form-row/?form_type=${type}&index=${currentIndex}`, {
// // //         headers: {
// // //             'X-Requested-With': 'XMLHttpRequest'
// // //         }
// // //     })
// // //     .then(response => {
// // //         if (!response.ok) {
// // //             throw new Error('Network response was not ok');
// // //         }
// // //         return response.text();
// // //     })
// // //     .then(html => {
// // //         // Remove loading state
// // //         if (loadingRow && loadingRow.parentNode) {
// // //             loadingRow.remove();
// // //         }
// // //
// // //         // If this is the first item, clear any empty state
// // //         if (currentIndex === 0 && container.querySelector('.text-center')) {
// // //             container.innerHTML = '';
// // //         }
// // //
// // //         // Insert the new row
// // //         container.insertAdjacentHTML('beforeend', html);
// // //
// // //         // Scroll to the new row
// // //         const newRow = container.lastElementChild;
// // //         if (newRow) {
// // //             newRow.scrollIntoView({ behavior: 'smooth', block: 'center' });
// // //
// // //             // Add highlight effect
// // //             newRow.classList.add('ring-2', 'ring-primary', 'ring-offset-2');
// // //             setTimeout(() => {
// // //                 newRow.classList.remove('ring-2', 'ring-primary', 'ring-offset-2');
// // //             }, 1500);
// // //         }
// // //     })
// // //     .catch(error => {
// // //         console.error('Error adding form row:', error);
// // //
// // //         // Remove loading state
// // //         if (loadingRow && loadingRow.parentNode) {
// // //             loadingRow.remove();
// // //         }
// // //
// // //         // Show error message
// // //         const errorMsg = document.createElement('div');
// // //         errorMsg.className = 'alert alert-error my-3';
// // //         errorMsg.textContent = 'Error adding new entry. Please try again.';
// // //         container.appendChild(errorMsg);
// // //
// // //         // Remove error after 3 seconds
// // //         setTimeout(() => {
// // //             if (errorMsg && errorMsg.parentNode) {
// // //                 errorMsg.remove();
// // //             }
// // //         }, 3000);
// // //     });
// // // }
// // //
// // // // Remove form row
// // // function removeFormRow(button, containerId, countFieldId) {
// // //     const container = document.getElementById(containerId);
// // //     if (!container) return;
// // //
// // //     const row = button.closest('.form-row');
// // //     if (!row) return;
// // //
// // //     // Animation for removal
// // //     row.style.transition = 'all 0.3s ease';
// // //     row.style.opacity = '0';
// // //     row.style.maxHeight = '0';
// // //     row.style.overflow = 'hidden';
// // //
// // //     setTimeout(() => {
// // //         if (row.parentNode) {
// // //             row.remove();
// // //         }
// // //
// // //         // Update the counter
// // //         const countField = document.getElementById(countFieldId);
// // //         if (countField) {
// // //             countField.value = parseInt(countField.value) - 1;
// // //         }
// // //
// // //         // Show empty state if no rows left
// // //         if (container.children.length === 0) {
// // //             // Fetch the empty state template or use a default
// // //             const emptyState = `
// // //                 <div class="bg-base-100 border border-gray-100 dark:border-gray-700 rounded-xl shadow p-8 text-center">
// // //                     <div class="w-16 h-16 rounded-full bg-primary/10 flex items-center justify-center mx-auto mb-4">
// // //                         <i class="fa-solid fa-plus text-primary text-2xl"></i>
// // //                     </div>
// // //                     <h3 class="text-lg font-medium mb-2">No Items Added Yet</h3>
// // //                     <p class="text-gray-500 max-w-md mx-auto mb-6">
// // //                         Add items to continue building your resume.
// // //                     </p>
// // //                     <button type="button" class="btn btn-primary"
// // //                             onclick="addFormRow('${containerId.replace('_container', '')}', '${containerId}', '${countFieldId}')">
// // //                         <i class="fa-solid fa-plus mr-2"></i> Add Your First Item
// // //                     </button>
// // //                 </div>
// // //             `;
// // //             container.innerHTML = emptyState;
// // //         }
// // //     }, 300);
// // // }
// // //
// // // // Add bullet point
// // // function addBulletPoint(parentIndex) {
// // //     const container = document.getElementById(`bullet_points_container_${parentIndex}`);
// // //     if (!container) return;
// // //
// // //     const bulletCount = container.querySelectorAll('.bullet-point-row').length;
// // //
// // //     // Update hidden field
// // //     const countField = document.getElementById(`bullet_count_${parentIndex}`);
// // //     if (countField) {
// // //         countField.value = bulletCount + 1;
// // //     }
// // //
// // //     // Create new bullet point row
// // //     const newRow = document.createElement('div');
// // //     newRow.className = 'bullet-point-row flex items-start gap-3 group p-2 rounded-md transition-colors';
// // //
// // //     newRow.innerHTML = `
// // //         <div class="mt-3 text-primary">•</div>
// // //         <div class="form-control flex-1">
// // //             <textarea class="textarea textarea-bordered w-full min-h-24"
// // //                 id="bullet_${parentIndex}_${bulletCount}"
// // //                 name="bullet_${parentIndex}_${bulletCount}"
// // //                 placeholder="Describe your achievement with action verbs and measurable results"></textarea>
// // //         </div>
// // //         <button type="button" class="btn btn-circle btn-outline btn-error btn-sm mt-3 opacity-70 hover:opacity-100"
// // //                 onclick="removeBulletPoint(this, '${parentIndex}')">
// // //             <i class="fa-solid fa-times"></i>
// // //         </button>
// // //     `;
// // //
// // //     // Add to container
// // //     container.appendChild(newRow);
// // //
// // //     // Add entrance animation
// // //     newRow.style.opacity = '0';
// // //     newRow.style.transform = 'translateY(10px)';
// // //
// // //     setTimeout(() => {
// // //         newRow.style.transition = 'all 0.3s ease';
// // //         newRow.style.opacity = '1';
// // //         newRow.style.transform = 'translateY(0)';
// // //
// // //         // Focus on new textarea
// // //         const textarea = document.getElementById(`bullet_${parentIndex}_${bulletCount}`);
// // //         if (textarea) {
// // //             textarea.focus();
// // //         }
// // //     }, 10);
// // // }
// // //
// // // // Remove bullet point
// // // function removeBulletPoint(button, parentIndex) {
// // //     const container = document.getElementById(`bullet_points_container_${parentIndex}`);
// // //     if (!container) return;
// // //
// // //     const row = button.closest('.bullet-point-row');
// // //     if (!row) return;
// // //
// // //     // Don't remove if it's the last one
// // //     if (container.querySelectorAll('.bullet-point-row').length <= 1) {
// // //         const textarea = row.querySelector('textarea');
// // //         if (textarea) {
// // //             textarea.value = '';
// // //             textarea.focus();
// // //         }
// // //         return;
// // //     }
// // //
// // //     // Animation
// // //     row.style.transition = 'all 0.2s ease';
// // //     row.style.opacity = '0';
// // //     row.style.transform = 'translateX(10px)';
// // //
// // //     setTimeout(() => {
// // //         if (row.parentNode) {
// // //             row.remove();
// // //         }
// // //
// // //         // Renumber bullets
// // //         container.querySelectorAll('.bullet-point-row').forEach((bullet, idx) => {
// // //             const textarea = bullet.querySelector('textarea');
// // //             if (textarea) {
// // //                 textarea.id = `bullet_${parentIndex}_${idx}`;
// // //                 textarea.name = `bullet_${parentIndex}_${idx}`;
// // //             }
// // //         });
// // //
// // //         // Update count
// // //         const countField = document.getElementById(`bullet_count_${parentIndex}`);
// // //         if (countField) {
// // //             countField.value = container.querySelectorAll('.bullet-point-row').length;
// // //         }
// // //     }, 200);
// // // }
// // //
// // // // Initialize on page load
// // // document.addEventListener('DOMContentLoaded', function() {
// // //     // Set up modal close actions
// // //     const modal = document.getElementById('preview-modal');
// // //     if (modal) {
// // //         // Close modal when clicking outside content
// // //         modal.addEventListener('click', function(e) {
// // //             if (e.target === this) {
// // //                 closePreviewModal();
// // //             }
// // //         });
// // //     }
// // //
// // //     // Close modal with escape key
// // //     document.addEventListener('keydown', function(e) {
// // //         if (e.key === 'Escape' && modal && !modal.classList.contains('hidden')) {
// // //             closePreviewModal();
// // //         }
// // //     });
// // //
// // //     // Initialize character counters
// // //     document.querySelectorAll('textarea[data-count]').forEach(textarea => {
// // //         const countDisplay = document.getElementById(textarea.dataset.count);
// // //         if (countDisplay) {
// // //             updateCharCount(textarea, countDisplay);
// // //             textarea.addEventListener('input', () => updateCharCount(textarea, countDisplay));
// // //         }
// // //     });
// // // });
// // //
// // // // Update character count
// // // function updateCharCount(textarea, countDisplay) {
// // //     if (!textarea || !countDisplay) return;
// // //
// // //     const count = textarea.value.length;
// // //     const minCount = parseInt(textarea.dataset.minCount || 0);
// // //
// // //     countDisplay.textContent = count;
// // //
// // //     if (minCount > 0) {
// // //         if (count < minCount) {
// // //             countDisplay.classList.add('text-error');
// // //             countDisplay.classList.remove('text-success');
// // //         } else {
// // //             countDisplay.classList.add('text-success');
// // //             countDisplay.classList.remove('text-error');
// // //         }
// // //     }
// // // }