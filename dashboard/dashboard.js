// Dashboard signal-table renderer.
// v0.1.6 P2-10: extracted from inline <script> so CSP can drop 'unsafe-inline'.

async function main() {
  const resp = await fetch("data/signal-table.csv");
  const text = await resp.text();
  const rows = parseCSV(text);
  document.getElementById("meta").textContent =
    `${rows.length} pilots · AACT snapshot ${rows[0]?.aact_snapshot || "?"}`;
  render(rows);
}
function parseCSV(text) {
  const lines = text.trim().split(/\r?\n/);
  const header = lines.shift().split(",");
  return lines.map(line => {
    const cells = splitCSVLine(line);
    return Object.fromEntries(header.map((h, i) => [h, cells[i] ?? ""]));
  });
}
function splitCSVLine(line) {
  const out = [];
  let cur = "", inQ = false;
  for (const ch of line) {
    if (ch === '"') { inQ = !inQ; continue; }
    if (ch === "," && !inQ) { out.push(cur); cur = ""; continue; }
    cur += ch;
  }
  out.push(cur);
  return out;
}
function render(rows) {
  const cols = [
    {key: "pilot_id", label: "ID"},
    {key: "pilot_title", label: "Pilot"},
    {key: "magnitude_value", label: "Magnitude (95% CI)"},
    {key: "n_trials_in_scope", label: "n"},
    {key: "tractability_AACT_only", label: "Tractability"},
    {key: "follow_up_potential", label: "Follow-up"},
    {key: "notes", label: "Notes"},
  ];
  const thead = document.querySelector("#signal-table thead");
  // v0.1.4 P1-14: keyboard-accessible sort headers (tabindex + role + aria-sort + Enter/Space binding)
  thead.innerHTML = "<tr>" + cols.map(c =>
    `<th scope="col" data-key="${c.key}" tabindex="0" role="button" aria-sort="none">${c.label}</th>`
  ).join("") + "</tr>";
  thead.querySelectorAll("th").forEach((th, i) => {
    const handler = () => sortBy(rows, cols[i].key);
    th.addEventListener("click", handler);
    th.addEventListener("keydown", e => {
      if (e.key === "Enter" || e.key === " ") { e.preventDefault(); handler(); }
    });
  });
  drawBody(rows);
}
let sortKey = "follow_up_potential", sortAsc = false;
function sortBy(rows, key) {
  if (sortKey === key) sortAsc = !sortAsc; else { sortKey = key; sortAsc = false; }
  rows.sort((a, b) => {
    const av = isFinite(parseFloat(a[key])) ? parseFloat(a[key]) : a[key];
    const bv = isFinite(parseFloat(b[key])) ? parseFloat(b[key]) : b[key];
    return (av > bv ? 1 : av < bv ? -1 : 0) * (sortAsc ? 1 : -1);
  });
  document.querySelectorAll("th").forEach(th => {
    th.classList.remove("sorted-asc", "sorted-desc");
    th.setAttribute("aria-sort", "none");
  });
  const active = document.querySelector(`th[data-key="${key}"]`);
  if (active) {
    active.classList.add(sortAsc ? "sorted-asc" : "sorted-desc");
    active.setAttribute("aria-sort", sortAsc ? "ascending" : "descending");
  }
  drawBody(rows);
}
function drawBody(rows) {
  const tbody = document.querySelector("#signal-table tbody");
  tbody.innerHTML = "";
  for (const r of rows) {
    const tr = document.createElement("tr");
    if (r.pilot_type === "tractability_probe") tr.classList.add("probe");
    const mag = parseFloat(r.magnitude_value);
    const lo = parseFloat(r.magnitude_ci_low);
    const hi = parseFloat(r.magnitude_ci_high);
    const magCell = isFinite(mag)
      ? `<span class="magnitude-bar" style="width:${Math.min(mag*120, 120).toFixed(1)}px" aria-hidden="true"></span>${mag.toFixed(3)} <span class="ci">[${lo.toFixed(3)}, ${hi.toFixed(3)}]</span>`
      : `<em class="ci">&mdash; (probe)</em>`;
    const cells = [
      `<td class="pilot-id">${escapeHtml(r.pilot_id)}</td>`,
      `<td>${escapeHtml(r.pilot_title)}</td>`,
      `<td>${magCell}</td>`,
      `<td>${escapeHtml(r.n_trials_in_scope)}</td>`,
      `<td>${escapeHtml(r.tractability_AACT_only)}</td>`,
      `<td class="followup">${escapeHtml(r.follow_up_potential)}/5</td>`,
      `<td>${escapeHtml(r.notes)}</td>`,
    ];
    tr.innerHTML = cells.join("");
    tbody.appendChild(tr);
  }
}
function escapeHtml(s) {
  return String(s ?? "")
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#39;");
}
main().catch(e => { document.getElementById("meta").textContent = "Error loading: " + e.message; });
