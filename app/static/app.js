const loadHomepageBtn = document.getElementById("load-homepage-btn");
const analyzeBtn = document.getElementById("analyze-btn");
const queryInput = document.getElementById("query-input");
const cardsDiv = document.getElementById("cards");
const reportOutput = document.getElementById("report-output");
const loadingDiv = document.getElementById("loading");

function formatMetric(value, digits = 2) {
  if (value === null || value === undefined || value === "N/A") return "N/A";
  if (typeof value === "number") {
    return value.toLocaleString(undefined, {
      maximumFractionDigits: digits,
    });
  }
  return value;
}

function renderHomepageCards(data) {
  cardsDiv.innerHTML = "";

  const items = Array.isArray(data) ? data : (data.topics || data.cards || []);
  if (!items.length) {
    cardsDiv.innerHTML = `<p class="empty-state">No homepage data returned.</p>`;
    return;
  }

  items.forEach((item) => {
    const card = document.createElement("div");
    card.className = "card";

    const avgEngagement =
      item.avg_engagement_rate ??
      item.avg_engagement ??
      "N/A";

    const topDuration =
      item.top_duration_bucket ??
      item.duration_bucket ??
      "N/A";

    const topKeyword =
      item.top_keyword ??
      item.keyword ??
      item.strongest_keyword_signal ??
      "N/A";

    card.innerHTML = `
      <h3>${item.topic || "Topic"}</h3>
      <div class="metric">
        <strong>Average engagement</strong>
        <div class="metric-value">${formatMetric(avgEngagement, 4)}</div>
      </div>
      <div class="metric">
        <strong>Top duration bucket</strong>
        <div class="metric-value">${topDuration}</div>
      </div>
      <div class="metric">
        <strong>Strongest keyword signal</strong>
        <div class="metric-value">${topKeyword}</div>
      </div>
    `;

    cardsDiv.appendChild(card);
  });
}

async function loadHomepage() {
  cardsDiv.innerHTML = `<p class="empty-state">Loading dashboard...</p>`;

  try {
    const res = await fetch("/homepage");
    const data = await res.json();
    renderHomepageCards(data);
  } catch (err) {
    cardsDiv.innerHTML = `<p class="empty-state">Failed to load homepage data.</p>`;
    console.error(err);
  }
}

function extractReportSections(data) {
  const analysis = data.analysis || {};
  const summary = analysis.summary || {};
  const hypothesis = analysis.hypothesis || {};

  const durationPatterns = analysis.duration_patterns || [];
  const keywordPatterns = analysis.keyword_patterns || [];

  const bestDuration = durationPatterns[0] || {};
  const bestKeyword = keywordPatterns[0] || {};

  const recommendation =
    analysis.recommendation ||
    `For this topic, creators should lean into ${bestDuration.duration_bucket || "high-performing formats"} and keyword framing around '${bestKeyword.keyword || "top-performing language"}'.`;

  return {
    overview: [
      `Videos analyzed: ${formatMetric(summary.num_videos, 0)}`,
      `Average views: ${formatMetric(summary.avg_views, 1)}`,
      `Median views: ${formatMetric(summary.median_views, 1)}`,
      `Average engagement rate: ${formatMetric(summary.avg_engagement_rate, 4)}`,
    ],
    formatSignal: [
      `Best duration bucket: ${bestDuration.duration_bucket || "N/A"}`,
      `Average engagement in that bucket: ${formatMetric(bestDuration.avg_engagement_rate, 4)}`,
    ],
    keywordSignal: [
      `Strongest keyword: ${bestKeyword.keyword || "N/A"}`,
      `Average engagement rate: ${formatMetric(bestKeyword.avg_engagement_rate, 4)}`,
      `Matching videos: ${formatMetric(bestKeyword.video_count, 0)}`,
    ],
    hypothesis: hypothesis.hypothesis || "No hypothesis returned.",
    evidence: hypothesis.supporting_evidence || [],
    caveats: hypothesis.caveats || [],
    recommendation: recommendation,
  };
}

function renderReport(data) {
  const sections = extractReportSections(data);

  const summaryCards = `
  <div class="mini-stats">
    <div class="mini-stat">
      <span>Videos</span>
      <strong>${formatMetric((data.analysis || {}).summary?.num_videos, 0)}</strong>
    </div>
    <div class="mini-stat">
      <span>Avg Views</span>
      <strong>${formatMetric((data.analysis || {}).summary?.avg_views, 0)}</strong>
    </div>
    <div class="mini-stat">
      <span>Engagement</span>
      <strong>${formatMetric((data.analysis || {}).summary?.avg_engagement_rate, 4)}</strong>
    </div>
  </div>
`;

  reportOutput.innerHTML = `
    ${summaryCards}

    <div class="report-block">
        <div class="report-section highlight">
        <h3>Hypothesis</h3>
        <p>${sections.hypothesis}</p>
        </div>

        <div class="report-section takeaway strong-takeaway">
        <h3>Creator Takeaway</h3>
        <p>${sections.recommendation}</p>
        </div>

        <div class="report-section">
        <h3>Supporting Evidence</h3>
        <ul>${sections.evidence.map(item => `<li>${item}</li>`).join("")}</ul>
        </div>

        <div class="report-section">
        <h3>Overview</h3>
        <ul>${sections.overview.map(item => `<li>${item}</li>`).join("")}</ul>
        </div>

        <div class="report-section">
        <h3>Top Format Signal</h3>
        <ul>${sections.formatSignal.map(item => `<li>${item}</li>`).join("")}</ul>
        </div>

        <div class="report-section">
        <h3>Top Keyword Signal</h3>
        <ul>${sections.keywordSignal.map(item => `<li>${item}</li>`).join("")}</ul>
        </div>

        <div class="report-section">
        <h3>Caveats</h3>
        <ul>${sections.caveats.map(item => `<li>${item}</li>`).join("")}</ul>
        </div>
    </div>
    `;
}

let chartInstance = null;

function renderChart(data) {
  const ctx = document.getElementById("durationChart");

  const patterns = data.analysis?.duration_patterns || [];

  const labels = patterns.map(p => p.duration_bucket);
  const values = patterns.map(p => p.avg_engagement_rate);

  if (chartInstance) {
    chartInstance.destroy();
  }

  chartInstance = new Chart(ctx, {
    type: "bar",
    data: {
      labels: labels,
      datasets: [{
        label: "Avg Engagement Rate",
        data: values,
      }]
    },
    options: {
        responsive: true,
        plugins: {
            legend: { display: false },
            title: {
            display: true,
            text: "Engagement Rate by Video Length",
            font: {
                size: 16
            }
            }
        },
        scales: {
            x: {
            title: {
                display: true,
                text: "Video Duration"
            }
            },
            y: {
            title: {
                display: true,
                text: "Engagement Rate"
            }
            }
        }
        }
  });
}

async function runAnalysis(query) {
  if (!query) return;

  loadingDiv.classList.remove("hidden");
  reportOutput.innerHTML = `<p class="empty-state">Running analysis...</p>`;

  try {
    const res = await fetch(`/analyze?query=${encodeURIComponent(query)}`);
    console.log("RUNNING QUERY:", query);
    const data = await res.json();
    console.log("ANALYZE DATA:", data);

    renderReport(data);
    renderChart(data);

  } catch (err) {
    reportOutput.innerHTML = `<p class="empty-state">Analysis failed.</p>`;
    console.error(err);
  } finally {
    loadingDiv.classList.add("hidden");
  }
}

loadHomepageBtn.addEventListener("click", loadHomepage);

analyzeBtn.addEventListener("click", () => {
  runAnalysis(queryInput.value.trim());
});

queryInput.addEventListener("keydown", (e) => {
  if (e.key === "Enter") {
    runAnalysis(queryInput.value.trim());
  }
});

document.querySelectorAll(".topic-btn").forEach((btn) => {
  btn.addEventListener("click", () => {
    const topic = btn.textContent.trim();
    queryInput.value = topic;
    runAnalysis(topic);
  });
});


loadHomepage();