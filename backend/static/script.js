
const applicationList = document.getElementById("application-list");
const addButton = document.getElementById("add-application");
const applicationCount = document.getElementById("application-count");

const STORAGE_KEY = "careerlens_applications";

const statuses = [
    "Applied",
    "Under Review",
    "Interview",
    "Offer",
    "Rejected"
];

let applications = loadApplications();

function loadApplications() {
    try {
        const saved = localStorage.getItem(STORAGE_KEY);
        const parsed = saved ? JSON.parse(saved) : [];
        return Array.isArray(parsed) ? parsed : [];
    } catch {
        return [];
    }
}

function saveApplications() {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(applications));
}

function renderApplications() {
    applicationList.innerHTML = "";
    applicationCount.textContent = applications.length;

    if (applications.length === 0) {
        applicationList.innerHTML = `
            <div class="empty-state">
                <div class="empty-icon">◷</div>
                <strong>Your job search starts here.</strong>
                <p>Add an application to begin tracking your progress.</p>
            </div>
        `;
        return;
    }

    applications.forEach((application) => {
        const row = document.createElement("div");
        row.className = "application-row";

        const details = document.createElement("div");

        const title = document.createElement("strong");
        title.textContent = application.title;

        const company = document.createElement("small");
        company.textContent = application.company;

        details.append(title, company);

        const date = document.createElement("span");
        date.textContent = application.date;

        const statusSelect = document.createElement("select");
        statusSelect.setAttribute(
            "aria-label",
            `Status for ${application.title} at ${application.company}`
        );

        statuses.forEach((status) => {
            const option = document.createElement("option");
            option.value = status;
            option.textContent = status;
            option.selected = status === application.status;
            statusSelect.appendChild(option);
        });

        statusSelect.addEventListener("change", () => {
            application.status = statusSelect.value;
            saveApplications();
        });

        row.append(details, date, statusSelect);
        applicationList.appendChild(row);
    });
}

function openApplicationForm() {
    if (document.getElementById("application-modal")) return;

    const overlay = document.createElement("div");
    overlay.id = "application-modal";
    overlay.className = "modal-overlay";

    overlay.innerHTML = `
        <form id="application-form" class="application-form">
            <div class="modal-heading">
                <div>
                    <p class="eyebrow">JOB SEARCH</p>
                    <h2>Add an application</h2>
                </div>
                <button type="button" id="close-modal"
                    class="close-modal" aria-label="Close form">×</button>
            </div>

            <label for="job-title">Job title</label>
            <input id="job-title" name="title"
                placeholder="e.g. Python Developer" required maxlength="100">

            <label for="company-name">Company</label>
            <input id="company-name" name="company"
                placeholder="e.g. ABC Technologies" required maxlength="100">

            <label for="application-date">Date applied</label>
            <input id="application-date" name="date"
                type="date" value="${new Date().toLocaleDateString("en-CA")}"
                required>

            <label for="application-status">Current status</label>
            <select id="application-status" name="status">
                ${statuses.map(status =>
                    `<option value="${status}">${status}</option>`
                ).join("")}
            </select>

            <button type="submit" class="primary-button submit-button">
                Save application
            </button>
        </form>
    `;

    document.body.appendChild(overlay);

    const form = document.getElementById("application-form");
    const titleInput = document.getElementById("job-title");

    document.getElementById("close-modal").addEventListener("click", () => {
        overlay.remove();
        addButton.focus();
    });

    overlay.addEventListener("click", (event) => {
        if (event.target === overlay) overlay.remove();
    });

    form.addEventListener("submit", (event) => {
        event.preventDefault();

        const formData = new FormData(form);
        const title = formData.get("title").trim();
        const company = formData.get("company").trim();
        const date = formData.get("date");
        const status = formData.get("status");

        if (!title || !company || !date || !statuses.includes(status)) {
            alert("Please complete all fields.");
            return;
        }

        applications.unshift({ title, company, date, status });

        try {
            saveApplications();
        } catch {
            applications.shift();
            alert("Could not save your application. Check browser storage.");
            return;
        }

        renderApplications();
        overlay.remove();

        document.getElementById("applications").scrollIntoView({
            behavior: "smooth"
        });
    });

    titleInput.focus();
}

addButton.addEventListener("click", openApplicationForm);

renderApplications();
