// static/js/project_enhancement.js
document.addEventListener('DOMContentLoaded', function () {
    const projectFormsetContainer = document.getElementById('project-formset-container');
    if (!projectFormsetContainer) {
        // console.warn('Project formset container not found.');
        return;
    }

    const projectFormsContainer = document.getElementById('project-forms');
    const addProjectButton = document.getElementById('add-project-form');
    const emptyProjectFormHtml = document.getElementById('empty-project-form')?.innerHTML;
    const totalFormsInput = projectFormsetContainer.querySelector('input[name="projects-TOTAL_FORMS"]');

    // URLs for AI actions - these should be defined in a <script> tag in projects.html
    // or passed via data attributes to the main container.
    let enhanceProjectBulletUrl = ''; // Default value
    let generateProjectBulletsUrl = ''; // Default value

    // Try to get URLs from global scope (if set in <script> tag in projects.html)
    if (typeof window.enhanceProjectBulletUrl !== 'undefined') {
        enhanceProjectBulletUrl = window.enhanceProjectBulletUrl;
    } else {
        console.warn('`enhanceProjectBulletUrl` not defined globally. AI features for single bullet enhancement might not work.');
    }
    if (typeof window.generateProjectBulletsUrl !== 'undefined') {
        generateProjectBulletsUrl = window.generateProjectBulletsUrl;
    } else {
        console.warn('`generateProjectBulletsUrl` not defined globally. AI features for generating all bullets might not work.');
    }


    if (!projectFormsContainer || !addProjectButton || !emptyProjectFormHtml || !totalFormsInput) {
        console.error('Project formset: Missing one or more core elements (forms container, add button, empty form template, or TOTAL_FORMS input).');
        return;
    }

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
    const csrftoken = getCookie('csrftoken');

    function openModal(modalId) {
        window.dispatchEvent(new CustomEvent('open-modal', { detail: modalId }));
    }

    function closeModal(modalId) {
        window.dispatchEvent(new CustomEvent('close-modal', { detail: modalId }));
    }

    addProjectButton.addEventListener('click', function () {
        const newIndex = parseInt(totalFormsInput.value);
        const newFormWrappedHtml = emptyProjectFormHtml
            .replace(/__prefix__/g, newIndex)
            .replace(/project_index_placeholder/g, newIndex); // If you use a specific placeholder

        const tempDiv = document.createElement('div');
        tempDiv.innerHTML = newFormWrappedHtml;
        const newFormElement = tempDiv.firstElementChild;

        if (newFormElement) {
            newFormElement.classList.remove('hidden');
            newFormElement.setAttribute('data-project-form-index', newIndex);
            const counterSpan = newFormElement.querySelector('.project-form-counter');
            if(counterSpan) counterSpan.textContent = newIndex + 1;

            projectFormsContainer.appendChild(newFormElement);
            totalFormsInput.value = newIndex + 1;

            const techSelect = newFormElement.querySelector('select[name$="-technologies"]');
            if (techSelect && window.TomSelect) { // Assuming TomSelect is loaded globally
                // new TomSelect(techSelect, { create: true, persist: false }); // Initialize TomSelect if used
            }

            initializeProjectBulletManagement(newFormElement, newIndex);
            initializeAIButtonsForProject(newFormElement, newIndex);
        } else {
            console.error("Failed to create new project form from template.");
        }
    });

    projectFormsContainer.addEventListener('click', function (e) {
        const removeButton = e.target.closest('.remove-project-form');
        if (removeButton) {
            const formToRemove = removeButton.closest('.project-form');
            const deleteCheckbox = formToRemove.querySelector('input[type="checkbox"][name$="-DELETE"]');
            if (deleteCheckbox) {
                deleteCheckbox.checked = true;
                formToRemove.style.display = 'none';
                // Add visual feedback for deletion
                let feedback = formToRemove.querySelector('.deletion-feedback');
                if (!feedback) {
                    feedback = document.createElement('p');
                    feedback.className = 'deletion-feedback text-xs text-red-700 dark:text-red-300 p-2 text-center font-semibold';
                    formToRemove.appendChild(feedback);
                }
                feedback.textContent = 'This project will be deleted upon saving.';
            } else {
                formToRemove.remove();
            }
        }
    });

    function initializeProjectBulletManagement(projectFormElement, projectIndex) {
        const addBulletButton = projectFormElement.querySelector(`.add-project-bullet-form[data-project-index="${projectIndex}"]`);
        const bulletsContainer = projectFormElement.querySelector(`#project-bullet-forms-${projectIndex}`);
        let emptyBulletFormHtml = projectFormElement.querySelector(`#empty-project-bullet-form-${projectIndex}`)?.innerHTML;
        const bulletTotalFormsInput = projectFormElement.querySelector(`input[name="projects-${projectIndex}-bullets-TOTAL_FORMS"]`);

        if (!addBulletButton || !bulletsContainer || !emptyBulletFormHtml || !bulletTotalFormsInput) {
            // console.warn(`Bullet elements missing for project ${projectIndex}`);
            return;
        }

        emptyBulletFormHtml = emptyBulletFormHtml.replace(new RegExp(`projects-${projectIndex}-bullets-__bullet_prefix__`, 'g'), `projects-${projectIndex}-bullets-__prefix__`);

        addBulletButton.addEventListener('click', function () {
            const bulletNewIndex = parseInt(bulletTotalFormsInput.value);
            let newBulletHtml = emptyBulletFormHtml;

            // Replace Django's __prefix__ for formset fields
            newBulletHtml = newBulletHtml.replace(/__prefix__/g, bulletNewIndex);
            // Replace custom __bullet_prefix__ if used for other attributes or display
            newBulletHtml = newBulletHtml.replace(/__bullet_prefix__/g, bulletNewIndex);


            const tempBulletDiv = document.createElement('div');
            tempBulletDiv.innerHTML = newBulletHtml.trim();
            const newBulletElement = tempBulletDiv.firstElementChild;

            if (newBulletElement) {
                newBulletElement.setAttribute('data-bullet-form-index', bulletNewIndex);
                newBulletElement.setAttribute('data-parent-index', projectIndex);

                // Update IDs and names if they were cloned with __prefix__ (Django's formset default)
                // For the main form fields
                newBulletElement.querySelectorAll('[id*="projects-' + projectIndex + '-bullets-__prefix__"]').forEach(el => {
                    el.id = el.id.replace('__prefix__', bulletNewIndex);
                });
                newBulletElement.querySelectorAll('[name*="projects-' + projectIndex + '-bullets-__prefix__"]').forEach(el => {
                    el.name = el.name.replace('__prefix__', bulletNewIndex);
                });
                // For any custom __bullet_prefix__ based IDs if used
                newBulletElement.querySelectorAll('[id*="__bullet_prefix__"]').forEach(el => {
                     el.id = el.id.replace('__bullet_prefix__', bulletNewIndex);
                });


                bulletsContainer.appendChild(newBulletElement);
                bulletTotalFormsInput.value = bulletNewIndex + 1;
                initializeAIButtonsForProject(newBulletElement, projectIndex, bulletNewIndex);
            } else {
                 console.error("Failed to create new project bullet form from template.");
            }
        });

        bulletsContainer.addEventListener('click', function (e) {
            const removeBulletButton = e.target.closest('.remove-project-bullet-form');
            if (removeBulletButton) {
                const bulletFormToRemove = removeBulletButton.closest('.bullet-point-row'); // Ensure this class matches your bullet row
                const deleteBulletCheckbox = bulletFormToRemove.querySelector('input[type="checkbox"][name$="-DELETE"]');
                if (deleteBulletCheckbox) {
                    deleteBulletCheckbox.checked = true;
                    bulletFormToRemove.style.display = 'none';
                } else {
                    bulletFormToRemove.remove();
                }
            }
        });
    }

    function initializeAIButtonsForProject(scopeElement, projectIndex, bulletIndex = null) {
        scopeElement.querySelectorAll('.ai-enhance-project-bullet-btn').forEach(btn => {
            if (btn.dataset.listenerAttached === 'true') return;
            btn.addEventListener('click', function () {
                const projIdx = this.dataset.projectIndex;
                const bIdx = this.dataset.bulletIndex;
                const bulletTextSelector = this.dataset.bulletTextSelector; // e.g. #id_projects-0-bullets-0-description
                const currentBulletText = document.querySelector(bulletTextSelector)?.value || '';
                const bulletId = this.dataset.bulletId || '';

                const projectName = document.querySelector(this.dataset.projectNameSelector)?.value || '';
                const projectSummary = document.querySelector(this.dataset.projectSummarySelector)?.value || '';

                openAIProjectModal('enhance_single_project_bullet', projIdx, bIdx, bulletId, currentBulletText, projectName, projectSummary);
            });
            btn.dataset.listenerAttached = 'true';
        });

        scopeElement.querySelectorAll('.ai-generate-project-bullets-btn').forEach(btn => {
            if (btn.dataset.listenerAttached === 'true') return;
            btn.addEventListener('click', function() {
                const projIdx = this.dataset.projectIndex;
                const projectName = document.querySelector(this.dataset.projectNameSelector)?.value || '';
                const projectSummary = document.querySelector(this.dataset.projectSummarySelector)?.value || '';
                openAIProjectModal('generate_project_bullets', projIdx, null, null, '', projectName, projectSummary);
            });
            btn.dataset.listenerAttached = 'true';
        });
    }

    function openAIProjectModal(actionType, projectIdx, bulletIdx, bulletId, bulletText, projectName, projectSummary) {
        const modal = document.getElementById('project-enhancement-modal');
        if (!modal) { console.error('Project enhancement modal not found'); return; }

        modal.querySelector('#project_ai_parent_index_modal').value = projectIdx;
        modal.querySelector('#project_ai_project_name_modal').value = projectName;
        modal.querySelector('#project_ai_project_summary_modal').value = projectSummary;
        modal.querySelector('#project_ai_action_type_modal').value = actionType;

        const form = modal.querySelector('#project-ai-form');
        const titleEl = modal.querySelector('#modal-title-project-ai');
        const subtitleEl = modal.querySelector('#project_ai_modal_subtitle');
        const singleBulletFields = modal.querySelector('#project_ai_single_bullet_fields_container');
        const generateBulletsFields = modal.querySelector('#project_ai_generate_bullets_fields_container');
        const enhancementTypeContainer = modal.querySelector('#project_ai_enhancement_type_container');
        const submitBtn = modal.querySelector('#project_ai_submit_btn');
        const indicatorText = modal.querySelector('#project_ai_indicator_text');

        modal.querySelector('#project_ai_result_area').innerHTML = '<p class="text-xs text-slate-400 dark:text-slate-500 italic">Suggestions will appear here.</p>';
        modal.querySelector('#apply-project-ai-btn').disabled = true;

        if (actionType === 'enhance_single_project_bullet') {
            titleEl.textContent = 'AI Enhance Project Bullet';
            subtitleEl.textContent = 'Refine your project bullet point for better impact.';
            singleBulletFields.classList.remove('hidden');
            generateBulletsFields.classList.add('hidden');
            enhancementTypeContainer.classList.remove('hidden');
            submitBtn.innerHTML = '<i class="fas fa-rocket mr-2"></i> Enhance Bullet';
            indicatorText.textContent = "Enhancing...";
            modal.querySelector('#project_ai_bullet_index_modal').value = bulletIdx;
            modal.querySelector('#project_ai_bullet_id_modal').value = bulletId;
            modal.querySelector('#project_ai_original_bullet_modal').value = bulletText;
            form.setAttribute('hx-post', window.enhanceProjectBulletUrl || '');
        } else if (actionType === 'generate_project_bullets') {
            titleEl.textContent = 'AI Generate Project Bullets';
            subtitleEl.textContent = 'Provide context to generate multiple relevant bullet points.';
            singleBulletFields.classList.add('hidden');
            generateBulletsFields.classList.remove('hidden');
            enhancementTypeContainer.classList.add('hidden');
            submitBtn.innerHTML = '<i class="fas fa-wand-magic-sparkles mr-2"></i> Generate Bullets';
            indicatorText.textContent = "Generating...";
            modal.querySelector('#project_ai_bullet_index_modal').value = '';
            modal.querySelector('#project_ai_bullet_id_modal').value = '';
            modal.querySelector('#project_ai_original_bullet_modal').value = '';
            modal.querySelector('#project_ai_target_job_title_modal').value = '';
            modal.querySelector('#project_ai_skills_modal').value = '';
            form.setAttribute('hx-post', window.generateProjectBulletsUrl || '');
        }
        openModal('project-enhancement-modal');
    }

    const applyProjectAIBtn = document.getElementById('apply-project-ai-btn');
    if(applyProjectAIBtn) {
        applyProjectAIBtn.addEventListener('click', function() {
            const projectIndex = document.getElementById('project_ai_parent_index_modal').value;
            const actionType = document.getElementById('project_ai_action_type_modal').value;
            const aiResultArea = document.getElementById('project_ai_result_area');

            if (actionType === 'enhance_single_project_bullet') {
                const bulletIndex = document.getElementById('project_ai_bullet_index_modal').value;
                const enhancedText = aiResultArea.querySelector('p')?.textContent.trim() || aiResultArea.textContent.trim(); // Get text from p or div

                const targetTextareaId = `id_projects-${projectIndex}-bullets-${bulletIndex}-description`;
                const targetTextarea = document.getElementById(targetTextareaId);

                if (targetTextarea && enhancedText) {
                    targetTextarea.value = enhancedText;
                } else {
                    console.error(`Target textarea for project bullet not found (ID: ${targetTextareaId}) or no text.`);
                }
            } else if (actionType === 'generate_project_bullets') {
                const bulletItems = aiResultArea.querySelectorAll('li, p.generated-bullet-item');
                const addBulletButton = document.querySelector(`.project-form[data-project-form-index="${projectIndex}"] .add-project-bullet-form`);

                bulletItems.forEach(bulletItem => {
                    const bulletText = bulletItem.textContent.trim();
                    if (bulletText && addBulletButton) {
                        addBulletButton.click();
                        const bulletsContainer = document.getElementById(`project-bullet-forms-${projectIndex}`);
                        const newBulletFormRow = bulletsContainer.lastElementChild;
                        if (newBulletFormRow) {
                            const newTextarea = newBulletFormRow.querySelector('textarea[name$="-description"]');
                            if (newTextarea) newTextarea.value = bulletText;
                        }
                    }
                });
            }
            closeModal('project-enhancement-modal');
        });
    }

    const projectAiResultDiv = document.getElementById('project_ai_result_area');
    if (projectAiResultDiv) {
        projectAiResultDiv.addEventListener('htmx:afterSwap', function(event) {
            if (event.detail.xhr.status === 200 && this.innerHTML.trim() !== '' && !this.querySelector('.text-red-500')) {
                const hasContent = this.querySelectorAll('li, p.generated-bullet-item').length > 0 ||
                                   (this.textContent.trim() !== '' && this.textContent.trim().toLowerCase() !== 'suggestions will appear here.' && this.textContent.trim().toLowerCase() !== 'suggestion will appear here.');
                document.getElementById('apply-project-ai-btn').disabled = !hasContent;
            } else {
                 document.getElementById('apply-project-ai-btn').disabled = true;
            }
        });
    }

    document.querySelectorAll('.project-form').forEach((formElement) => {
        const index = formElement.dataset.projectFormIndex;
        initializeProjectBulletManagement(formElement, index);
        initializeAIButtonsForProject(formElement, index);
        const techSelect = formElement.querySelector('select[name$="-technologies"]');
        // if (window.TomSelect && techSelect && !techSelect.classList.contains('tomselected')) {
        //    new TomSelect(techSelect,{create: true, persist: false });
        // }
    });
});


// // project_enhancement.js - Add to your static/js directory
//
// /**
//  * Opens the project enhancement modal and populates it with data
//  *
//  * @param {string} parentIndex - The parent index of the bullet point
//  * @param {string} bulletIndex - The index of the bullet point
//  * @param {string} projectName - The name of the project
//  * @param {string} projectTitle - The title/role of the project (optional)
//  * @param {string} projectSummary - The summary of the project (optional)
//  */
// function openProjectEnhanceModal(parentIndex, bulletIndex, projectName, projectTitle = "", projectSummary = "") {
//     console.log("Opening project enhancement modal for bullet:", parentIndex, bulletIndex);
//     const modal = document.getElementById('project-enhancement-modal');
//     if (!modal) {
//         console.error("Enhancement modal not found!");
//         return;
//     }
//
//     // Get the bullet text
//     const bulletTextarea = document.getElementById(`bullet_${parentIndex}_${bulletIndex}`);
//     if (!bulletTextarea) {
//         console.error("Bullet textarea not found:", `bullet_${parentIndex}_${bulletIndex}`);
//         return;
//     }
//
//     const bulletText = bulletTextarea.value.trim();
//     if (!bulletText) {
//         alert('Please enter some text in the bullet point first.');
//         return;
//     }
//
//     // Set hidden fields and original bullet text
//     document.getElementById('parent_index_modal').value = parentIndex;
//     document.getElementById('bullet_index_modal').value = bulletIndex;
//     document.getElementById('original_bullet_modal').value = bulletText;
//
//     // Set project context fields
//     document.getElementById('project_name_modal').value = projectName;
//     document.getElementById('project_title_modal').value = projectTitle || "";
//     document.getElementById('project_summary_modal').value = projectSummary || "";
//
//     // Update display text
//     document.getElementById('project_name_display').textContent = projectName;
//     document.getElementById('project_title_display').textContent = projectTitle || "(Not specified)";
//     document.getElementById('project_summary_display').textContent = projectSummary || "(No summary provided)";
//
//     // Reset enhancement options and results
//     document.getElementById('enhancement-general').checked = true;
//     document.getElementById('enhance-engine-chatgpt').checked = true;
//     document.getElementById('enhancement_in_progress').classList.add('hidden');
//     document.getElementById('enhanced_bullet_result').innerHTML = '<p class="text-gray-400 italic">Enhanced bullet point will appear here</p>';
//     document.getElementById('apply_enhancement_btn').disabled = true;
//
//     // Show the modal
//     modal.classList.remove('hidden');
//     modal.style.display = 'block';
//     document.body.classList.add('overflow-hidden');
// }
//
// /**
//  * Closes the project enhancement modal
//  */
// function closeProjectEnhanceModal() {
//     const modal = document.getElementById('project-enhancement-modal');
//     if (modal) {
//         modal.classList.add('hidden');
//         modal.style.display = 'none';
//         document.body.classList.remove('overflow-hidden');
//     }
// }
//
// /**
//  * Apply the enhanced bullet point back to the form
//  */
// function applyProjectEnhancement() {
//     console.log("Applying project enhancement");
//     const parentIndex = document.getElementById('parent_index_modal').value;
//     const bulletIndex = document.getElementById('bullet_index_modal').value;
//     const enhancedBullet = document.getElementById('enhanced_bullet_result').textContent.trim();
//
//     // Find the textarea to update
//     const bulletTextarea = document.getElementById(`bullet_${parentIndex}_${bulletIndex}`);
//     if (bulletTextarea && enhancedBullet && enhancedBullet !== "Enhanced bullet point will appear here") {
//         // Update the textarea
//         bulletTextarea.value = enhancedBullet;
//
//         // Update the bullet quality display if that function exists
//         if (typeof checkBulletQuality === 'function') {
//             checkBulletQuality(bulletTextarea);
//         }
//
//         // Add a highlight effect
//         bulletTextarea.classList.add('bg-green-50', 'border-green-300');
//         setTimeout(() => {
//             bulletTextarea.classList.remove('bg-green-50', 'border-green-300');
//         }, 1500);
//
//         // Close the modal
//         closeProjectEnhanceModal();
//
//         // Show success message (if you have a toast system)
//         if (typeof showToast === 'function') {
//             showToast("Bullet point enhanced successfully!", "success");
//         }
//     } else {
//         console.error("Could not find bullet textarea or enhanced text");
//         if (typeof showToast === 'function') {
//             showToast("Error applying enhancement", "error");
//         } else {
//             alert("Error applying enhancement. Please try again.");
//         }
//     }
// }
//
// // Handle successful enhancement result
// document.addEventListener('htmx:afterSwap', function(evt) {
//     if (evt.detail.target.id === 'enhanced_bullet_result') {
//         // Enable the apply button
//         const applyBtn = document.getElementById('apply_enhancement_btn');
//         if (applyBtn) {
//             applyBtn.disabled = false;
//         }
//
//         // Check the content length and provide feedback
//         const resultText = evt.detail.target.textContent.trim();
//         const resultLength = resultText.length;
//         let qualityClass = '';
//         let qualityMessage = '';
//
//         if (resultLength >= 80 && resultLength <= 150) {
//             qualityClass = 'text-success';
//             qualityMessage = 'Excellent length and impact';
//         } else if (resultLength > 150) {
//             qualityClass = 'text-warning';
//             qualityMessage = 'Good but slightly long';
//         } else {
//             qualityClass = 'text-warning';
//             qualityMessage = 'Good but could be more detailed';
//         }
//
//         // Add quality indicator if it doesn't exist
//         const qualityIndicator = document.createElement('div');
//         qualityIndicator.id = 'quality_indicator';
//         qualityIndicator.className = `mt-2 text-sm ${qualityClass}`;
//         qualityIndicator.textContent = qualityMessage;
//
//         // Replace existing indicator or add new one
//         const existingIndicator = document.getElementById('quality_indicator');
//         if (existingIndicator) {
//             existingIndicator.replaceWith(qualityIndicator);
//         } else {
//             evt.detail.target.appendChild(qualityIndicator);
//         }
//     }
// });
//
// // Document ready handler to bind events
// document.addEventListener('DOMContentLoaded', function() {
//     // If project-enhancement-form exists outside of HTMX requests, set up form submission
//     const enhancementForm = document.getElementById('project-enhancement-form');
//     if (enhancementForm) {
//         enhancementForm.addEventListener('submit', function(e) {
//             // Let HTMX handle the form submission
//             console.log("Project enhancement form submitted via HTMX");
//         });
//     }
//
//     // Set up event listeners for any enhance buttons already in the DOM
//     const enhanceButtons = document.querySelectorAll('.project-enhance-btn');
//     enhanceButtons.forEach(btn => {
//         const parentIndex = btn.getAttribute('data-parent');
//         const bulletIndex = btn.getAttribute('data-index');
//         const projectName = btn.getAttribute('data-project-name');
//         const projectTitle = btn.getAttribute('data-project-title');
//         const projectSummary = btn.getAttribute('data-project-summary');
//
//         if (parentIndex && bulletIndex && projectName) {
//             btn.addEventListener('click', function() {
//                 openProjectEnhanceModal(parentIndex, bulletIndex, projectName, projectTitle, projectSummary);
//             });
//         }
//     });
// });