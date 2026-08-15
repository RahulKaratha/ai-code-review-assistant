const form = document.getElementById('review-form');
const modeSelect = document.getElementById('review_mode');
const branchFields = document.getElementById('branch-fields');
const submitBtn = document.getElementById('submit-btn');
const errorBox = document.getElementById('error-box');
const results = document.getElementById('results');
const spinner = document.getElementById('spinner');

modeSelect.addEventListener('change', () => {
  branchFields.style.display = modeSelect.value === 'branch' ? 'block' : 'none';
});

form.addEventListener('submit', async (e) => {
  e.preventDefault();
  errorBox.style.display = 'none';
  results.style.display = 'none';
  spinner.style.display = 'block';
  submitBtn.disabled = true;

  const body = {
    repository_url: document.getElementById('repository_url').value.trim(),
    review_mode: modeSelect.value,
    branch: document.getElementById('branch').value.trim() || 'main',
  };

  if (body.review_mode === 'branch') {
    body.base_branch = document.getElementById('base_branch').value.trim();
    body.target_branch = document.getElementById('target_branch').value.trim();
  }

  try {
    const res = await fetch('/review', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body),
    });

    const data = await res.json();

    if (!res.ok) {
      throw new Error(data.detail || `Server error ${res.status}`);
    }

    render(data);
  } catch (err) {
    errorBox.textContent = err.message;
    errorBox.style.display = 'block';
  } finally {
    spinner.style.display = 'none';
    submitBtn.disabled = false;
  }
});

function severity(s) {
  return `<span class="issue-severity sev-${s}">${s}</span>`;
}

function render(data) {
  document.getElementById('result-risk').innerHTML =
    `<span class="risk-badge risk-${data.overall_risk}">${data.overall_risk}</span>`;

  document.getElementById('result-summary').textContent = data.summary;

  const issuesEl = document.getElementById('result-issues');
  if (data.issues.length === 0) {
    issuesEl.innerHTML = '<p style="color:var(--muted);font-size:.9rem">No issues found.</p>';
  } else {
    issuesEl.innerHTML = data.issues.map(i => `
      <div class="issue issue-${i.severity}">
        <div class="issue-header">
          ${severity(i.severity)}
          <span class="issue-category">${i.category}</span>
        </div>
        <p class="issue-description">${i.description}</p>
        <p class="issue-recommendation"><strong>Fix:</strong> ${i.recommendation}</p>
      </div>`).join('');
  }

  const posEl = document.getElementById('result-positives');
  posEl.innerHTML = data.positive_observations.length
    ? data.positive_observations.map(o => `<li>${o}</li>`).join('')
    : '<li>None noted.</li>';

  results.style.display = 'block';
  results.scrollIntoView({ behavior: 'smooth' });
}
