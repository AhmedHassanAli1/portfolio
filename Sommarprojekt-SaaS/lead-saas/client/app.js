const API = "http://localhost:3000";
const token = localStorage.getItem("token");
const REFRESH_INTERVAL = 2000;

// =====================
// AUTH
// =====================
function requireAuth() {
  const path = window.location.pathname;

  if (!token && (path.includes("dashboard") || path.includes("account"))) {
    window.location.href = "/login.html";
  }
}

requireAuth();

// =====================
// USER
// =====================
function getUser() {
  if (!token) return null;

  try {
    return JSON.parse(atob(token.split(".")[1]));
  } catch {
    return null;
  }
}

const user = getUser();

// =====================
// HELPERS
// =====================
function setText(id, value) {
  const el = document.getElementById(id);
  if (el) el.innerText = value;
}

function formatTime(timestamp) {
  return new Date(timestamp).toLocaleString("sv-SE");
}

function getGreeting() {
  const hour = new Date().getHours();

  if (hour < 12) return "God morgon";
  if (hour < 18) return "God dag";
  return "God kväll";
}

function getUserName() {
  return user?.name || user?.email?.split("@")[0] || "Användare";
}

function escapeHtml(value) {
  return String(value ?? "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

function getStatusBadge(status) {
  const base = "text-xs px-2.5 py-1 rounded-full font-medium";

  if (status === "FOLLOWED_UP") {
    return `${base} bg-green-100 text-green-700`;
  }

  if (status === "NY") {
    return `${base} bg-yellow-100 text-yellow-700`;
  }

  return `${base} bg-gray-100 text-gray-600`;
}

function getMiniBadge(status, label) {
  const base = "text-[11px] px-2 py-1 rounded-full font-medium";

  if (status === "SENT") {
    return `<span class="${base} bg-green-100 text-green-700">${label}: SENT</span>`;
  }

  if (status === "FAILED") {
    return `<span class="${base} bg-red-100 text-red-700">${label}: FAILED</span>`;
  }

  return `<span class="${base} bg-gray-100 text-gray-600">${label}: NONE</span>`;
}

function isValidEmail(email) {
  return /\S+@\S+\.\S+/.test(email);
}

// =====================
// HEADER
// =====================
function setHeader() {
  setText("greeting", `${getGreeting()}, ${getUserName()}`);
  setText("accountName", getUserName());
}

// =====================
// KPI
// =====================
function renderKpis(leads, autos, emailLog, smsLog) {
  const newLeads = leads.filter(lead => lead.status === "NY").length;
  const followedUpLeads = leads.filter(lead => lead.status === "FOLLOWED_UP").length;
  const totalLeads = leads.length;
  const activeAutomations = autos.length;
  const sentEmails = emailLog.filter(item => item.status === "SENT").length;
  const sentSms = smsLog.filter(item => item.status === "SENT").length;

  setText("newLeads", newLeads);
  setText("followedUpLeads", followedUpLeads);
  setText("totalLeads", totalLeads);
  setText("activeAutomations", activeAutomations);
  setText("sentEmails", sentEmails);
  setText("sentSms", sentSms);
}

// =====================
// RENDER: LEADS
// =====================
function renderLeads(leads) {
  const leadsEl = document.getElementById("leads");
  if (!leadsEl) return;

  if (!leads.length) {
    leadsEl.innerHTML = `
      <div class="text-center py-12 text-gray-500">
        <div class="text-3xl mb-2">📭</div>
        <div class="font-medium text-gray-700">Inga leads ännu</div>
        <div class="text-sm text-gray-400 mt-1">
          Skapa en testlead i panelen till höger för att testa flödet.
        </div>
      </div>
    `;
    return;
  }

  leadsEl.innerHTML = leads
    .map(lead => `
      <div class="border border-gray-200 rounded-2xl p-4 bg-gray-50">
        <div class="flex items-start justify-between gap-3">
          <div class="min-w-0">
            <div class="font-semibold text-gray-900 truncate">
              ${escapeHtml(lead.name)}
            </div>
            <div class="text-sm text-gray-600 mt-1">
              ${escapeHtml(lead.email || "Ingen e-post")}
            </div>
            <div class="text-sm text-gray-600 mt-1">
              ${escapeHtml(lead.phone || "Inget telefonnummer")}
            </div>
          </div>

          <span class="${getStatusBadge(lead.status)}">
            ${escapeHtml(lead.status)}
          </span>
        </div>

        <div class="text-sm text-gray-600 mt-3 break-words">
          ${escapeHtml(lead.message)}
        </div>

        <div class="flex flex-wrap gap-2 mt-3">
          ${getMiniBadge(lead.followUpEmailStatus, "Mail")}
          ${getMiniBadge(lead.followUpSmsStatus, "SMS")}
        </div>

        <div class="text-xs text-gray-400 mt-3">
          Skapad: ${formatTime(lead.createdAt)}
        </div>
      </div>
    `)
    .join("");
}

// =====================
// RENDER: AUTOMATIONS
// =====================
function renderAutomations(autos) {
  const autosEl = document.getElementById("autos");
  if (!autosEl) return;

  if (!autos.length) {
    autosEl.innerHTML = `
      <div class="rounded-2xl border border-dashed border-gray-200 p-4 text-sm text-gray-500 bg-gray-50">
        Inga automationer ännu.
      </div>
    `;
    return;
  }

  autosEl.innerHTML = autos
    .map(auto => `
      <div class="border border-gray-200 p-3 rounded-2xl bg-gray-50 flex justify-between items-start gap-3">
        <div class="min-w-0">
          <div class="flex flex-wrap items-center gap-2 mb-1">
            <span class="text-xs px-2.5 py-1 rounded-full font-medium ${
              auto.channel === "email"
                ? "bg-blue-100 text-blue-700"
                : "bg-amber-100 text-amber-700"
            }">
              ${auto.channel === "email" ? "MAIL" : "SMS"}
            </span>
            <span class="text-xs text-gray-500">${auto.delaySeconds}s</span>
          </div>

          ${auto.channel === "email"
            ? `<div class="text-sm font-medium text-gray-800 break-words">${escapeHtml(auto.subject || "Uppföljning från LeadFlow")}</div>`
            : ""
          }

          <div class="text-sm text-gray-700 break-words mt-1">
            ${escapeHtml(auto.message)}
          </div>
        </div>

        <button
          onclick="deleteAuto(${auto.id})"
          class="text-red-500 hover:text-red-700 text-sm font-medium shrink-0"
          title="Ta bort automation"
        >
          Ta bort
        </button>
      </div>
    `)
    .join("");
}

// =====================
// RENDER: ACTIVITY
// =====================
function renderActivity(activity) {
  const activityEl = document.getElementById("activity");
  if (!activityEl) return;

  if (!activity.length) {
    activityEl.innerHTML = `
      <div class="rounded-2xl border border-dashed border-gray-200 p-4 text-sm text-gray-500 bg-gray-50">
        Ingen aktivitet ännu.
      </div>
    `;
    return;
  }

  activityEl.innerHTML = activity
    .slice(0, 8)
    .map(item => `
      <div class="border-b border-gray-100 py-3 last:border-b-0">
        <div class="text-sm text-gray-800 break-words">
          ${escapeHtml(item.message)}
        </div>
        <div class="text-xs text-gray-400 mt-1">
          ${formatTime(item.createdAt)}
        </div>
      </div>
    `)
    .join("");
}

// =====================
// RENDER: EMAIL LOG
// =====================
function renderEmailLog(emailLog) {
  const emailEl = document.getElementById("emailLog");
  if (!emailEl) return;

  if (!emailLog.length) {
    emailEl.innerHTML = `
      <div class="rounded-2xl border border-dashed border-gray-200 p-4 text-sm text-gray-500 bg-gray-50">
        Inga skickade mail ännu.
      </div>
    `;
    return;
  }

  emailEl.innerHTML = emailLog
    .slice(0, 8)
    .map(email => `
      <div class="border border-gray-200 rounded-2xl p-4 bg-gray-50">
        <div class="flex justify-between items-start gap-3">
          <div class="min-w-0">
            <div class="text-sm font-medium text-gray-900">
              ${escapeHtml(email.to)}
            </div>
            <div class="text-sm text-gray-700 mt-1">
              ${escapeHtml(email.subject || "Uppföljning från LeadFlow")}
            </div>
            <div class="text-sm text-gray-600 mt-1 break-words">
              ${escapeHtml(email.message)}
            </div>
          </div>

          <span class="text-xs px-2.5 py-1 rounded-full font-medium ${
            email.status === "SENT"
              ? "bg-green-100 text-green-700"
              : "bg-red-100 text-red-700"
          } shrink-0">
            ${escapeHtml(email.status)}
          </span>
        </div>

        <div class="text-xs text-gray-400 mt-3">
          ${formatTime(email.createdAt)}
        </div>
      </div>
    `)
    .join("");
}

// =====================
// RENDER: SMS LOG
// =====================
function renderSmsLog(smsLog) {
  const smsEl = document.getElementById("smsLog");
  if (!smsEl) return;

  if (!smsLog.length) {
    smsEl.innerHTML = `
      <div class="rounded-2xl border border-dashed border-gray-200 p-4 text-sm text-gray-500 bg-gray-50">
        Inga skickade SMS ännu.
      </div>
    `;
    return;
  }

  smsEl.innerHTML = smsLog
    .slice(0, 8)
    .map(sms => `
      <div class="border border-gray-200 rounded-2xl p-4 bg-gray-50">
        <div class="flex justify-between items-start gap-3">
          <div class="min-w-0">
            <div class="text-sm font-medium text-gray-900">
              ${escapeHtml(sms.to)}
            </div>
            <div class="text-sm text-gray-600 mt-1 break-words">
              ${escapeHtml(sms.message)}
            </div>
          </div>

          <span class="text-xs px-2.5 py-1 rounded-full font-medium ${
            sms.status === "SENT"
              ? "bg-green-100 text-green-700"
              : "bg-red-100 text-red-700"
          } shrink-0">
            ${escapeHtml(sms.status)}
          </span>
        </div>

        <div class="text-xs text-gray-400 mt-3">
          ${formatTime(sms.createdAt)}
        </div>
      </div>
    `)
    .join("");
}

// =====================
// ACCOUNT
// =====================
function renderAccount() {
  setText("name", user?.name || "Okänd");
  setText("email", user?.email || "Ingen email");
}

// =====================
// CHANNEL UI
// =====================
function toggleAutomationFields() {
  const channelSelect = document.getElementById("autoChannel");
  const subjectWrap = document.getElementById("autoSubjectWrap");
  const channel = channelSelect?.value || "email";

  if (!subjectWrap) return;

  if (channel === "email") {
    subjectWrap.classList.remove("hidden");
  } else {
    subjectWrap.classList.add("hidden");
  }
}

// =====================
// LOAD
// =====================
async function load() {
  try {
    const headers = { Authorization: token };

    const [leadsRes, autosRes, activityRes, smsRes, emailRes] = await Promise.all([
      fetch(`${API}/leads`, { headers }),
      fetch(`${API}/automations`, { headers }),
      fetch(`${API}/activity`, { headers }),
      fetch(`${API}/sms-log`, { headers }),
      fetch(`${API}/email-log`, { headers })
    ]);

    if ([leadsRes, autosRes, activityRes, smsRes, emailRes].some(res => !res.ok)) {
      throw new Error("Kunde inte hämta dashboard-data");
    }

    const [leads, autos, activity, smsLog, emailLog] = await Promise.all([
      leadsRes.json(),
      autosRes.json(),
      activityRes.json(),
      smsRes.json(),
      emailRes.json()
    ]);

    renderKpis(leads, autos, emailLog, smsLog);
    renderLeads(leads);
    renderAutomations(autos);
    renderActivity(activity);
    renderSmsLog(smsLog);
    renderEmailLog(emailLog);
    renderAccount();
  } catch (error) {
    console.error(error);
  }
}

// =====================
// CREATE AUTOMATION
// =====================
async function addAuto() {
  const channelInput = document.getElementById("autoChannel");
  const delayInput = document.getElementById("delay");
  const subjectInput = document.getElementById("subject");
  const msgInput = document.getElementById("msg");

  const channel = channelInput?.value || "email";
  const delaySeconds = Number(delayInput?.value);
  const subject = subjectInput?.value?.trim();
  const message = msgInput?.value?.trim();

  if (!message) {
    alert("Skriv ett meddelande");
    return;
  }

  if (!delaySeconds || delaySeconds < 1) {
    alert("Ange antal sekunder, minst 1");
    return;
  }

  if (channel === "email" && !subject) {
    alert("Skriv ett ämne för mail");
    return;
  }

  try {
    const response = await fetch(`${API}/automations`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: token
      },
      body: JSON.stringify({
        channel,
        delaySeconds,
        subject,
        message
      })
    });

    if (!response.ok) {
      throw new Error("Kunde inte skapa automation");
    }

    delayInput.value = "";
    msgInput.value = "";
    if (subjectInput) subjectInput.value = "";

    load();
  } catch (error) {
    console.error(error);
    alert("Något gick fel när automationen skulle sparas");
  }
}

// =====================
// CREATE TEST LEAD
// =====================
async function addLead() {
  const nameInput = document.getElementById("leadName");
  const emailInput = document.getElementById("leadEmail");
  const phoneInput = document.getElementById("leadPhone");
  const messageInput = document.getElementById("leadMessage");

  const name = nameInput?.value?.trim();
  const email = emailInput?.value?.trim();
  const phone = phoneInput?.value?.trim();
  const message = messageInput?.value?.trim();

  if (!name) {
    alert("Skriv ett namn");
    return;
  }

  if (!email && !phone) {
    alert("Skriv minst en e-postadress eller ett telefonnummer");
    return;
  }

  if (email && !isValidEmail(email)) {
    alert("Skriv en giltig e-postadress");
    return;
  }

  if (!message) {
    alert("Skriv ett meddelande");
    return;
  }

  try {
    const response = await fetch(`${API}/leads`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: token
      },
      body: JSON.stringify({
        name,
        email,
        phone,
        message
      })
    });

    if (!response.ok) {
      throw new Error("Kunde inte skapa lead");
    }

    nameInput.value = "";
    emailInput.value = "";
    phoneInput.value = "";
    messageInput.value = "";

    load();
  } catch (error) {
    console.error(error);
    alert("Något gick fel när leaden skulle skapas");
  }
}

// =====================
// DELETE AUTOMATION
// =====================
async function deleteAuto(id) {
  try {
    const response = await fetch(`${API}/automations/${id}`, {
      method: "DELETE",
      headers: { Authorization: token }
    });

    if (!response.ok) {
      throw new Error("Kunde inte ta bort automation");
    }

    load();
  } catch (error) {
    console.error(error);
    alert("Något gick fel när automationen skulle tas bort");
  }
}

// =====================
// LOGOUT
// =====================
function logout() {
  localStorage.removeItem("token");
  window.location.href = "/login.html";
}

// =====================
// INIT
// =====================
setHeader();
toggleAutomationFields();
load();
setInterval(load, REFRESH_INTERVAL);