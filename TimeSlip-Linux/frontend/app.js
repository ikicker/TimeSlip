var $ = function (id) { return document.getElementById(id); };

var state = {
  sessions: [],
  running: null,
  rate: 0,
  tick: null,
  editId: null
};

function api(path, options) {
  options = options || {};
  options.headers = options.headers || {};
  if (options.body && typeof options.body !== "string") {
    options.headers["Content-Type"] = "application/json";
    options.body = JSON.stringify(options.body);
  }
  return fetch(path, options).then(function (res) {
    return res.json().then(function (data) {
      if (!res.ok) throw new Error(data.error || "Request failed");
      return data;
    });
  });
}

function pad(n) { return String(n).padStart(2, "0"); }

function formatDuration(ms) {
  var total = Math.max(0, Math.floor(ms / 1000));
  var h = Math.floor(total / 3600);
  var m = Math.floor((total % 3600) / 60);
  var s = total % 60;
  return pad(h) + ":" + pad(m) + ":" + pad(s);
}

function hoursDecimal(ms) {
  return Math.round((ms / 3600000) * 10000) / 10000;
}

function fmtDateTime(ms) {
  return new Date(ms).toLocaleString([], {
    year: "numeric", month: "short", day: "numeric",
    hour: "numeric", minute: "2-digit"
  });
}

function fmtTime(ms) {
  return new Date(ms).toLocaleTimeString([], { hour: "numeric", minute: "2-digit" });
}

function toast(msg) {
  var el = $("toast");
  el.textContent = msg;
  el.style.display = "block";
  clearTimeout(toast._t);
  toast._t = setTimeout(function () { el.style.display = "none"; }, 2200);
}

function currentElapsed() {
  if (!state.running) return 0;
  return Date.now() - state.running.startMs;
}

function updateClock() {
  var ms = state.running ? currentElapsed() : 0;
  $("clock").innerHTML = formatDuration(ms).replace(/:(\d{2})$/, "<small>:$1</small>");
  $("statusText").textContent = state.running ? "Running" : "Ready";
  $("statusDot").classList.toggle("live", !!state.running);
  $("meta").textContent = state.running
    ? "Started " + fmtTime(state.running.startMs)
    : "Add a comment, then start the timer";
  $("startBtn").classList.toggle("hidden", !!state.running);
  $("stopBtn").classList.toggle("hidden", !state.running);
  $("comment").disabled = !!state.running;
  if (state.running && state.running.comment) $("comment").value = state.running.comment;
}

function dayKey(ms) {
  var d = new Date(ms);
  return d.getFullYear() + "-" + pad(d.getMonth() + 1) + "-" + pad(d.getDate());
}

function renderStats() {
  var today = dayKey(Date.now());
  var weekAgo = Date.now() - 7 * 86400000;
  var todayMs = 0, weekMs = 0, allMs = 0;
  state.sessions.forEach(function (s) {
    allMs += s.durationMs;
    if (dayKey(s.startMs) === today) todayMs += s.durationMs;
    if (s.startMs >= weekAgo) weekMs += s.durationMs;
  });
  if (state.running) {
    var live = currentElapsed();
    allMs += live; todayMs += live; weekMs += live;
  }
  $("statToday").textContent = formatDuration(todayMs);
  $("statWeek").textContent = formatDuration(weekMs);
  $("statAll").textContent = formatDuration(allMs);
}

function escapeHtml(str) {
  return String(str)
    .replace(/&/g, "&amp;").replace(/</g, "&lt;")
    .replace(/>/g, "&gt;").replace(/"/g, "&quot;");
}

function renderSessions() {
  var list = $("sessions");
  if (!state.sessions.length) {
    list.innerHTML = '<div class="empty">No completed sessions yet. Start the timer to log work.</div>';
    return;
  }
  var html = state.sessions.map(function (s) {
    var bill = hoursDecimal(s.durationMs);
    var money = state.rate ? " · $" + (bill * state.rate).toFixed(2) : "";
    return '<article class="session" data-id="' + s.id + '">' +
      '<p class="title">' + escapeHtml(s.comment || "Untitled work") + "</p>" +
      '<div class="times">' + fmtDateTime(s.startMs) + " → " + fmtTime(s.endMs) + "<br>" +
      formatDuration(s.durationMs) + " · " + bill.toFixed(2) + " hrs to bill" + money + "</div>" +
      '<div class="actions"><button class="mini" data-act="edit">Edit</button>' +
      '<button class="mini danger" data-act="delete">Delete</button></div></article>';
  }).join("");
  list.innerHTML = html;
}

function startTicker() {
  stopTicker();
  state.tick = setInterval(function () { updateClock(); renderStats(); }, 250);
}

function stopTicker() {
  if (state.tick) clearInterval(state.tick);
  state.tick = null;
}

function applyState(data) {
  state.sessions = data.sessions || [];
  state.running = data.running || null;
  state.rate = data.rate || 0;
  $("rateInput").value = state.rate || "";
  updateClock();
  renderStats();
  renderSessions();
  if (state.running) startTicker();
  else stopTicker();
}

function refresh() {
  return api("/api/state").then(applyState);
}

function toLocalInput(ms) {
  var d = new Date(ms);
  var local = new Date(d.getTime() - d.getTimezoneOffset() * 60000);
  return local.toISOString().slice(0, 16);
}

function bind() {
  $("startBtn").addEventListener("click", function () {
    api("/api/sessions/start", { method: "POST", body: { comment: $("comment").value } })
      .then(function () { $("comment").value = ""; return refresh(); })
      .catch(function (err) { toast(err.message); });
  });
  $("stopBtn").addEventListener("click", function () {
    api("/api/sessions/stop", { method: "POST", body: {} })
      .then(function () { toast("Session saved"); return refresh(); })
      .catch(function (err) { toast(err.message); });
  });
  $("clearAll").addEventListener("click", function () {
    if (!confirm("Delete all saved sessions on this Mac?")) return;
    api("/api/sessions/clear", { method: "POST", body: {} })
      .then(refresh)
      .catch(function (err) { toast(err.message); });
  });
  $("rateInput").addEventListener("change", function () {
    api("/api/settings", { method: "POST", body: { rate: $("rateInput").value } })
      .then(function (data) { state.rate = data.rate; renderSessions(); })
      .catch(function (err) { toast(err.message); });
  });
  $("exportBtn").addEventListener("click", function () {
    var from = $("exportFrom").value ? new Date($("exportFrom").value).getTime() : 0;
    var to = $("exportTo").value ? new Date($("exportTo").value).getTime() + 86400000 - 1 : 0;
    var url = "/api/export.xlsx?from=" + from + "&to=" + to;
    window.location.href = url;
    toast("Excel report downloading");
  });
  $("sessions").addEventListener("click", function (e) {
    var btn = e.target.closest("button");
    var card = e.target.closest(".session");
    if (!btn || !card) return;
    if (btn.getAttribute("data-act") === "edit") {
      var s = null;
      for (var i = 0; i < state.sessions.length; i++) {
        if (state.sessions[i].id === card.getAttribute("data-id")) s = state.sessions[i];
      }
      if (!s) return;
      state.editId = s.id;
      $("editComment").value = s.comment;
      $("editStart").value = toLocalInput(s.startMs);
      $("editEnd").value = toLocalInput(s.endMs);
      $("editSheet").classList.add("open");
    }
    if (btn.getAttribute("data-act") === "delete") {
      if (!confirm("Delete this work session?")) return;
      api("/api/sessions/" + card.getAttribute("data-id"), { method: "DELETE" })
        .then(refresh)
        .catch(function (err) { toast(err.message); });
    }
  });
  $("saveEdit").addEventListener("click", function () {
    api("/api/sessions/" + state.editId, {
      method: "PUT",
      body: {
        comment: $("editComment").value,
        startMs: new Date($("editStart").value).getTime(),
        endMs: new Date($("editEnd").value).getTime()
      }
    }).then(function () {
      $("editSheet").classList.remove("open");
      toast("Session updated");
      return refresh();
    }).catch(function (err) { toast(err.message); });
  });
  $("closeEdit").addEventListener("click", function () {
    $("editSheet").classList.remove("open");
  });
  document.querySelectorAll("[data-tab]").forEach(function (btn) {
    btn.addEventListener("click", function () {
      document.querySelectorAll("[data-tab]").forEach(function (b) { b.classList.remove("active"); });
      btn.classList.add("active");
      $("timerView").classList.toggle("hidden", btn.getAttribute("data-tab") !== "timer");
      $("exportView").classList.toggle("hidden", btn.getAttribute("data-tab") !== "export");
      $("logView").classList.toggle("hidden", btn.getAttribute("data-tab") !== "log");
    });
  });
}

bind();
refresh().catch(function () { toast("Could not reach the TimeSlip backend"); });
document.addEventListener("visibilitychange", function () {
  if (!document.hidden) { updateClock(); renderStats(); }
});
