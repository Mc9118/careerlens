
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

// ---------------- APPLICATION TRACKER ----------------

function loadApplications() {
    try {
        const saved = localStorage.getItem(STORAGE_KEY);
        const parsed = saved ? JSON.parse(saved) : [];
        return Array.isArray(parsed) ? parsed : [];
    } catch {
        return [];
    }
}

let applications = loadApplications();

function saveApplications() {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(applications));
}

function renderApplications() {
    if (!applicationList || !applicationCount) return;

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
        addButton?.focus();
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

        document.getElementById("applications")?.scrollIntoView({
            behavior: "smooth"
        });
    });

    titleInput.focus();
}

addButton?.addEventListener("click", openApplicationForm);
renderApplications();

// ---------------- ATS RESUME ANALYZER ----------------

const atsForm = document.getElementById("ats-form");

if (atsForm) {
    atsForm.addEventListener("submit", async (event) => {
        event.preventDefault();

        const message = document.getElementById("ats-message");
        const results = document.getElementById("ats-results");
        const button = document.getElementById("analyze-button");

        message.textContent = "Analyzing your resume...";
        results.hidden = true;
        button.disabled = true;

        try {
            const formData = new FormData(atsForm);

            const response = await fetch("/api/analyze-resume", {
                method: "POST",
                body: formData
            });

            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.error || "Analysis failed.");
            }

            document.getElementById("ats-score").textContent = data.score;

           function fillList(elementId, items) {
    const list = document.getElementById(elementId);

    if (!list) {
        console.error(`CareerLens: HTML element not found: ${elementId}`);
        return;
    }

    list.replaceChildren();

    if (!Array.isArray(items) || items.length === 0) {
        const item = document.createElement("li");
        item.textContent = "None found";
        list.appendChild(item);
        return;
    }

    items.forEach((text) => {
        const item = document.createElement("li");
        item.textContent = text;
        list.appendChild(item);
    });
}

            fillList("matched-keywords", data.matched_keywords);
            fillList("missing-keywords", data.missing_keywords);
            fillList("ats-suggestions", data.suggestions);

            // Update Skill Gap Analysis using the same ATS results.
const skillGapEmpty = document.getElementById("skill-gap-empty");
const skillGapResults = document.getElementById("skill-gap-results");
const skillCount = document.getElementById("skill-count");

fillList("skill-gap-matched", data.matched_keywords);
fillList("skill-gap-missing", data.missing_keywords);

// Show the missing keywords as learning priorities.
const recommendations = data.missing_keywords.map(
    skill => `Learn and practice ${skill}.`
);

fillList("skill-gap-recommendations", recommendations);

if (skillGapEmpty) {
    skillGapEmpty.hidden = true;
}

if (skillGapResults) {
    skillGapResults.hidden = false;
}

if (skillCount) {
    skillCount.textContent = data.missing_keywords.length;
}

            document.getElementById("ats-note").textContent = data.note;
            results.hidden = false;
            message.textContent = "Analysis complete!";

            // Update the dashboard's ATS score card.
            const atsStat = document.getElementById("ats-stat");
            if (atsStat) {
                atsStat.innerHTML = `${data.score}<small> / 100</small>`;
            }
        } catch (error) {
            message.textContent =
                error.message || "Something went wrong. Please try again.";
        } finally {
            button.disabled = false;
        }
    });
}

console.log("CareerLens JavaScript loaded");
console.log("ATS form found:", Boolean(atsForm));
