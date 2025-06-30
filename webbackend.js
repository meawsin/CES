const API_BASE_URL = "http://127.0.0.1:5000/api";

// DOM Elements
const headerStudentName = document.getElementById("headerStudentName");
const logoutButton = document.getElementById("logoutBtn"); // Desktop logout button
const welcomeMessage = document.getElementById("welcomeMessage");
const studentBatchDepartment = document.getElementById("studentBatchDepartment");

// Tab Buttons (Desktop)
const tabPendingEvaluations = document.getElementById("tabPendingEvaluations");
const tabMyProfile = document.getElementById("tabMyProfile");
const tabCompletedEvaluations = document.getElementById("tabCompletedEvaluations");
const tabComplaints = document.getElementById("tabComplaints");
const tabRequestFaculty = document.getElementById("tabRequestFaculty");

// Mobile Sidebar Elements
const sidebarToggle = document.getElementById("sidebarToggle");
const mobileSidebar = document.getElementById("mobileSidebar");
const mobileSidebarBackdrop = document.getElementById("mobileSidebarBackdrop");
const mobileSidebarTabButtons = document.querySelectorAll("#mobileSidebar .tab-button");
const mobileProfileImage = document.getElementById("mobileProfileImage"); // Profile image in mobile sidebar

// Content Containers
const pendingEvaluationsContent = document.getElementById("pendingEvaluationsContent");
const myProfileContent = document.getElementById("myProfileContent");
const completedEvaluationsContent = document.getElementById("completedEvaluationsContent");
const complaintsContent = document.getElementById("complaintsContent");
const requestFacultyContent = document.getElementById("requestFacultyContent");

// Pending Evaluations elements
const loadingPending = document.getElementById("loadingPending");
const noPendingEvaluations = document.getElementById("noPendingEvaluations");
const pendingEvaluationsList = document.getElementById("pendingEvaluationsList");

// My Profile elements
const profileLoading = document.getElementById("profileLoading");
const profileError = document.getElementById("profileError");
const profileDetails = document.getElementById("profileDetails");
const saveProfileButton = document.getElementById("saveProfileButton");

// Profile fields display (span) and editable input elements
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
const complaintMessageBox = document.getElementById("complaintMessageBox"); // Still used for inline error
const complaintMessageText = document.getElementById("complaintMessageText"); // Still used for inline error
const complaintSuccess = document.getElementById("complaintSuccess");

// Request Faculty elements
const facultyRequestForm = document.getElementById('facultyRequestForm');
const requestCourseName = document.getElementById('requestCourseName'); // Input field for course name
const requestedFacultyName = document.getElementById('requestedFacultyName');
const requestDetails = document.getElementById('requestDetails');
const requestSubmissionSuccess = document.getElementById('requestSubmissionSuccess');
const goToDashboardAfterRequestSubmit = document.getElementById('goToDashboardAfterRequestSubmit');


let currentStudentData = null; // To store full student profile data
let currentCompletedEvaluations = []; // To store current completed evaluations list

// Custom Message Box Elements
const customMessageBoxOverlay = document.getElementById('customMessageBoxOverlay');
const customMessageBoxTitle = document.getElementById('customMessageBoxTitle');
const customMessageBoxContent = document.getElementById('customMessageBoxContent');
const customMessageBoxCloseBtn = document.getElementById('customMessageBoxCloseBtn');

// --- Custom Message Box Function ---
function showCustomMessageBox(title, message) {
    customMessageBoxTitle.textContent = title;
    customMessageBoxContent.textContent = message;
    customMessageBoxOverlay.classList.remove('hidden');
}

customMessageBoxCloseBtn.addEventListener('click', () => {
    customMessageBoxOverlay.classList.add('hidden');
});

// --- Robust Error Handling Helper ---
function handleApiError(response) {
    if (response.status === 401) {
        showCustomMessageBox('Session Expired', 'Your session has expired. Please log in again.');
        localStorage.clear();
        // Redirect to login page only after user acknowledges the message
        customMessageBoxCloseBtn.onclick = () => { window.location.href = 'student_login.html'; };
        return true;
    }
    return false;
}

// --- Initialization ---
document.addEventListener("DOMContentLoaded", () => {
    const studentToken = localStorage.getItem("studentToken");
    const studentId = localStorage.getItem("studentId");
    const studentName = localStorage.getItem("studentName");
    const studentBatch = localStorage.getItem("studentBatch"); // Get batch from local storage
    const studentDepartment = localStorage.getItem("studentDepartment"); // Get department from local storage

    // Redirect to login if no token or essential info is found
    if (!studentToken || !studentId || !studentName) {
        localStorage.clear();
        window.location.href = "student_login.html";
        return;
    }

    // Populate header and welcome message
    // Added null checks for elements to prevent "Cannot set properties of null" errors
    if (headerStudentName) headerStudentName.textContent = `Welcome, ${studentName}`;
    if (welcomeMessage) welcomeMessage.textContent = `Welcome, ${studentName} 👋`;
    if (studentBatchDepartment) studentBatchDepartment.textContent = `Batch: ${studentBatch || "N/A"}, Dept: ${studentDepartment || "N/A"}`;

    // Populate mobile sidebar user info
    if (mobileProfileImage) {
        mobileProfileImage.src = localStorage.getItem("profilePictureUrl") || "https://placehold.co/80x80/cccccc/ffffff?text=Profile";
    }

    // Populate mobile student ID
    if (mobileStudentId) {
        if (studentId) {
            mobileStudentId.textContent = studentId;
        }
    }

    // Determine which tab to show based on URL parameter or default
    const urlParams = new URLSearchParams(window.location.search);
    const initialTab = urlParams.get('tab') || 'pendingEvaluations';
    showTab(initialTab);
});

// --- Automatic Refresh After Actions ---
let currentActiveTab = 'pendingEvaluations'; // Track current active tab

function refreshCurrentTabAfterAction() {
    console.log("Auto-refreshing current tab after action:", currentActiveTab);
    showTab(currentActiveTab);
}

// --- Tab Switching Logic ---
function showTab(tabName) {
    // Update current active tab
    currentActiveTab = tabName;
    
    // Hide all content sections and deactivate all tab buttons
    const allTabContents = [pendingEvaluationsContent, myProfileContent, completedEvaluationsContent, complaintsContent, requestFacultyContent];
    const allTabButtons = [tabPendingEvaluations, tabMyProfile, tabCompletedEvaluations, tabComplaints, tabRequestFaculty];

    allTabContents.forEach(content => { if(content) content.classList.remove("active"); });
    allTabButtons.forEach(button => { if(button) button.classList.remove("active"); });
    // Deactivate mobile sidebar buttons as well
    mobileSidebarTabButtons.forEach(button => { if(button) button.classList.remove("active"); });

    // Activate selected tab and show content with animation
    let currentContent;
    let currentButton; // For desktop tabs
    let currentMobileButton; // For mobile sidebar tabs

    switch (tabName) {
        case "pendingEvaluations":
            currentContent = pendingEvaluationsContent;
            currentButton = tabPendingEvaluations;
            currentMobileButton = document.querySelector('#mobileSidebar button[data-tab-name="pendingEvaluations"]');
            loadPendingEvaluations();
            break;
        case "myProfile":
            currentContent = myProfileContent;
            currentButton = tabMyProfile;
            currentMobileButton = document.querySelector('#mobileSidebar button[data-tab-name="myProfile"]');
            loadMyProfile();
            break;
        case "completedEvaluations":
            currentContent = completedEvaluationsContent;
            currentButton = tabCompletedEvaluations;
            currentMobileButton = document.querySelector('#mobileSidebar button[data-tab-name="completedEvaluations"]');
            loadCompletedEvaluations();
            break;
        case "complaints":
            currentContent = complaintsContent;
            currentButton = tabComplaints;
            currentMobileButton = document.querySelector('#mobileSidebar button[data-tab-name="complaints"]');
            loadComplaintList(); // Calling loadComplaintList here
            break;
        case "requestFaculty":
            currentContent = requestFacultyContent;
            currentButton = tabRequestFaculty;
            currentMobileButton = document.querySelector('#mobileSidebar button[data-tab-name="requestFaculty"]');
            // No longer loading upcoming courses into a select, just showing the input field
            break;
    }

    if (currentContent) {
        currentContent.classList.add("active");
    }
    if (currentButton) { // Desktop button
        currentButton.classList.add("active");
    }
    if (currentMobileButton) { // Mobile button
        currentMobileButton.classList.add("active");
    }

    // Close mobile sidebar if open
    if (mobileSidebar && mobileSidebar.classList.contains('open')) {
        toggleSidebar();
    }
}

// --- Event Listeners for Tabs (Desktop) ---
if (tabPendingEvaluations) tabPendingEvaluations.addEventListener("click", () => showTab("pendingEvaluations"));
if (tabMyProfile) tabMyProfile.addEventListener("click", () => showTab("myProfile"));
if (tabCompletedEvaluations) tabCompletedEvaluations.addEventListener("click", () => showTab("completedEvaluations"));
if (tabComplaints) tabComplaints.addEventListener("click", () => showTab("complaints"));
if (tabRequestFaculty) tabRequestFaculty.addEventListener("click", () => showTab("requestFaculty"));

// --- Mobile Sidebar Toggle ---
if (sidebarToggle) sidebarToggle.addEventListener('click', toggleSidebar);
if (mobileSidebarBackdrop) mobileSidebarBackdrop.addEventListener('click', toggleSidebar);

function toggleSidebar() {
    if (mobileSidebar) mobileSidebar.classList.toggle('open');
    if (mobileSidebarBackdrop) mobileSidebarBackdrop.classList.toggle('open');
    document.body.classList.toggle('overflow-hidden'); // Prevent scrolling body when sidebar is open
    const mainContentWrapper = document.querySelector('.main-content-wrapper');
    const topNavBar = document.querySelector('.top-nav-bar');
    if (mainContentWrapper) mainContentWrapper.classList.toggle('sidebar-open'); // Adjust main content position
    if (topNavBar) topNavBar.classList.toggle('sidebar-open'); // Adjust top nav bar position
}

// --- Event Listeners for Mobile Sidebar Tabs ---
mobileSidebarTabButtons.forEach(button => {
    button.addEventListener('click', (event) => {
        const tabName = event.currentTarget.dataset.tabName;
        showTab(tabName);
    });
});

// --- Logout Functionality ---
// Both desktop and mobile logout buttons will call this function
function handleLogout() {
    // Optionally, send a logout request to the backend
    try {
        authenticatedFetch(`${API_BASE_URL}/student/logout`, { method: "POST" });
    } catch (error) {
        console.error("Logout API failed, but proceeding with client-side logout:", error);
    } finally {
        localStorage.clear();
        // Clear specific items used for UI display
        localStorage.removeItem("studentBatch");
        localStorage.removeItem("studentDepartment");
        localStorage.removeItem("profilePictureUrl");
        window.location.href = "student_login.html";
    }
}

if (logoutButton) logoutButton.addEventListener("click", handleLogout); // Desktop logout

// --- Helper function for authenticated API fetches ---
async function authenticatedFetch(url, options = {}) {
    const studentToken = localStorage.getItem("studentToken");
    if (!studentToken) {
        showCustomMessageBox('Authentication Required', 'Session expired or not logged in. Please log in again.');
        localStorage.clear();
        customMessageBoxCloseBtn.onclick = () => { window.location.href = 'student_login.html'; };
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
        showCustomMessageBox('Network Error', 'Could not connect to the server. Please check your internet connection or API server status.');
        throw err;
    }
    if (handleApiError(response)) {
        throw new Error('API error handled and redirected.');
    }
    return response;
}

// --- Pending Evaluations Logic ---
async function loadPendingEvaluations() {
    if (loadingPending) loadingPending.classList.remove("hidden");
    if (noPendingEvaluations) noPendingEvaluations.classList.add("hidden");
    if (pendingEvaluationsList) pendingEvaluationsList.innerHTML = "";

    try {
        const response = await authenticatedFetch(`${API_BASE_URL}/student/evaluations/assigned`);

        if (response.ok) {
            const evaluations = await response.json();
            if (loadingPending) loadingPending.classList.add("hidden");

            if (evaluations.length === 0) {
                if (noPendingEvaluations) noPendingEvaluations.classList.remove("hidden");
            } else {
                evaluations.forEach((evaluation) => {
                    const evalCard = document.createElement("div");
                    evalCard.className = "evaluation-item flex flex-col rounded-xl shadow-md bg-white p-4 space-y-3";
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
                    if (pendingEvaluationsList) pendingEvaluationsList.appendChild(evalCard);
                });

                document.querySelectorAll(".take-evaluation-button").forEach((button) => {
                    button.addEventListener("click", (event) => {
                        const evalId = event.currentTarget.dataset.evaluationId;
                        const courseCode = event.currentTarget.dataset.courseCode;
                        window.location.href = `take_evaluation.html?evalId=${evalId}&courseCode=${courseCode}`;
                    });
                });
            }
        } else {
            if (loadingPending) loadingPending.classList.add("hidden");
            const errorData = await response.json();
            showCustomMessageBox('Error', `Failed to load evaluations: ${errorData.message || response.statusText}`);
            if (noPendingEvaluations) {
            noPendingEvaluations.textContent = `Failed to load evaluations: ${errorData.message || response.statusText}`;
                noPendingEvaluations.classList.remove("hidden");
            }
            console.error("Failed to load evaluations:", errorData);
        }
    } catch (error) {
        if (loadingPending) loadingPending.classList.add("hidden");
            console.error("Network error loading evaluations:", error);
    }
}

// --- My Profile Logic ---
async function loadMyProfile() {
    if (profileLoading) profileLoading.classList.remove("hidden");
    if (profileError) profileError.classList.add("hidden");
    if (profileDetails) profileDetails.classList.add("hidden");
    if (saveProfileButton) saveProfileButton.classList.add("hidden");

    try {
        const response = await authenticatedFetch(`${API_BASE_URL}/student/profile`);

        if (response.ok) {
            currentStudentData = await response.json();
            if (profileLoading) profileLoading.classList.add("hidden");
            if (profileDetails) profileDetails.classList.remove("hidden");

            // Populate static fields
            if (profileFields.student_id) profileFields.student_id.textContent = currentStudentData.student_id || "N/A";
            if (profileFields.email) profileFields.email.textContent = currentStudentData.email || "N/A";
            if (profileFields.dob) profileFields.dob.textContent = currentStudentData.dob || "N/A";
            if (profileFields.gender) profileFields.gender.textContent = currentStudentData.gender || "N/A";
            if (profileFields.session) profileFields.session.textContent = currentStudentData.session || "N/A";
            if (profileFields.batch) profileFields.batch.textContent = currentStudentData.batch || "N/A";
            if (profileFields.department) profileFields.department.textContent = currentStudentData.department || "N/A";
            if (profileFields.enrollment_date) profileFields.enrollment_date.textContent = currentStudentData.enrollment_date || "N/A";
            if (profileFields.cgpa) profileFields.cgpa.textContent = currentStudentData.cgpa || "N/A";

            // Update header and profile image
            // Store batch and department in local storage for mobile sidebar
            localStorage.setItem("studentBatch", currentStudentData.batch || "N/A");
            localStorage.setItem("studentDepartment", currentStudentData.department || "N/A");
            if (studentBatchDepartment) studentBatchDepartment.textContent = `Batch: ${currentStudentData.batch || "N/A"}, Dept: ${currentStudentData.department || "N/A"}`;
            
            const profilePicUrl = currentStudentData.profile_picture || "https://placehold.co/100x100/cccccc/ffffff?text=Profile";
            if (mobileProfileImage) mobileProfileImage.src = profilePicUrl; // Update mobile sidebar image
            localStorage.setItem("profilePictureUrl", profilePicUrl); // Store for mobile sidebar persistence

            // Populate editable fields and attach event listeners
            for (const fieldName in editableProfileFields) {
                const { span, input } = editableProfileFields[fieldName];
                if (span) span.textContent = currentStudentData[fieldName] || "N/A";
                if (input) input.value = currentStudentData[fieldName] || "";

                const editIcon = document.querySelector(`.edit-icon[data-field="${fieldName}"]`);
                if (editIcon) {
                    editIcon.onclick = () => enableEdit(fieldName);
                }

                if (input) {
                    input.onblur = () => disableEdit(fieldName);
                input.onkeydown = (e) => {
                    if (e.key === "Enter") {
                            e.preventDefault();
                        disableEdit(fieldName);
                    }
                };
                }
            }
        } else {
            if (profileLoading) profileLoading.classList.add("hidden");
            const errorData = await response.json();
            showCustomMessageBox('Error', `Failed to load profile: ${errorData.message || response.statusText}`);
            if (profileError) {
            profileError.textContent = `Failed to load profile: ${errorData.message || response.statusText}`;
                profileError.classList.remove("hidden");
            }
            console.error("Failed to load profile:", errorData);
        }
    } catch (error) {
        if (profileLoading) profileLoading.classList.add("hidden");
            console.error("Network error loading profile:", error);
    }
}

function enableEdit(fieldName) {
    const { span, input } = editableProfileFields[fieldName];
    const editIcon = document.querySelector(`.edit-icon[data-field="${fieldName}"]`);

    if (span) span.classList.add("hidden");
    if (input) input.classList.remove("hidden");
    if (input) input.focus();

    if (editIcon) {
        editIcon.classList.add("hidden");
    }
    if (saveProfileButton) saveProfileButton.classList.remove("hidden");
}

async function disableEdit(fieldName) {
    const { span, input } = editableProfileFields[fieldName];
    const editIcon = document.querySelector(`.edit-icon[data-field="${fieldName}"]`);
    const newValue = input ? input.value.trim() : ''; // Safely get value

    if (input) input.classList.add("hidden");
    if (span) {
    span.classList.remove("hidden");
        span.textContent = newValue || "N/A";
    }

    if (editIcon) {
        editIcon.classList.remove("hidden");
    }

    if (newValue !== (currentStudentData[fieldName] || "")) {
        try {
            const response = await authenticatedFetch(`${API_BASE_URL}/student/profile/update`, {
                method: "PUT",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ [fieldName]: newValue }),
            });

            const data = await response.json();
            if (response.ok) {
                currentStudentData[fieldName] = newValue;
                showCustomMessageBox('Success', 'Profile updated successfully!');
                checkAndHideSaveButton();
                // Auto-refresh profile tab to show updated information
                if (currentActiveTab === 'myProfile') {
                    setTimeout(() => refreshCurrentTabAfterAction(), 1000); // Small delay to show success message
                }
            } else {
                showCustomMessageBox('Error', "Failed to update profile: " + (data.message || response.statusText));
                if (span) span.textContent = currentStudentData[fieldName] || "N/A";
                console.error("Profile update error:", data);
            }
        } catch (error) {
            if (span) span.textContent = currentStudentData[fieldName] || "N/A";
            console.error("Network error profile update:", error);
        }
    } else {
        checkAndHideSaveButton();
    }
}

function checkAndHideSaveButton() {
    let anyFieldStillEditing = false;
    for (const key in editableProfileFields) {
        if (editableProfileFields[key].input && !editableProfileFields[key].input.classList.contains("hidden")) {
            anyFieldStillEditing = true;
            break;
        }
    }
    if (!anyFieldStillEditing) {
        if (saveProfileButton) saveProfileButton.classList.add("hidden");
    }
}

if (saveProfileButton) {
saveProfileButton.addEventListener("click", async () => {
    for (const fieldName in editableProfileFields) {
        const { input } = editableProfileFields[fieldName];
            if (input && !input.classList.contains("hidden")) {
                input.blur();
            }
        }
    });
    }

// --- Completed Evaluations Logic ---
async function loadCompletedEvaluations() {
    if (loadingCompleted) loadingCompleted.classList.remove("hidden");
    if (noCompletedEvaluations) noCompletedEvaluations.classList.add("hidden");
    if (completedEvaluationsList) completedEvaluationsList.innerHTML = "";

    try {
        const response = await authenticatedFetch(`${API_BASE_URL}/student/evaluations/completed`);

        if (response.ok) {
            const completedEvaluations = await response.json();
            if (loadingCompleted) loadingCompleted.classList.add("hidden");

            console.log("Completed evaluations data:", completedEvaluations); // Debug log

            if (completedEvaluations.length === 0) {
                if (noCompletedEvaluations) noCompletedEvaluations.classList.remove("hidden");
            } else {
                displayCompletedEvaluations(completedEvaluations);
            }
        } else {
            if (loadingCompleted) loadingCompleted.classList.add("hidden");
            const errorData = await response.json();
            showCustomMessageBox('Error', `Failed to load completed evaluations: ${errorData.message || response.statusText}`);
            if (noCompletedEvaluations) {
            noCompletedEvaluations.textContent = `Failed to load completed evaluations: ${errorData.message || response.statusText}`;
            noCompletedEvaluations.classList.remove("hidden");
            }
            console.error("Failed to load completed evaluations:", errorData);
        }
    } catch (error) {
        if (loadingCompleted) loadingCompleted.classList.add("hidden");
            console.error("Network error loading completed evaluations:", error);
    }
}

function displayCompletedEvaluations(evaluations) {
    const container = completedEvaluationsList;
    if (!container) return;

    container.innerHTML = '';

    if (!evaluations || evaluations.length === 0) {
        noCompletedEvaluations.classList.remove('hidden');
        return;
    }

    noCompletedEvaluations.classList.add('hidden');
    
    // Store the evaluations for later use
    currentCompletedEvaluations = evaluations;

    evaluations.forEach((evaluation, index) => {
        const card = document.createElement('div');
        card.className = 'evaluation-item bg-white rounded-lg shadow-md p-6 hover:shadow-lg transition-shadow duration-300';

        // Provide fallback values for missing data
        const courseName = evaluation.course_name || evaluation.course_id || 'Course Information Not Available';
        const session = evaluation.session || 'Session Not Available';
        const batch = evaluation.batch || 'Batch Not Available';
        const facultyName = evaluation.faculty_name || 'Faculty Information Not Available';
        const completionDate = evaluation.completion_date || 'Date Not Available';
        const templateName = evaluation.template_name || evaluation.title || 'Evaluation Template';

        card.innerHTML = `
            <div class="flex justify-between items-start mb-4">
                <div class="flex-1">
                    <h4 class="text-lg font-semibold text-gray-800 mb-2">${templateName}</h4>
                    <div class="space-y-1 text-sm text-gray-600">
                        <p><strong>Course:</strong> ${courseName}</p>
                        <p><strong>Faculty:</strong> ${facultyName}</p>
                        <p><strong>Session:</strong> ${session}</p>
                        <p><strong>Batch:</strong> ${batch}</p>
                        <p><strong>Completed:</strong> ${completionDate}</p>
                    </div>
                </div>
                <div class="ml-4">
                    <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">
                        <i class="fas fa-check-circle mr-1"></i>Completed
                    </span>
                </div>
            </div>
            <div class="flex justify-end">
                <button onclick="viewCompletedEvaluationDetails(${index})" 
                        class="view-evaluation-button bg-blue-500 hover:bg-blue-600 text-white px-4 py-2 rounded-md text-sm font-medium transition-colors duration-200">
                    <i class="fas fa-eye mr-2"></i>View Details
                </button>
            </div>
        `;

        container.appendChild(card);
    });
}

async function viewCompletedEvaluationDetails(index) {
    try {
        console.log('Loading evaluation details for index:', index);
        
        // Get the evaluation data from the current evaluations list
        const evaluation = currentCompletedEvaluations[index];
        if (!evaluation) {
            console.error('Evaluation not found in current list');
            showCustomMessageBox('Error', 'Evaluation details not found.');
            return;
        }
        
        // Build URL parameters - only include course_code if it's not "N/A"
        let url = `${API_BASE_URL}/student/evaluations/completed/details?template_id=${evaluation.template_id}`;
        if (evaluation.course_code && evaluation.course_code !== "N/A") {
            url += `&course_code=${encodeURIComponent(evaluation.course_code)}`;
        }
        
        // Use the correct API endpoint with template_id and optional course_code parameters
        const response = await authenticatedFetch(url);
        
        if (response.ok) {
            const data = await response.json();
            console.log('Evaluation details loaded:', data);
            
            // Show evaluation details in a modal
            showEvaluationDetailsModal(data, evaluation);
        } else {
            console.error('Failed to load evaluation details:', response.status);
            showCustomMessageBox('Error', 'Failed to load evaluation details. Please try again.');
        }
    } catch (error) {
        console.error('Error loading evaluation details:', error);
        showCustomMessageBox('Error', 'Failed to load evaluation details. Please try again.');
    }
}

function showEvaluationDetailsModal(evaluationData, evaluation) {
    // Create a simple modal to show evaluation details
    const modalHtml = `
        <div class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
            <div class="bg-white rounded-lg p-6 max-w-2xl w-full mx-4 max-h-[80vh] overflow-y-auto">
                <div class="flex justify-between items-center mb-4">
                    <h3 class="text-xl font-bold text-gray-800">Evaluation Details</h3>
                    <button onclick="closeEvaluationModal()" class="text-gray-500 hover:text-gray-700">
                        <i class="fas fa-times text-xl"></i>
                    </button>
                </div>
                <div class="space-y-4">
                    <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <div>
                            <strong>Template:</strong> ${evaluation.template_name || evaluation.title || 'N/A'}
                        </div>
                        <div>
                            <strong>Course:</strong> ${evaluation.course_name || evaluation.course_code || 'N/A'}
                        </div>
                        <div>
                            <strong>Completed:</strong> ${evaluation.completion_date || 'N/A'}
                        </div>
                    </div>
                    
                    ${evaluationData.feedback ? `
                        <div class="border-t pt-4">
                            <h4 class="font-semibold mb-2">Your Responses:</h4>
                            <div class="space-y-2">
                                ${Object.entries(evaluationData.feedback).map(([question, answer]) => `
                                    <div class="bg-gray-50 p-3 rounded">
                                        <strong>${question}:</strong>
                                        <p class="mt-1">${answer || 'No answer provided'}</p>
                                    </div>
                                `).join('')}
                            </div>
                        </div>
                    ` : '<p class="text-gray-500">No detailed responses available.</p>'}
                    
                    ${evaluationData.comment ? `
                        <div class="border-t pt-4">
                            <h4 class="font-semibold mb-2">General Comment:</h4>
                            <div class="bg-gray-50 p-3 rounded">
                                <p>${evaluationData.comment}</p>
                            </div>
                        </div>
                    ` : ''}
                </div>
                <div class="mt-6 flex justify-end">
                    <button onclick="closeEvaluationModal()" class="bg-gray-500 hover:bg-gray-600 text-white px-4 py-2 rounded">
                        Close
                    </button>
                </div>
            </div>
        </div>
    `;
    
    // Remove any existing modal
    const existingModal = document.querySelector('.evaluation-modal');
    if (existingModal) {
        existingModal.remove();
    }
    
    // Add new modal
    const modalContainer = document.createElement('div');
    modalContainer.className = 'evaluation-modal';
    modalContainer.innerHTML = modalHtml;
    document.body.appendChild(modalContainer);
}

function closeEvaluationModal() {
    const modal = document.querySelector('.evaluation-modal');
    if (modal) {
        modal.remove();
    }
}

// --- Complaints Logic ---
// Moved loadComplaintList function here for proper scope
async function loadComplaintList() {
    const complaintList = document.getElementById('complaintList');
    const noComplaintsMsg = document.getElementById('noComplaintsMsg');
    if (!complaintList || !noComplaintsMsg) {
        console.warn("Complaint list elements not found.");
        return;
    }

    complaintList.innerHTML = '';
    noComplaintsMsg.classList.add('hidden');
    try {
        const token = localStorage.getItem('studentToken');
        const response = await fetch(`${API_BASE_URL}/student/complaints/list`, {
            headers: { 'Authorization': `Bearer ${token}` }
        });
        if (response.ok) {
            const complaints = await response.json();
            if (complaints.length === 0) {
                noComplaintsMsg.classList.remove('hidden');
            } else {
                complaints.forEach(c => {
                    const card = document.createElement('div');
                    card.className = 'bg-gray-50 border rounded-lg p-4 flex flex-col md:flex-row md:items-center justify-between shadow-sm';
                    card.innerHTML = `
                        <div>
                            <div class='font-semibold text-gray-800'>${c.issue_type}</div>
                            <div class='text-gray-600 text-sm mb-1'>${c.details}</div>
                            <div class='text-xs text-gray-400'>${c.course_code ? 'Course: ' + c.course_code : ''}</div>
                        </div>
                        <div class='mt-2 md:mt-0'>
                            <span class='px-3 py-1 rounded-full text-xs font-bold ${c.status === 'resolved' ? 'bg-green-200 text-green-800' : 'bg-yellow-100 text-yellow-700'}'>${c.status.replace('_', ' ').charAt(0).toUpperCase() + c.status.replace('_', ' ').slice(1)}</span>
                        </div>
                    `;
                    complaintList.appendChild(card);
                });
            }
        } else {
            const errorData = await response.json();
            noComplaintsMsg.textContent = `Failed to load complaints: ${errorData.message || response.statusText}`;
            noComplaintsMsg.classList.remove('hidden');
        }
    } catch (e) {
        noComplaintsMsg.textContent = 'Error loading complaints: ' + e.message;
        noComplaintsMsg.classList.remove('hidden');
    }
}

if (complaintForm) {
complaintForm.addEventListener("submit", async (e) => {
    e.preventDefault();
        if (complaintMessageBox) complaintMessageBox.classList.add("hidden");
        if (complaintSuccess) complaintSuccess.classList.add("hidden");

    const complaintData = {
            course_code: complaintCourse ? complaintCourse.value.trim() : null,
            issue_type: complaintIssueType ? complaintIssueType.value : '',
            details: complaintDetails ? complaintDetails.value.trim() : '',
        };

    if (!complaintData.issue_type) {
            if (complaintMessageText) complaintMessageText.textContent = "Please select an issue type.";
            if (complaintMessageBox) complaintMessageBox.classList.remove("hidden");
        return;
    }
    if (!complaintData.details) {
            if (complaintMessageText) complaintMessageText.textContent = "Please provide details for your complaint.";
            if (complaintMessageBox) complaintMessageBox.classList.remove("hidden");
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
                if (complaintSuccess) complaintSuccess.classList.remove("hidden");
                if (complaintForm) complaintForm.reset();
                loadComplaintList();
                // Auto-refresh complaints tab to show new complaint in list
                if (currentActiveTab === 'complaints') {
                    setTimeout(() => refreshCurrentTabAfterAction(), 1000); // Small delay to show success message
                }
        } else {
                if (complaintMessageText) complaintMessageText.textContent = data.message || "Failed to submit complaint.";
                if (complaintMessageBox) complaintMessageBox.classList.remove("hidden");
            console.error("Complaint submission error:", data);
        }
    } catch (error) {
            console.error("Network error complaint submission:", error);
        }
    });
}

// --- Request Faculty Logic ---
if (facultyRequestForm) {
    facultyRequestForm.addEventListener('submit', (e) => {
        e.preventDefault();
        submitFacultyRequest();
    });
}

if (goToDashboardAfterRequestSubmit) {
    goToDashboardAfterRequestSubmit.addEventListener('click', () => {
        showTab('requestFaculty');
    });
}

// Removed loadUpcomingCourses as requestCourseName is now a text input

async function submitFacultyRequest() {
    if (requestSubmissionSuccess) requestSubmissionSuccess.classList.add('hidden');

    const courseName = requestCourseName ? requestCourseName.value.trim() : '';
    const facultyName = requestedFacultyName ? requestedFacultyName.value.trim() : '';
    const details = requestDetails ? requestDetails.value.trim() : '';

    if (!courseName) {
        showCustomMessageBox('Validation Error', 'Please enter the upcoming course name.');
        return;
    }
    if (!details) {
        showCustomMessageBox('Validation Error', 'Please provide details for your request.');
        return;
    }

    try {
        const response = await authenticatedFetch(`${API_BASE_URL}/student/requests/faculty_request`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                course_name: courseName,
                requested_faculty_name: facultyName || null,
                details: details
            })
        });

        const data = await response.json();

        if (response.ok) {
            const requestFormContainer = document.getElementById('requestFormContainer');
            if (requestFormContainer) requestFormContainer.classList.add('hidden');
            if (requestSubmissionSuccess) requestSubmissionSuccess.classList.remove('hidden');
            if (facultyRequestForm) facultyRequestForm.reset();
            showCustomMessageBox('Success', 'Your faculty request has been submitted successfully!');
            // Auto-refresh request faculty tab to show success state
            if (currentActiveTab === 'requestFaculty') {
                setTimeout(() => refreshCurrentTabAfterAction(), 1000); // Small delay to show success message
            }
        } else {
            showCustomMessageBox('Submission Failed', data.message || 'Failed to submit request. Please try again.');
            console.error('Request submission error:', data);
        }
    } catch (error) {
        console.error('Network error during request submission:', error);
        showCustomMessageBox('Network Error', 'Network error or server unavailable. Please try again later.');
    }
}

// Function to test database field size limit
async function testDatabaseFieldSize() {
    const testUrl = 'https://placehold.co/50x50/cccccc/ffffff?text=TEST';
    console.log('Testing database field with URL length:', testUrl.length);
    
    try {
        const response = await authenticatedFetch(`${API_BASE_URL}/student/profile/update`, {
            method: "PUT",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ profile_picture: testUrl }),
        });
        
        if (response.ok) {
            console.log('Database field test successful');
            return true;
        } else {
            console.log('Database field test failed');
            return false;
        }
    } catch (error) {
        console.error('Database field test error:', error);
        return false;
    }
}
