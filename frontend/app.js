const API_URL = "http://127.0.0.1:8000";


/* =================================
   HELPERS
================================= */

function escapeHtml(value) {

    if (
        value === null ||
        value === undefined
    ) {
        return "";
    }

    return String(value)
        .replaceAll("&", "&amp;")
        .replaceAll("<", "&lt;")
        .replaceAll(">", "&gt;")
        .replaceAll('"', "&quot;")
        .replaceAll("'", "&#039;");
}


function formatDate(value) {

    if (!value) {
        return "—";
    }

    return new Date(value).toLocaleString();
}


function showToast(message) {

    const toast =
        document.getElementById("toast");

    const toastMessage =
        document.getElementById("toastMessage");

    toastMessage.textContent = message;

    toast.classList.add("show");

    setTimeout(() => {
        toast.classList.remove("show");
    }, 3500);
}


/* =================================
   HEALTH
================================= */

async function checkHealth() {

    const status =
        document.getElementById("apiStatus");

    const orb =
        document.getElementById("apiOrb");

    const heroHealth =
        document.getElementById("heroHealth");

    const topStatus =
        document.getElementById("topStatus");

    try {

        const response =
            await fetch(`${API_URL}/health`);

        if (!response.ok) {
            throw new Error("API unavailable");
        }

        const data =
            await response.json();

        if (data.status === "healthy") {

            status.textContent = "HEALTHY";

            orb.style.background =
                "var(--green)";

            orb.style.boxShadow =
                "0 0 15px var(--green)";

            heroHealth.textContent =
                "OPERATIONAL";

            heroHealth.classList.add("green");

            topStatus.textContent =
                "SYSTEM ONLINE";

        } else {

            status.textContent =
                "UNHEALTHY";

            topStatus.textContent =
                "SYSTEM DEGRADED";
        }

    } catch (error) {

        status.textContent = "OFFLINE";

        orb.style.background =
            "var(--orange)";

        orb.style.boxShadow =
            "0 0 15px var(--orange)";

        heroHealth.textContent =
            "OFFLINE";

        heroHealth.classList.remove("green");

        topStatus.textContent =
            "SYSTEM OFFLINE";

        console.error(error);
    }
}


/* =================================
   LOAD JOBS
================================= */

async function loadJobs() {

    const container =
        document.getElementById(
            "jobsContainer"
        );

    try {

        const response =
            await fetch(`${API_URL}/jobs`);

        if (!response.ok) {
            throw new Error(
                "Failed to load jobs"
            );
        }

        const jobs =
            await response.json();

        if (!jobs.length) {

            container.innerHTML = `
                <div class="loading-state">
                    No jobs available yet.
                </div>
            `;

            return;
        }

        /*
         * Show the most recent records first.
         * Limit the visual dashboard to 10 jobs.
         */
        const visibleJobs =
            jobs.slice(-10).reverse();

        container.innerHTML =
            visibleJobs.map(job => `

                <article class="job-card">

                    <div class="job-card-header">

                        <h3>
                            ${escapeHtml(job.title)}
                        </h3>

                        <span class="source-pill">
                            ${escapeHtml(
                                job.source || "UNKNOWN"
                            ).toUpperCase()}
                        </span>

                    </div>

                    <div class="job-company">
                        ${escapeHtml(
                            job.company ||
                            "Unknown company"
                        )}
                    </div>

                    <div class="job-details">

                        <span class="job-detail">
                            ${escapeHtml(
                                job.location ||
                                "Location not specified"
                            )}
                        </span>

                        <span class="job-detail">
                            ${escapeHtml(
                                job.job_type ||
                                "Type not specified"
                            )}
                        </span>

                    </div>

                    <a
                        class="job-link"
                        href="${escapeHtml(job.url)}"
                        target="_blank"
                        rel="noopener noreferrer"
                    >
                        VIEW LISTING
                        <span>↗</span>
                    </a>

                </article>

            `).join("");

    } catch (error) {

        container.innerHTML = `
            <div class="loading-state">
                Unable to load live job data.
            </div>
        `;

        console.error(error);
    }
}


/* =================================
   LOAD INGESTION LOGS
================================= */

async function loadLogs() {

    const container =
        document.getElementById(
            "logsContainer"
        );

    try {

        const response =
            await fetch(
                `${API_URL}/ingestion-logs`
            );

        if (!response.ok) {
            throw new Error(
                "Failed to load logs"
            );
        }

        const logs =
            await response.json();

        if (!logs.length) {

            container.innerHTML = `
                <div class="loading-state">
                    No ingestion history yet.
                </div>
            `;

            return;
        }

        container.innerHTML = `

            <table class="logs-table">

                <thead>

                    <tr>

                        <th>SOURCE</th>
                        <th>FALLBACK</th>
                        <th>FETCHED</th>
                        <th>INSERTED</th>
                        <th>SKIPPED</th>
                        <th>STATUS</th>
                        <th>TIME</th>

                    </tr>

                </thead>

                <tbody>

                    ${logs.map(log => {

                        const fallback =
                            log.fallback_used === "True" ||
                            log.fallback_used === true;

                        return `

                            <tr>

                                <td>
                                    ${escapeHtml(
                                        log.source
                                    )}
                                </td>

                                <td>
                                    ${
                                        fallback
                                            ? "YES"
                                            : "NO"
                                    }
                                </td>

                                <td>
                                    ${log.jobs_fetched ?? 0}
                                </td>

                                <td>
                                    ${log.jobs_inserted ?? 0}
                                </td>

                                <td>
                                    ${log.jobs_skipped ?? 0}
                                </td>

                                <td class="log-success">
                                    ${escapeHtml(
                                        log.status
                                    ).toUpperCase()}
                                </td>

                                <td>
                                    ${formatDate(
                                        log.created_at
                                    )}
                                </td>

                            </tr>

                        `;
                    }).join("")}

                </tbody>

            </table>
        `;

    } catch (error) {

        container.innerHTML = `
            <div class="loading-state">
                Unable to load ingestion history.
            </div>
        `;

        console.error(error);
    }
}


/* =================================
   LATEST STATISTICS
================================= */

async function loadLatestStats() {

    try {

        const response =
            await fetch(
                `${API_URL}/ingestion-logs`
            );

        if (!response.ok) {
            throw new Error(
                "Failed to load statistics"
            );
        }

        const logs =
            await response.json();

        if (!logs.length) {
            return;
        }

        const latest = logs[0];

        const fallback =
            latest.fallback_used === "True" ||
            latest.fallback_used === true;

        document.getElementById(
            "primarySource"
        ).textContent =
            latest.source || "—";

        document.getElementById(
            "heroPrimary"
        ).textContent =
            (
                latest.source || "—"
            ).toUpperCase();

        document.getElementById(
            "fallbackStatus"
        ).textContent =
            fallback
                ? "ACTIVE"
                : "STANDBY";

        document.getElementById(
            "lastRun"
        ).textContent =
            formatDate(
                latest.created_at
            );

        document.getElementById(
            "jobsFetched"
        ).textContent =
            latest.jobs_fetched ?? 0;

        document.getElementById(
            "jobsInserted"
        ).textContent =
            latest.jobs_inserted ?? 0;

        document.getElementById(
            "jobsSkipped"
        ).textContent =
            latest.jobs_skipped ?? 0;

        document.getElementById(
            "jobsTotal"
        ).textContent =
            latest.jobs_fetched ?? 0;

    } catch (error) {

        console.error(error);
    }
}


/* =================================
   NORMAL INGESTION
================================= */

async function runIngestion() {

    const button =
        document.getElementById(
            "ingestBtn"
        );

    button.disabled = true;

    button.innerHTML =
        `<span class="button-icon">↻</span> INGESTING...`;

    try {

        const response =
            await fetch(
                `${API_URL}/ingest`,
                {
                    method: "POST"
                }
            );

        if (!response.ok) {
            throw new Error(
                "Ingestion failed"
            );
        }

        const result =
            await response.json();

        showToast(
            `Ingestion complete — ${result.total} jobs processed`
        );

        await refreshDashboard();

    } catch (error) {

        showToast(
            "Ingestion failed — check the API"
        );

        console.error(error);

    } finally {

        button.disabled = false;

        button.innerHTML =
            `<span class="button-icon">↯</span> Ingest Jobs`;
    }
}


/* =================================
   FALLBACK TEST
================================= */

async function testFallback() {

    const button =
        document.getElementById(
            "fallbackBtn"
        );

    const confirmed =
        confirm(
            "Run the controlled fallback test?\n\n" +
            "JobFlow will simulate a primary-source " +
            "failure and switch to Remotive."
        );

    if (!confirmed) {
        return;
    }

    button.disabled = true;

    button.innerHTML =
        `<span>↻</span> TESTING...`;

    try {

        const response =
            await fetch(
                `${API_URL}/test-fallback`,
                {
                    method: "POST"
                }
            );

        if (!response.ok) {
            throw new Error(
                "Fallback test failed"
            );
        }

        const result =
            await response.json();

        if (result.fallback_used) {

            showToast(
                "Fallback successful — Remotive recovered the pipeline"
            );

        } else {

            showToast(
                "Fallback test completed"
            );
        }

        await refreshDashboard();

    } catch (error) {

        showToast(
            "Fallback test failed — check the API"
        );

        console.error(error);

    } finally {

        button.disabled = false;

        button.innerHTML =
            `<span>◇</span> Test Fallback`;
    }
}


/* =================================
   REFRESH DASHBOARD
================================= */

async function refreshDashboard() {

    await checkHealth();

    await Promise.all([
        loadJobs(),
        loadLogs(),
        loadLatestStats()
    ]);
}


/* =================================
   INITIALIZATION
================================= */

async function initializeDashboard() {

    await refreshDashboard();

    /*
     * Lightweight status refresh.
     * This keeps the command center feeling
     * live without repeatedly ingesting data.
     */
    setInterval(
        checkHealth,
        30000
    );
}


initializeDashboard();