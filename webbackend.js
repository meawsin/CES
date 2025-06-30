const API_BASE_URL = "http://127.0.0.1:5000/api";

// DOM Elements
const headerStudentName = document.getElementById("headerStudentName");
const logoutButton = document.getElementById("logoutBtn"); // Updated ID
const welcomeMessage = document.getElementById("welcomeMessage");
const studentBatchDepartment = document.getElementById("studentBatchDepartment");
const profileImage = document.getElementById("profileImage");

// Tab Buttons (updated IDs for consistency)
const tabPendingEvaluations = document.getElementById("tabPendingEvaluations");
const tabMyProfile = document.getElementById("tabMyProfile");
const tabCompletedEvaluations = document.getElementById("tabCompletedEvaluations");
const tabComplaints = document.getElementById("tabComplaints");

// Sidebar Links (updated IDs for consistency)
const pendingEvaluationsLink = document.getElementById("pendingEvaluationsLink");
const myProfileLink = document.getElementById("myProfileLink");
const completedEvaluationsLink = document.getElementById("completedEvaluationsLink");
const complaintsLink = document.getElementById("complaintsLink");

// Content Containers
const pendingEvaluationsContent = document.getElementById("pendingEvaluationsContent");
const myProfileContent = document.getElementById("myProfileContent");
const completedEvaluationsContent = document.getElementById("completedEvaluationsContent");
const complaintsContent = document.getElementById("complaintsContent");

// Pending Evaluations elements
const loadingPending = document.getElementById("loadingPending");
const noPendingEvaluations = document.getElementById("noPendingEvaluations");
const pendingEvaluationsList = document.getElementById("pendingEvaluationsList");

// My Profile elements
const profileLoading = document.getElementById("profileLoading");
const profileError = document.getElementById("profileError");
const profileDetails = document.getElementById("profileDetails");
const saveProfileButton = document.getElementById("saveProfileButton");

// Profile fields display (span) and editable input elements (dynamic based on HTML)
// Store references to the actual span and input elements for profile fields
const profileFields = {
    student_id: document.getElementById("profileStudentId"),
    name: document.getElementById("profileName"),
    email: document.getElementById("profileEmail"),
    contact_no: document.getElementById("profileContactNo"),
    dob: document.getElementById("profileDob"),
    gender: document.getElementById("profileGender"),
    session: document.getElementById("profileSession"),
    batch: document.getElementById("profileBatch"),
    department: document.getElementById("profileDepartment"),
    enrollment_date: document.getElementById("profileEnrollmentDate"),
    cgpa: document.getElementById("profileCgpa"),
    behavioral_records: document.getElementById("profileBehavioralRecords"),
    profile_picture: document.getElementById("profilePictureUrl"),
};

// Map editable field names to their display span, input, and edit icon
const editableProfileFields = {
    name: {
        span: profileFields.name,
        input: document.getElementById("editName"),
    },
    contact_no: {
        span: profileFields.contact_no,
        input: document.getElementById("editContactNo"),
    },
    behavioral_records: {
        span: profileFields.behavioral_records,
        input: document.getElementById("editBehavioralRecords"),
    },
    profile_picture: {
        span: profileFields.profile_picture,
        input: document.getElementById("editProfilePictureUrl"),
    },
};

// Completed Evaluations elements
const loadingCompleted = document.getElementById("loadingCompleted");
const noCompletedEvaluations = document.getElementById("noCompletedEvaluations");
const completedEvaluationsList = document.getElementById("completedEvaluationsList");

// Complaints elements
const complaintForm = document.getElementById("complaintForm");
const complaintCourse = document.getElementById("complaintCourse");
const complaintIssueType = document.getElementById("complaintIssueType");
const complaintDetails = document.getElementById("complaintDetails");
const complaintMessageBox = document.getElementById("complaintMessageBox");
const complaintMessageText = document.getElementById("complaintMessageText");
const complaintSuccess = document.getElementById("complaintSuccess");

let currentStudentData = null; // To store full student profile data

// --- Robust Error Handling Helper ---
function handleApiError(response) {
    if (response.status === 401) {
        alert('Session expired. Please log in again.');
        localStorage.clear();
        window.location.href = 'student_login.html';
        return true;
    }
    if (response.status === 404) {
        alert('Feature not available. Please contact admin.');
        return true;
    }
    return false;
}

// --- Initialization ---
document.addEventListener("DOMContentLoaded", () => {
    const studentToken = localStorage.getItem("studentToken");
    const studentId = localStorage.getItem("studentId");
    const studentName = localStorage.getItem("studentName");

    // Redirect to login if no token or essential info is found
    if (!studentToken || !studentId || !studentName) {
        localStorage.clear();
        window.location.href = "student_login.html";
        return;
    }

    // Populate header and welcome message
    headerStudentName.textContent = `Welcome, ${studentName}`;
    welcomeMessage.textContent = `Welcome, ${studentName} 👋`;

    // Set initial active tab (default to pending evaluations)
    showTab("pendingEvaluations");
});

// --- Tab Switching Logic ---
function showTab(tabName) {
    // Hide all content sections and deactivate all tab buttons
    const allTabContents = [pendingEvaluationsContent, myProfileContent, completedEvaluationsContent, complaintsContent];
    const allTabButtons = [tabPendingEvaluations, tabMyProfile, tabCompletedEvaluations, tabComplaints];

    allTabContents.forEach(content => content.classList.remove("active"));
    allTabButtons.forEach(button => button.classList.remove("active"));

    // Activate selected tab and show content with animation
    let currentContent;
    let currentButton;

    switch (tabName) {
        case "pendingEvaluations":
            currentContent = pendingEvaluationsContent;
            currentButton = tabPendingEvaluations;
            loadPendingEvaluations();
            break;
        case "myProfile":
            currentContent = myProfileContent;
            currentButton = tabMyProfile;
            loadMyProfile();
            break;
        case "completedEvaluations":
            currentContent = completedEvaluationsContent;
            currentButton = tabCompletedEvaluations;
            loadCompletedEvaluations();
            break;
        case "complaints":
            currentContent = complaintsContent;
            currentButton = tabComplaints;
            // No specific load function for complaints, just show the form
            break;
    }

    if (currentContent && currentButton) {
        currentContent.classList.add("active");
        currentButton.classList.add("active");
    }
}

// --- Event Listeners for Tabs and Sidebar ---
tabPendingEvaluations.addEventListener("click", () => showTab("pendingEvaluations"));
tabMyProfile.addEventListener("click", () => showTab("myProfile"));
tabCompletedEvaluations.addEventListener("click", () => showTab("completedEvaluations"));
tabComplaints.addEventListener("click", () => showTab("complaints"));

pendingEvaluationsLink.addEventListener("click", (e) => { e.preventDefault(); showTab("pendingEvaluations"); });
myProfileLink.addEventListener("click", (e) => { e.preventDefault(); showTab("myProfile"); });
completedEvaluationsLink.addEventListener("click", (e) => { e.preventDefault(); showTab("completedEvaluations"); });
complaintsLink.addEventListener("click", (e) => { e.preventDefault(); showTab("complaints"); });

// --- Logout Functionality ---
logoutButton.addEventListener("click", async () => {
    localStorage.clear();
    window.location.href = "student_login.html";
});

// --- Helper function for authenticated API fetches ---
async function authenticatedFetch(url, options = {}) {
    const studentToken = localStorage.getItem("studentToken");
    if (!studentToken) {
        alert("Session expired or not logged in. Please log in again.");
        localStorage.clear();
        window.location.href = "student_login.html";
        throw new Error("No authentication token found.");
    }
    options.headers = {
        ...options.headers,
        Authorization: `Bearer ${studentToken}`,
    };
    let response;
    try {
        response = await fetch(url, options);
    } catch (err) {
        alert('Network error. Please check your API server.');
        throw err;
    }
    if (handleApiError(response)) throw new Error('API error handled');
    return response;
}

// --- Pending Evaluations Logic ---
async function loadPendingEvaluations() {
    loadingPending.classList.remove("hidden"); // Show loading indicator
    noPendingEvaluations.classList.add("hidden"); // Hide no data message
    pendingEvaluationsList.innerHTML = ""; // Clear previous list content

    try {
        const response = await authenticatedFetch(`${API_BASE_URL}/student/evaluations/assigned`);

        if (response.ok) {
            const evaluations = await response.json();
            loadingPending.classList.add("hidden"); // Hide loading indicator

            if (evaluations.length === 0) {
                noPendingEvaluations.classList.remove("hidden"); // Show no data message
            } else {
                evaluations.forEach((evaluation) => {
                    const evalCard = document.createElement("div");
                    evalCard.className = "evaluation-item flex flex-col rounded-xl shadow-md bg-white p-4 space-y-3"; // Added Tailwind classes
                    evalCard.innerHTML = `
                        <div class="flex-grow">
                            <h3 class="text-xl font-semibold text-gray-900">${evaluation.title}</h3>
                            <p class="text-sm text-gray-600">
                                ${evaluation.course_code ? `Course: ${evaluation.course_code}` : ""}
                                ${evaluation.batch ? `Batch: ${evaluation.batch}` : ""}
                                ${evaluation.session ? `Session: ${evaluation.session}` : ""}
                            </p>
                            <p class="text-xs text-gray-500 mt-1">Due: ${evaluation.last_date || "N/A"}</p>
                        </div>
                        <div class="mt-4 self-end">
                            <button class="take-evaluation-button bg-teal-600 hover:bg-teal-700 text-white px-4 py-2 rounded-lg shadow-md transition duration-300 ease-in-out transform hover:scale-105"
                                    data-evaluation-id="${evaluation.id}"
                                    data-course-code="${evaluation.course_code || ""}">
                                <i class="fas fa-pencil-alt mr-2"></i>Take Evaluation
                            </button>
                        </div>
                    `;
                    pendingEvaluationsList.appendChild(evalCard);
                });

                // Attach event listeners to "Take Evaluation" buttons
                document.querySelectorAll(".take-evaluation-button").forEach((button) => {
                    button.addEventListener("click", (event) => {
                        const evalId = event.target.dataset.evaluationId;
                        const courseCode = event.target.dataset.courseCode;
                        window.location.href = `take_evaluation.html?evalId=${evalId}&courseCode=${courseCode}`;
                    });
                });
            }
        } else {
            loadingPending.classList.add("hidden"); // Hide loading indicator
            const errorData = await response.json();
            noPendingEvaluations.textContent = `Failed to load evaluations: ${errorData.message || response.statusText}`;
            noPendingEvaluations.classList.remove("hidden"); // Show error message
            console.error("Failed to load evaluations:", errorData);
        }
    } catch (error) {
        loadingPending.classList.add("hidden"); // Hide loading indicator
        if (error.message !== "Unauthorized access, redirecting to login." && error.message !== "No authentication token found.") {
            noPendingEvaluations.textContent = "Network error. Please check your API server.";
            noPendingEvaluations.classList.remove("hidden");
            console.error("Network error loading evaluations:", error);
        }
    }
}

// --- My Profile Logic ---
async function loadMyProfile() {
    profileLoading.classList.remove("hidden"); // Show loading indicator
    profileError.classList.add("hidden"); // Hide error message
    profileDetails.classList.add("hidden"); // Hide profile details
    saveProfileButton.classList.add("hidden"); // Hide save button

    const studentId = localStorage.getItem("studentId");

    try {
        const response = await authenticatedFetch(`${API_BASE_URL}/student/profile`);

        if (response.ok) {
            currentStudentData = await response.json(); // Store full profile data
            profileLoading.classList.add("hidden"); // Hide loading
            profileDetails.classList.remove("hidden"); // Show profile details

            // Populate static fields
            profileFields.student_id.textContent = currentStudentData.student_id || "N/A";
            profileFields.email.textContent = currentStudentData.email || "N/A";
            profileFields.dob.textContent = currentStudentData.dob || "N/A";
            profileFields.gender.textContent = currentStudentData.gender || "N/A";
            profileFields.session.textContent = currentStudentData.session || "N/A";
            profileFields.batch.textContent = currentStudentData.batch || "N/A";
            profileFields.department.textContent = currentStudentData.department || "N/A";
            profileFields.enrollment_date.textContent = currentStudentData.enrollment_date || "N/A";
            profileFields.cgpa.textContent = currentStudentData.cgpa || "N/A";

            // Update header and profile image
            studentBatchDepartment.textContent = `Batch: ${currentStudentData.batch || "N/A"}, Dept: ${currentStudentData.department || "N/A"}`;
            if (currentStudentData.profile_picture) {
                profileImage.src = currentStudentData.profile_picture;
            } else {
                profileImage.src = "https://placehold.co/100x100/cccccc/ffffff?text=Profile"; // Default placeholder
            }

            // Populate editable fields and attach event listeners
            for (const fieldName in editableProfileFields) {
                const { span, input } = editableProfileFields[fieldName];
                span.textContent = currentStudentData[fieldName] || "N/A";
                input.value = currentStudentData[fieldName] || "";

                // Attach event listener to the edit icon
                const editIcon = document.querySelector(`.edit-icon[data-field="${fieldName}"]`);
                if (editIcon) {
                    editIcon.onclick = () => enableEdit(fieldName);
                }

                input.onblur = () => disableEdit(fieldName); // Save on blur
                input.onkeydown = (e) => {
                    if (e.key === "Enter") {
                        e.preventDefault(); // Prevent form submission
                        disableEdit(fieldName);
                    }
                };
            }
        } else {
            profileLoading.classList.add("hidden"); // Hide loading
            const errorData = await response.json();
            profileError.textContent = `Failed to load profile: ${errorData.message || response.statusText}`;
            profileError.classList.remove("hidden"); // Show error message
            console.error("Failed to load profile:", errorData);
        }
    } catch (error) {
        profileLoading.classList.add("hidden"); // Hide loading
        if (error.message !== "Unauthorized access, redirecting to login." && error.message !== "No authentication token found.") {
            profileError.textContent = "Network error. Please check your API server.";
            profileError.classList.remove("hidden");
            console.error("Network error loading profile:", error);
        }
    }
}

function enableEdit(fieldName) {
    const { span, input } = editableProfileFields[fieldName];
    const editIcon = document.querySelector(`.edit-icon[data-field="${fieldName}"]`);

    span.classList.add("hidden"); // Hide display span
    input.classList.remove("hidden"); // Show input field
    input.focus(); // Focus on the input

    if (editIcon) {
        editIcon.classList.add("hidden"); // Hide edit icon
    }
    saveProfileButton.classList.remove("hidden"); // Show save button
}

async function disableEdit(fieldName) {
    const { span, input } = editableProfileFields[fieldName];
    const editIcon = document.querySelector(`.edit-icon[data-field="${fieldName}"]`);
    const newValue = input.value.trim();

    // Hide input, show span immediately for responsiveness
    input.classList.add("hidden");
    span.classList.remove("hidden");
    span.textContent = newValue || "N/A"; // Optimistic update

    if (editIcon) {
        editIcon.classList.remove("hidden"); // Show edit icon again
    }

    // If value changed, send update to API
    if (newValue !== (currentStudentData[fieldName] || "")) {
        try {
            const response = await authenticatedFetch(`${API_BASE_URL}/student/profile/update`, {
                method: "PUT",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ [fieldName]: newValue }),
            });

            const data = await response.json();
            if (response.ok) {
                currentStudentData[fieldName] = newValue; // Update local data
                // alert("Profile updated successfully!"); // Use a more subtle notification
                // Special handling for profile_picture to update img src
                if (fieldName === "profile_picture" && newValue) {
                    profileImage.src = newValue;
                }
                // Check if any other editable fields are open. If not, hide save button.
                checkAndHideSaveButton();
            } else {
                alert("Failed to update profile: " + (data.message || response.statusText));
                // Revert optimistic update if API fails
                span.textContent = currentStudentData[fieldName] || "N/A";
                console.error("Profile update error:", data);
            }
        } catch (error) {
            alert("Network error during profile update.");
            span.textContent = currentStudentData[fieldName] || "N/A";
            console.error("Network error profile update:", error);
        }
    } else {
        // If value didn't change, just hide the save button if no other fields are being edited
        checkAndHideSaveButton();
    }
}

// Helper to check if any input is still active and hide save button accordingly
function checkAndHideSaveButton() {
    let anyFieldStillEditing = false;
    for (const key in editableProfileFields) {
        if (!editableProfileFields[key].input.classList.contains("hidden")) {
            anyFieldStillEditing = true;
            break;
        }
    }
    if (!anyFieldStillEditing) {
        saveProfileButton.classList.add("hidden");
    }
}

saveProfileButton.addEventListener("click", async () => {
    // Trigger blur for all active input fields to save any unsaved changes
    for (const fieldName in editableProfileFields) {
        const { input } = editableProfileFields[fieldName];
        if (!input.classList.contains("hidden")) {
            input.blur(); // This will trigger disableEdit for each
        }
    }
    // The actual saving is handled by disableEdit on blur/enter.
    // The saveProfileButton will be hidden automatically by disableEdit if no fields are in edit mode.
});

// --- Completed Evaluations Logic ---
async function loadCompletedEvaluations() {
    loadingCompleted.classList.remove("hidden");
    noCompletedEvaluations.classList.add("hidden");
    completedEvaluationsList.innerHTML = "";

    try {
        const response = await authenticatedFetch(`${API_BASE_URL}/student/evaluations/completed`);

        if (response.ok) {
            const completedEvaluations = await response.json();
            loadingCompleted.classList.add("hidden");

            if (completedEvaluations.length === 0) {
                noCompletedEvaluations.classList.remove("hidden");
            } else {
                completedEvaluations.forEach((evaluation) => {
                    const evalCard = document.createElement("div");
                    evalCard.className = "evaluation-item flex flex-col rounded-xl shadow-md bg-white p-4 space-y-3";
                    evalCard.innerHTML = `
                        <div class="flex-grow">
                            <h3 class="text-xl font-semibold text-gray-900">${evaluation.title}</h3>
                            <p class="text-sm text-gray-600">
                                Course: ${evaluation.course_name} (${evaluation.course_code})
                            </p>
                            <p class="text-xs text-gray-500 mt-1">Completed On: ${evaluation.completion_date}</p>
                        </div>
                        <div class="mt-4 self-end">
                            <button class="view-evaluation-button bg-gray-300 hover:bg-gray-400 text-gray-800 px-4 py-2 rounded-lg shadow-md transition duration-300 ease-in-out transform hover:scale-105">
                                <i class="fas fa-eye mr-2"></i>View Details
                            </button>
                        </div>
                    `;
                    completedEvaluationsList.appendChild(evalCard);
                });
                // Note: 'View Details' button functionality is not yet implemented in backend,
                // so it's a placeholder button for now.
            }
        } else {
            loadingCompleted.classList.add("hidden");
            const errorData = await response.json();
            noCompletedEvaluations.textContent = `Failed to load completed evaluations: ${errorData.message || response.statusText}`;
            noCompletedEvaluations.classList.remove("hidden");
            console.error("Failed to load completed evaluations:", errorData);
        }
    } catch (error) {
        loadingCompleted.classList.add("hidden");
        if (error.message !== "Unauthorized access, redirecting to login." && error.message !== "No authentication token found.") {
            noCompletedEvaluations.textContent = "Network error. Please check your API server.";
            noCompletedEvaluations.classList.remove("hidden");
            console.error("Network error loading completed evaluations:", error);
        }
    }
}

// --- Complaints Logic ---
complaintForm.addEventListener("submit", async (e) => {
    e.preventDefault();
    complaintMessageBox.classList.add("hidden");
    complaintSuccess.classList.add("hidden");

    const complaintData = {
        course_code: complaintCourse.value.trim() || null, // null if empty
        issue_type: complaintIssueType.value,
        details: complaintDetails.value.trim(),
    };

    // Frontend validation
    if (!complaintData.issue_type) {
        complaintMessageText.textContent = "Please select an issue type.";
        complaintMessageBox.classList.remove("hidden");
        return;
    }
    if (!complaintData.details) {
        complaintMessageText.textContent = "Please provide details for your complaint.";
        complaintMessageBox.classList.remove("hidden");
        return;
    }

    try {
        const response = await authenticatedFetch(`${API_BASE_URL}/student/complaints/submit`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(complaintData),
        });

        const data = await response.json();
        if (response.ok) {
            complaintSuccess.classList.remove("hidden"); // Show success message
            complaintForm.reset(); // Clear the form fields
        } else {
            complaintMessageText.textContent = data.message || "Failed to submit complaint.";
            complaintMessageBox.classList.remove("hidden"); // Show error message
            console.error("Complaint submission error:", data);
        }
    } catch (error) {
        if (error.message !== "Unauthorized access, redirecting to login." && error.message !== "No authentication token found.") {
            complaintMessageText.textContent = "Network error. Please check your API server.";
            complaintMessageBox.classList.remove("hidden");
            console.error("Network error complaint submission:", error);
        }
    }
});

