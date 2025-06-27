const API_BASE_URL = "http://127.0.0.1:5000/api";

// DOM Elements
const headerStudentName = document.getElementById("headerStudentName");
const logoutButton = document.getElementById("logoutButton");
const welcomeMessage = document.getElementById("welcomeMessage");
const studentBatchDepartment = document.getElementById(
  "studentBatchDepartment"
);
const profileImage = document.getElementById("profileImage");

// Tab Buttons
const tabPendingEvaluations = document.getElementById("tabPendingEvaluations");
const tabMyProfile = document.getElementById("tabMyProfile");
const tabCompletedEvaluations = document.getElementById(
  "tabCompletedEvaluations"
);
const tabComplaints = document.getElementById("tabComplaints");

// Sidebar Links
const pendingEvaluationsLink = document.getElementById(
  "pendingEvaluationsLink"
);
const myProfileLink = document.getElementById("myProfileLink");
const completedEvaluationsLink = document.getElementById(
  "completedEvaluationsLink"
);
const complaintsLink = document.getElementById("complaintsLink");

// Content Containers
const pendingEvaluationsContent = document.getElementById(
  "pendingEvaluationsContent"
);
const myProfileContent = document.getElementById("myProfileContent");
const completedEvaluationsContent = document.getElementById(
  "completedEvaluationsContent"
);
const complaintsContent = document.getElementById("complaintsContent");

// Pending Evaluations
const loadingPending = document.getElementById("loadingPending");
const noPendingEvaluations = document.getElementById("noPendingEvaluations");
const pendingEvaluationsList = document.getElementById(
  "pendingEvaluationsList"
);

// My Profile
const profileLoading = document.getElementById("profileLoading");
const profileError = document.getElementById("profileError");
const profileDetails = document.getElementById("profileDetails");
const saveProfileButton = document.getElementById("saveProfileButton");

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
const editableProfileFields = {
  name: {
    span: document.getElementById("profileName"),
    input: document.getElementById("editName"),
  },
  contact_no: {
    span: document.getElementById("profileContactNo"),
    input: document.getElementById("editContactNo"),
  },
  behavioral_records: {
    span: document.getElementById("profileBehavioralRecords"),
    input: document.getElementById("editBehavioralRecords"),
  },
  profile_picture: {
    span: document.getElementById("profilePictureUrl"),
    input: document.getElementById("editProfilePictureUrl"),
  },
};

// Completed Evaluations
const loadingCompleted = document.getElementById("loadingCompleted");
const noCompletedEvaluations = document.getElementById(
  "noCompletedEvaluations"
);
const completedEvaluationsList = document.getElementById(
  "completedEvaluationsList"
);

// Complaints
const complaintForm = document.getElementById("complaintForm");
const complaintCourse = document.getElementById("complaintCourse");
const complaintIssueType = document.getElementById("complaintIssueType");
const complaintDetails = document.getElementById("complaintDetails");
const complaintMessageBox = document.getElementById("complaintMessageBox");
const complaintMessageText = document.getElementById("complaintMessageText");
const complaintSuccess = document.getElementById("complaintSuccess");

let currentStudentData = null; // To store full student profile data

// --- Initialization ---
document.addEventListener("DOMContentLoaded", () => {
  const studentToken = localStorage.getItem("studentToken");
  const studentId = localStorage.getItem("studentId");
  const studentName = localStorage.getItem("studentName");

  if (!studentToken || !studentId || !studentName) {
    window.location.href = "student_login.html";
    return;
  }

  headerStudentName.textContent = `Welcome, ${studentName}`;
  welcomeMessage.textContent = `Welcome, ${studentName} 👋`;

  // Initial content load (default to pending evaluations)
  showTab("pendingEvaluations");
});

// --- Tab Switching Logic ---
function showTab(tabName) {
  // Hide all content sections
  pendingEvaluationsContent.classList.add("hidden");
  myProfileContent.classList.add("hidden");
  completedEvaluationsContent.classList.add("hidden");
  complaintsContent.classList.add("hidden");

  // Deactivate all tab buttons
  tabPendingEvaluations.classList.remove("active");
  tabMyProfile.classList.remove("active");
  tabCompletedEvaluations.classList.remove("active");
  tabComplaints.classList.remove("active");

  // Activate selected tab and show content
  switch (tabName) {
    case "pendingEvaluations":
      pendingEvaluationsContent.classList.remove("hidden");
      tabPendingEvaluations.classList.add("active");
      loadPendingEvaluations();
      break;
    case "myProfile":
      myProfileContent.classList.remove("hidden");
      tabMyProfile.classList.add("active");
      loadMyProfile();
      break;
    case "completedEvaluations":
      completedEvaluationsContent.classList.remove("hidden");
      tabCompletedEvaluations.classList.add("active");
      loadCompletedEvaluations();
      break;
    case "complaints":
      complaintsContent.classList.remove("hidden");
      tabComplaints.classList.add("active");
      break;
  }
}

// --- Event Listeners for Tabs and Sidebar ---
tabPendingEvaluations.addEventListener("click", () =>
  showTab("pendingEvaluations")
);
tabMyProfile.addEventListener("click", () => showTab("myProfile"));
tabCompletedEvaluations.addEventListener("click", () =>
  showTab("completedEvaluations")
);
tabComplaints.addEventListener("click", () => showTab("complaints"));

pendingEvaluationsLink.addEventListener("click", (e) => {
  e.preventDefault();
  showTab("pendingEvaluations");
});
myProfileLink.addEventListener("click", (e) => {
  e.preventDefault();
  showTab("myProfile");
});
completedEvaluationsLink.addEventListener("click", (e) => {
  e.preventDefault();
  showTab("completedEvaluations");
});
complaintsLink.addEventListener("click", (e) => {
  e.preventDefault();
  showTab("complaints");
});

// --- Logout Functionality ---
logoutButton.addEventListener("click", async () => {
  const studentToken = localStorage.getItem("studentToken");
  try {
    const response = await fetch(`${API_BASE_URL}/student/logout`, {
      method: "POST",
      headers: {
        Authorization: `Bearer ${studentToken}`,
      },
    });
    if (response.ok) {
      localStorage.clear();
      window.location.href = "student_login.html";
    } else {
      alert("Logout failed. Please try again.");
      console.error("Logout error:", await response.json());
    }
  } catch (error) {
    // Catching network errors and other exceptions
    console.error("Network error during logout:", error);
    alert("Network error during logout. Please check your connection.");
  }
});

// --- Helper function for authenticated API fetches ---
async function authenticatedFetch(url, options = {}) {
  const studentToken = localStorage.getItem("studentToken");
  if (!studentToken) {
    // If no token, redirect to login, as the user is not authenticated
    alert("Session expired or not logged in. Please log in again.");
    localStorage.clear(); // Clear any stale data
    window.location.href = "student_login.html";
    throw new Error("No authentication token found.");
  }

  // Ensure headers exist and add Authorization header
  options.headers = {
    ...options.headers,
    Authorization: `Bearer ${studentToken}`,
  };

  const response = await fetch(url, options);

  // Handle 401 Unauthorized specifically
  if (response.status === 401) {
    alert("Session expired or unauthorized. Please log in again.");
    localStorage.clear(); // Clear local storage to ensure fresh login
    window.location.href = "student_login.html";
    throw new Error("Unauthorized access, redirecting to login.");
  }

  return response;
}

// --- Pending Evaluations Logic (from previous dashboard) ---
async function loadPendingEvaluations() {
  loadingPending.classList.remove("hidden");
  noPendingEvaluations.classList.add("hidden");
  pendingEvaluationsList.innerHTML = "";

  try {
    // Use the authenticatedFetch helper
    const response = await authenticatedFetch(
      `${API_BASE_URL}/student/evaluations/assigned`,
      {
        method: "GET", // Headers already handled by helper
      }
    );

    if (response.ok) {
      const evaluations = await response.json();
      loadingPending.classList.add("hidden");

      if (evaluations.length === 0) {
        noPendingEvaluations.classList.remove("hidden");
      } else {
        evaluations.forEach((evaluation) => {
          const evalCard = document.createElement("div");
          evalCard.className = "card evaluation-item flex flex-col p-4";
          evalCard.innerHTML = `
                                <div class="flex-grow">
                                    <h3 class="text-xl font-semibold text-gray-900">${
                                      evaluation.title
                                    }</h3>
                                    <p class="text-sm text-gray-600">
                                        ${
                                          evaluation.course_code
                                            ? `Course: ${evaluation.course_code}`
                                            : ""
                                        }
                                        ${
                                          evaluation.batch
                                            ? `Batch: ${evaluation.batch}`
                                            : ""
                                        }
                                        ${
                                          evaluation.session
                                            ? `Session: ${evaluation.session}`
                                            : ""
                                        }
                                    </p>
                                    <p class="text-xs text-gray-500 mt-1">Due: ${
                                      evaluation.last_date || "N/A"
                                    }</p>
                                </div>
                                <div class="mt-4 self-end">
                                    <button class="take-evaluation-button bg-blue-500 hover:bg-blue-600 text-white font-bold py-2 px-4 rounded-md shadow transition duration-300 ease-in-out" 
                                            data-evaluation-id="${
                                              evaluation.id
                                            }"
                                            data-course-code="${
                                              evaluation.course_code || ""
                                            }">
                                        Take Evaluation
                                    </button>
                                </div>
                            `;
          pendingEvaluationsList.appendChild(evalCard);
        });

        document
          .querySelectorAll(".take-evaluation-button")
          .forEach((button) => {
            button.addEventListener("click", (event) => {
              const evalId = event.target.dataset.evaluationId;
              const courseCode = event.target.dataset.courseCode;
              window.location.href = `take_evaluation.html?evalId=${evalId}&courseCode=${courseCode}`;
            });
          });
      }
    } else {
      loadingPending.classList.add("hidden");
      const errorData = await response.json();
      noPendingEvaluations.textContent = `Failed to load evaluations: ${
        errorData.message || response.statusText
      }`;
      noPendingEvaluations.classList.remove("hidden");
      console.error("Failed to load evaluations:", errorData);
    }
  } catch (error) {
    loadingPending.classList.add("hidden");
    // Only display general network error if not handled by authenticatedFetch (e.g., no token initially)
    if (
      error.message !== "Unauthorized access, redirecting to login." &&
      error.message !== "No authentication token found."
    ) {
      noPendingEvaluations.textContent =
        "Network error. Please check your API server.";
      noPendingEvaluations.classList.remove("hidden");
      console.error("Network error loading evaluations:", error);
    }
  }
}

// --- My Profile Logic ---
async function loadMyProfile() {
  profileLoading.classList.remove("hidden");
  profileError.classList.add("hidden");
  profileDetails.classList.add("hidden");
  saveProfileButton.classList.add("hidden");

  const studentId = localStorage.getItem("studentId"); // Ensure studentId is available

  try {
    // Use the authenticatedFetch helper
    const response = await authenticatedFetch(
      `${API_BASE_URL}/student/profile`,
      {
        method: "GET", // Headers already handled by helper
      }
    );

    if (response.ok) {
      currentStudentData = await response.json(); // Store full profile
      profileLoading.classList.add("hidden");
      profileDetails.classList.remove("hidden");

      // Populate static fields
      profileFields.student_id.textContent = currentStudentData.student_id;
      profileFields.email.textContent = currentStudentData.email;
      profileFields.dob.textContent = currentStudentData.dob || "N/A";
      profileFields.gender.textContent = currentStudentData.gender || "N/A";
      profileFields.session.textContent = currentStudentData.session || "N/A";
      profileFields.batch.textContent = currentStudentData.batch || "N/A";
      profileFields.department.textContent =
        currentStudentData.department || "N/A";
      profileFields.enrollment_date.textContent =
        currentStudentData.enrollment_date || "N/A";
      profileFields.cgpa.textContent = currentStudentData.cgpa || "N/A";

      // Set header info based on loaded profile
      studentBatchDepartment.textContent = `Batch: ${
        currentStudentData.batch || "N/A"
      }, Dept: ${currentStudentData.department || "N/A"}`;
      if (currentStudentData.profile_picture) {
        profileImage.src = currentStudentData.profile_picture;
      } else {
        profileImage.src =
          "https://placehold.co/80x80/cccccc/ffffff?text=Profile";
      }

      // Populate editable fields and attach edit listeners
      for (const fieldName in editableProfileFields) {
        const { span, input } = editableProfileFields[fieldName];
        span.textContent = currentStudentData[fieldName] || "N/A";
        input.value = currentStudentData[fieldName] || "";

        // Attach event listener for editing
        span.onclick = () => enableEdit(fieldName);
        input.onblur = () => disableEdit(fieldName); // Save on blur
        input.onkeydown = (e) => {
          if (e.key === "Enter") {
            disableEdit(fieldName);
          }
        };
      }
    } else {
      profileLoading.classList.add("hidden");
      const errorData = await response.json();
      profileError.textContent = `Failed to load profile: ${
        errorData.message || response.statusText
      }`;
      profileError.classList.remove("hidden");
      console.error("Failed to load profile:", errorData);
    }
  } catch (error) {
    profileLoading.classList.add("hidden");
    if (
      error.message !== "Unauthorized access, redirecting to login." &&
      error.message !== "No authentication token found."
    ) {
      profileError.textContent = "Network error. Please check your API server.";
      profileError.classList.remove("hidden");
      console.error("Network error loading profile:", error);
    }
  }
}

function enableEdit(fieldName) {
  const { span, input } = editableProfileFields[fieldName];
  span.classList.add("hidden");
  input.classList.remove("hidden");
  input.focus();
  saveProfileButton.classList.remove("hidden");
}

async function disableEdit(fieldName) {
  const { span, input } = editableProfileFields[fieldName];
  const newValue = input.value.trim();

  // Hide input, show span immediately for responsiveness
  input.classList.add("hidden");
  span.classList.remove("hidden");
  span.textContent = newValue || "N/A"; // Optimistic update

  // If value changed, send update to API
  if (newValue !== (currentStudentData[fieldName] || "")) {
    const studentId = localStorage.getItem("studentId"); // Ensure studentId is available
    try {
      // Use the authenticatedFetch helper
      const response = await authenticatedFetch(
        `${API_BASE_URL}/student/profile/update`,
        {
          method: "PUT",
          headers: {
            "Content-Type": "application/json", // Add content type for PUT requests
          },
          body: JSON.stringify({ [fieldName]: newValue }),
        }
      );

      const data = await response.json();
      if (response.ok) {
        currentStudentData[fieldName] = newValue; // Update local data
        alert("Profile updated successfully!");
        // Special handling for profile_picture to update img src
        if (fieldName === "profile_picture" && newValue) {
          profileImage.src = newValue;
        }
      } else {
        alert(
          "Failed to update profile: " + (data.message || response.statusText)
        );
        // Revert optimistic update if API fails
        span.textContent = currentStudentData[fieldName] || "N/A";
        console.error("Profile update error:", data);
      }
    } catch (error) {
      alert("Network error during profile update.");
      span.textContent = currentStudentData[fieldName] || "N/A";
      console.error("Network error profile update:", error);
    }
  }
  // Check if any other editable fields are open. If not, hide save button.
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
  // This button primarily serves as a visual cue or to manually trigger blur for all.
  // The saveProfileButton will be hidden automatically by disableEdit if no fields are in edit mode.
});

// --- Completed Evaluations Logic ---
async function loadCompletedEvaluations() {
  loadingCompleted.classList.remove("hidden");
  noCompletedEvaluations.classList.add("hidden");
  completedEvaluationsList.innerHTML = "";

  try {
    // Use the authenticatedFetch helper
    const response = await authenticatedFetch(
      `${API_BASE_URL}/student/evaluations/completed`,
      {
        method: "GET", // Headers already handled by helper
      }
    );

    if (response.ok) {
      const completedEvaluations = await response.json();
      loadingCompleted.classList.add("hidden");

      if (completedEvaluations.length === 0) {
        noCompletedEvaluations.classList.remove("hidden");
      } else {
        completedEvaluations.forEach((evaluation) => {
          const evalCard = document.createElement("div");
          evalCard.className = "card evaluation-item flex flex-col p-4";
          evalCard.innerHTML = `
                                <div class="flex-grow">
                                    <h3 class="text-xl font-semibold text-gray-900">${evaluation.title}</h3>
                                    <p class="text-sm text-gray-600">
                                        Course: ${evaluation.course_name} (${evaluation.course_code})
                                    </p>
                                    <p class="text-xs text-gray-500 mt-1">Completed On: ${evaluation.completion_date}</p>
                                </div>
                            `;
          completedEvaluationsList.appendChild(evalCard);
        });
      }
    } else {
      loadingCompleted.classList.add("hidden");
      const errorData = await response.json();
      noCompletedEvaluations.textContent = `Failed to load completed evaluations: ${
        errorData.message || response.statusText
      }`;
      noCompletedEvaluations.classList.remove("hidden");
      console.error("Failed to load completed evaluations:", errorData);
    }
  } catch (error) {
    loadingCompleted.classList.add("hidden");
    if (
      error.message !== "Unauthorized access, redirecting to login." &&
      error.message !== "No authentication token found."
    ) {
      noCompletedEvaluations.textContent =
        "Network error. Please check your API server.";
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
    course_code: complaintCourse.value.trim() || null,
    issue_type: complaintIssueType.value,
    details: complaintDetails.value.trim(),
  };

  if (!complaintData.issue_type) {
    complaintMessageText.textContent = "Please select an issue type.";
    complaintMessageBox.classList.remove("hidden");
    return;
  }
  if (!complaintData.details) {
    complaintMessageText.textContent =
      "Please provide details for your complaint.";
    complaintMessageBox.classList.remove("hidden");
    return;
  }

  try {
    // Use the authenticatedFetch helper
    const response = await authenticatedFetch(
      `${API_BASE_URL}/student/complaints/submit`,
      {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(complaintData),
      }
    );

    const data = await response.json();
    if (response.ok) {
      complaintSuccess.classList.remove("hidden");
      complaintForm.reset(); // Clear the form
    } else {
      complaintMessageText.textContent =
        data.message || "Failed to submit complaint.";
      complaintMessageBox.classList.remove("hidden");
      console.error("Complaint submission error:", data);
    }
  } catch (error) {
    if (
      error.message !== "Unauthorized access, redirecting to login." &&
      error.message !== "No authentication token found."
    ) {
      complaintMessageText.textContent =
        "Network error. Please check your API server.";
      complaintMessageBox.classList.remove("hidden");
      console.error("Network error complaint submission:", error);
    }
  }
});
