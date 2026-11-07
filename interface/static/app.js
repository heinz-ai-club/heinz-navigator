// Plain JavaScript, no frameworks. Talks to /api/ask and /api/check.

const $ = (id) => document.getElementById(id);

// Build elements with textContent only, so nothing from the server is run as HTML.
function el(tag, text, className) {
  const node = document.createElement(tag);
  if (text !== undefined) node.textContent = text;
  if (className) node.className = className;
  return node;
}

// ---- Tabs ----
const tabs = [
  { tab: $("tab-ask"), panel: $("panel-ask") },
  { tab: $("tab-check"), panel: $("panel-check") },
];
tabs.forEach(({ tab }) => {
  tab.addEventListener("click", () => {
    tabs.forEach((t) => {
      const active = t.tab === tab;
      t.tab.setAttribute("aria-selected", String(active));
      t.panel.hidden = !active;
    });
  });
});

// ---- Shared helpers ----
async function postJSON(url, body) {
  const res = await fetch(url, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  if (!res.ok) throw new Error("request failed");
  return res.json();
}

function showError(box) {
  box.replaceChildren(el("p", "Sorry, something went wrong. Please try again.", "error"));
}

function statusNotice(status) {
  if (status === "placeholder") {
    return el("div", "This feature is not built yet. You are seeing a placeholder answer.", "notice");
  }
  if (status === "no_answer") {
    return el("div", "The documents do not answer this question. Please contact the right office.", "notice");
  }
  if (status === "unknown_program") {
    return el("div", "This program is not supported yet.", "notice");
  }
  return null;
}

function sourcesList(sources) {
  const frag = document.createDocumentFragment();
  if (!sources || sources.length === 0) return frag;
  frag.append(el("h2", "Sources"));
  const ul = el("ul");
  sources.forEach((s) => {
    const li = el("li");
    const a = el("a", s.title);
    // Only allow http(s) links.
    a.href = /^https?:\/\//i.test(s.url) ? s.url : "#";
    a.target = "_blank";
    a.rel = "noopener noreferrer";
    li.append(a);
    if (s.snippet) li.append(el("div", s.snippet, "snippet"));
    ul.append(li);
  });
  frag.append(ul);
  return frag;
}

// ---- Ask Heinz ----
const askForm = $("ask-form");
const questionBox = $("question");

// Enter submits; Shift+Enter makes a new line.
questionBox.addEventListener("keydown", (e) => {
  if (e.key === "Enter" && !e.shiftKey) {
    e.preventDefault();
    askForm.requestSubmit();
  }
});

askForm.addEventListener("submit", async (e) => {
  e.preventDefault();
  const question = questionBox.value.trim();
  const box = $("ask-result");
  if (!question) return;
  $("ask-button").disabled = true;
  box.replaceChildren(el("p", "Thinking...", "loading"));
  try {
    const data = await postJSON("/api/ask", { question });
    const wrap = el("div", undefined, "result");
    const notice = statusNotice(data.status);
    if (notice) wrap.append(notice);
    wrap.append(el("p", data.answer, "answer"), sourcesList(data.sources));
    box.replaceChildren(wrap);
  } catch {
    showError(box);
  } finally {
    $("ask-button").disabled = false;
  }
});

// ---- Requirement Checker ----
$("check-form").addEventListener("submit", async (e) => {
  e.preventDefault();
  const program = $("program").value.trim();
  const courses = $("courses").value
    .split(/[\n,]+/)
    .map((c) => c.trim())
    .filter(Boolean);
  const box = $("check-result");
  if (!program) return;
  $("check-button").disabled = true;
  box.replaceChildren(el("p", "Checking...", "loading"));
  try {
    const data = await postJSON("/api/check", { program, completed_courses: courses });
    const wrap = el("div", undefined, "result");
    const notice = statusNotice(data.status);
    if (notice) wrap.append(notice);

    wrap.append(el("h2", "Done"));
    const done = el("ul");
    data.satisfied.forEach((s) => {
      done.append(el("li", `${s.requirement}: ${s.courses.join(", ") || "none"}`));
    });
    wrap.append(done);

    wrap.append(el("h2", "Still needed"));
    const todo = el("ul");
    data.remaining.forEach((r) => {
      const li = el("li", `${r.requirement}: ${r.description}`);
      if (r.options.length) li.append(el("div", `Options: ${r.options.join(", ")}`, "small"));
      todo.append(li);
    });
    wrap.append(todo);

    if (data.notes) wrap.append(el("h2", "Notes"), el("p", data.notes));
    wrap.append(sourcesList(data.sources));
    box.replaceChildren(wrap);
  } catch {
    showError(box);
  } finally {
    $("check-button").disabled = false;
  }
});
