/* ================================================================
   AI README Generator — Frontend Logic
   ================================================================ */

(function () {
    "use strict";

    // ---- DOM refs (Generate tab) ----
    const form = document.getElementById("generateForm");
    const repoInput = document.getElementById("repoUrl");
    const submitBtn = document.getElementById("submitBtn");
    const customInstr = document.getElementById("customInstructions");
    const githubTokenIn = document.getElementById("githubToken");

    const inputCard = document.getElementById("inputCard");
    const loadingCard = document.getElementById("loadingCard");
    const resultCard = document.getElementById("resultCard");
    const errorCard = document.getElementById("errorCard");

    const loadingTitle = document.getElementById("loadingTitle");
    const loadingStatus = document.getElementById("loadingStatus");
    const loadingSteps = document.getElementById("loadingSteps");
    const step1 = document.getElementById("step1");
    const step2 = document.getElementById("step2");
    const step3 = document.getElementById("step3");

    const resultRepoName = document.getElementById("resultRepoName");
    const resultTime = document.getElementById("resultTime");
    const resultPreview = document.getElementById("resultPreview");
    const resultRawCode = document.getElementById("resultRawCode");

    const copyBtn = document.getElementById("copyBtn");
    const downloadBtn = document.getElementById("downloadBtn");
    const newBtn = document.getElementById("newBtn");
    const retryBtn = document.getElementById("retryBtn");

    const togglePreview = document.getElementById("togglePreview");
    const toggleRaw = document.getElementById("toggleRaw");
    const previewPane = document.getElementById("resultPreview");
    const rawPane = document.getElementById("resultRaw");

    const errorMessage = document.getElementById("errorMessage");

    // ---- DOM refs (Analyze tab) ----
    const analyzeForm = document.getElementById("analyzeForm");
    const analyzeRepoInput = document.getElementById("analyzeRepoUrl");
    const analyzeSubmitBtn = document.getElementById("analyzeSubmitBtn");
    const analyzeTokenIn = document.getElementById("analyzeGithubToken");
    const analyzeInputCard = document.getElementById("analyzeInputCard");
    const analyzeResultCard = document.getElementById("analyzeResultCard");
    const analyzeRepoName = document.getElementById("analyzeRepoName");
    const analyzeNewBtn = document.getElementById("analyzeNewBtn");
    const scoreArc = document.getElementById("scoreArc");
    const scoreValue = document.getElementById("scoreValue");
    const scoreSummary = document.getElementById("scoreSummary");
    const strengthsList = document.getElementById("strengthsList");
    const improvementsList = document.getElementById("improvementsList");
    const missingTags = document.getElementById("missingTags");

    // ---- DOM refs (Tabs) ----
    const tabGenerate = document.getElementById("tabGenerate");
    const tabAnalyze = document.getElementById("tabAnalyze");
    const tabContentGen = document.getElementById("tabContentGenerate");
    const tabContentAna = document.getElementById("tabContentAnalyze");

    // ---- DOM refs (Advanced toggle) ----
    const toggleAdvanced = document.getElementById("toggleAdvanced");
    const advancedPanel = document.getElementById("advancedPanel");
    const toggleIcon = document.getElementById("toggleIcon");

    // ---- State ----
    let currentMarkdown = "";
    let currentRepoName = "";
    let currentMode = "generate"; // "generate" or "analyze"

    // ---- Helpers ----
    function hideAll() {
        [inputCard, loadingCard, resultCard, errorCard, analyzeInputCard, analyzeResultCard].forEach(c => {
            if (c) c.classList.add("hidden");
        });
    }

    function showCard(card) {
        hideAll();
        card.classList.remove("hidden");
    }

    function showToast(message) {
        let toast = document.querySelector(".toast");
        if (!toast) {
            toast = document.createElement("div");
            toast.className = "toast";
            document.body.appendChild(toast);
        }
        toast.textContent = message;
        toast.classList.add("show");
        setTimeout(() => toast.classList.remove("show"), 2500);
    }

    function animateSteps(mode) {
        loadingSteps.classList.remove("hidden");

        if (mode === "analyze") {
            loadingTitle.textContent = "Analyzing README…";
            step1.innerHTML = '<span class="loader__step-icon">📡</span> Fetching repo data';
            step2.innerHTML = '<span class="loader__step-icon">🔍</span> AI is analyzing';
            step3.innerHTML = '<span class="loader__step-icon">📊</span> Scoring';
        } else {
            loadingTitle.textContent = "Generating your README…";
            step1.innerHTML = '<span class="loader__step-icon">📡</span> Fetching repo data';
            step2.innerHTML = '<span class="loader__step-icon">🤖</span> AI is writing';
            step3.innerHTML = '<span class="loader__step-icon">✨</span> Polishing output';
        }

        step1.classList.add("active");
        step2.classList.remove("active", "done");
        step3.classList.remove("active", "done");
        loadingStatus.textContent = "Fetching repository data from GitHub…";

        setTimeout(() => {
            step1.classList.remove("active");
            step1.classList.add("done");
            step2.classList.add("active");
            loadingStatus.textContent = mode === "analyze"
                ? "AI is analyzing the README…"
                : "AI is generating your README…";
        }, 2000);

        setTimeout(() => {
            step2.classList.remove("active");
            step2.classList.add("done");
            step3.classList.add("active");
            loadingStatus.textContent = mode === "analyze"
                ? "Calculating score…"
                : "Polishing the output…";
        }, 6000);
    }

    // ---- Markdown rendering ----
    function renderMarkdown(md) {
        if (typeof marked !== "undefined") {
            marked.setOptions({ breaks: true, gfm: true });
            return marked.parse(md);
        }
        return `<pre>${md}</pre>`;
    }

    // ---- Tab switching ----
    function switchTab(tab) {
        currentMode = tab;
        hideAll();

        if (tab === "generate") {
            tabGenerate.classList.add("active");
            tabAnalyze.classList.remove("active");
            tabContentGen.classList.remove("hidden");
            tabContentAna.classList.add("hidden");
            inputCard.classList.remove("hidden");
        } else {
            tabAnalyze.classList.add("active");
            tabGenerate.classList.remove("active");
            tabContentAna.classList.remove("hidden");
            tabContentGen.classList.add("hidden");
            analyzeInputCard.classList.remove("hidden");
        }
    }

    tabGenerate.addEventListener("click", () => switchTab("generate"));
    tabAnalyze.addEventListener("click", () => switchTab("analyze"));

    // ---- Advanced toggle ----
    toggleAdvanced.addEventListener("click", () => {
        advancedPanel.classList.toggle("hidden");
        toggleIcon.classList.toggle("open");
    });

    // ---- Generate form submit ----
    form.addEventListener("submit", async (e) => {
        e.preventDefault();
        const repoUrl = repoInput.value.trim();
        if (!repoUrl) return;

        const style = document.querySelector('input[name="style"]:checked').value;
        const customInstructions = customInstr.value.trim();
        const githubToken = githubTokenIn.value.trim() || null;

        showCard(loadingCard);
        submitBtn.disabled = true;
        animateSteps("generate");

        try {
            const body = { repo_url: repoUrl, style: style };
            if (customInstructions) body.custom_instructions = customInstructions;
            if (githubToken) body.github_token = githubToken;

            const response = await fetch("/api/generate", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(body),
            });

            if (!response.ok) {
                const err = await response.json().catch(() => ({ detail: "Unknown error" }));
                throw new Error(err.detail || `HTTP ${response.status}`);
            }

            const data = await response.json();
            currentMarkdown = data.readme_content;
            currentRepoName = data.repo_name;

            resultRepoName.textContent = data.repo_name;
            resultTime.textContent = `⏱ < 15 sec`;
            resultPreview.innerHTML = renderMarkdown(currentMarkdown);
            resultRawCode.textContent = currentMarkdown;

            togglePreview.classList.add("active");
            toggleRaw.classList.remove("active");
            previewPane.classList.remove("hidden");
            rawPane.classList.add("hidden");

            showCard(resultCard);

        } catch (err) {
            errorMessage.textContent = err.message || "An unexpected error occurred.";
            showCard(errorCard);
        } finally {
            submitBtn.disabled = false;
        }
    });

    // ---- Analyze form submit ----
    analyzeForm.addEventListener("submit", async (e) => {
        e.preventDefault();
        const repoUrl = analyzeRepoInput.value.trim();
        if (!repoUrl) return;

        const githubToken = analyzeTokenIn.value.trim() || null;

        showCard(loadingCard);
        analyzeSubmitBtn.disabled = true;
        animateSteps("analyze");

        try {
            const body = { repo_url: repoUrl };
            if (githubToken) body.github_token = githubToken;

            const response = await fetch("/api/analyze", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(body),
            });

            if (!response.ok) {
                const err = await response.json().catch(() => ({ detail: "Unknown error" }));
                throw new Error(err.detail || `HTTP ${response.status}`);
            }

            const data = await response.json();

            // Populate analyze result
            analyzeRepoName.textContent = data.repo_name;
            scoreSummary.textContent = data.summary;

            // Animate score
            const score = Math.min(100, Math.max(0, data.score));
            const circumference = 339.292; // 2 * PI * 54
            const offset = circumference - (score / 100) * circumference;

            // Color based on score
            let color = "#f85149"; // red
            if (score >= 70) color = "#39d353"; // green
            else if (score >= 40) color = "#e3b341"; // yellow

            scoreArc.style.stroke = color;
            scoreValue.style.color = color;

            // Trigger animation
            setTimeout(() => {
                scoreArc.style.strokeDashoffset = offset;
                scoreValue.textContent = score;
            }, 100);

            // Strengths
            strengthsList.innerHTML = "";
            (data.strengths || []).forEach(s => {
                const li = document.createElement("li");
                li.textContent = s;
                strengthsList.appendChild(li);
            });

            // Improvements
            improvementsList.innerHTML = "";
            (data.improvements || []).forEach(s => {
                const li = document.createElement("li");
                li.textContent = s;
                improvementsList.appendChild(li);
            });

            // Missing sections
            missingTags.innerHTML = "";
            (data.missing_sections || []).forEach(s => {
                const tag = document.createElement("span");
                tag.className = "missing-tag";
                tag.textContent = s;
                missingTags.appendChild(tag);
            });

            showCard(analyzeResultCard);

        } catch (err) {
            errorMessage.textContent = err.message || "An unexpected error occurred.";
            showCard(errorCard);
        } finally {
            analyzeSubmitBtn.disabled = false;
        }
    });

    // ---- Toggle preview / raw ----
    togglePreview.addEventListener("click", () => {
        togglePreview.classList.add("active");
        toggleRaw.classList.remove("active");
        previewPane.classList.remove("hidden");
        rawPane.classList.add("hidden");
    });

    toggleRaw.addEventListener("click", () => {
        toggleRaw.classList.add("active");
        togglePreview.classList.remove("active");
        rawPane.classList.remove("hidden");
        previewPane.classList.add("hidden");
    });

    // ---- Copy ----
    copyBtn.addEventListener("click", () => {
        navigator.clipboard.writeText(currentMarkdown).then(() => {
            showToast("✅ Markdown copied to clipboard!");
        }).catch(() => {
            showToast("❌ Failed to copy");
        });
    });

    // ---- Download ----
    downloadBtn.addEventListener("click", () => {
        const blob = new Blob([currentMarkdown], { type: "text/markdown;charset=utf-8" });
        const url = URL.createObjectURL(blob);
        const a = document.createElement("a");
        a.href = url;
        a.download = `${currentRepoName.replace("/", "_")}_README.md`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
        showToast("💾 README.md downloaded!");
    });

    // ---- New / Retry ----
    newBtn.addEventListener("click", () => {
        currentMarkdown = "";
        currentRepoName = "";
        switchTab("generate");
        repoInput.focus();
    });

    analyzeNewBtn.addEventListener("click", () => {
        // Reset score circle
        scoreArc.style.strokeDashoffset = 339.292;
        scoreValue.textContent = "0";
        switchTab("analyze");
        analyzeRepoInput.focus();
    });

    retryBtn.addEventListener("click", () => {
        switchTab(currentMode);
    });

})();
