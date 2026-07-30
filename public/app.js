const ICONS = {
  focal: `<svg viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.5"><circle cx="8" cy="8" r="6"/><circle cx="8" cy="8" r="1.6" fill="currentColor" stroke="none"/></svg>`,
  layout: `<svg viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.5"><rect x="2" y="2" width="12" height="12" rx="1.5"/><line x1="2" y1="8" x2="14" y2="8"/><line x1="9" y1="8" x2="9" y2="14"/></svg>`,
  space: `<svg viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M2 5V2h3M11 2h3v3M14 11v3h-3M5 14H2v-3"/><circle cx="8" cy="8" r="1.4" fill="currentColor" stroke="none"/></svg>`,
  color: `<svg viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M8 2c2.5 3 4.5 5.4 4.5 7.7A4.4 4.4 0 0 1 8 14a4.4 4.4 0 0 1-4.5-4.3C3.5 7.4 5.5 5 8 2z"/></svg>`,
  type: `<svg viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M3 13L7 3h2l4 10M4.8 9.5h6.4"/></svg>`,
  concept: `<svg viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M8 1.5v2M12.6 3.4l-1.4 1.4M14.5 8h-2M3.5 8h-2M4.8 4.8L3.4 3.4M6 12.5h4M6.8 14.5h2.4M8 6a2.6 2.6 0 0 1 1.4 4.8v1.2H6.6v-1.2A2.6 2.6 0 0 1 8 6z"/></svg>`,
};

const DIMS = {
  focal:   { label: "Focal hierarchy", color: "var(--focal)" },
  layout:  { label: "Layout",          color: "var(--layout)" },
  space:   { label: "Negative space",  color: "var(--space)" },
  color:   { label: "Color story",     color: "var(--color)" },
  type:    { label: "Typography",      color: "var(--type)" },
  concept: { label: "Concept",         color: "var(--concept)" },
};

const $ = (id) => document.getElementById(id);
const state = { tray: [], currentImage: null, mode: null };

// ---------- helpers ----------
function toast(msg, isError) {
  const t = $("toast");
  t.textContent = msg;
  t.classList.toggle("error", !!isError);
  t.classList.remove("hidden");
  clearTimeout(t._timer);
  t._timer = setTimeout(() => t.classList.add("hidden"), 3200);
}

function show(el, on = true) { el.classList.toggle("hidden", !on); }

function setLoading(on, text) {
  if (text) $("loading-text").textContent = text;
  show($("loading"), on);
}

async function api(path, body, signal) {
  const res = await fetch(path, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
    signal,
  });
  const data = await res.json();
  if (res.status === 401) { lock("Your session expired. Sign in again."); }
  if (!res.ok) throw new Error(data.error || "request failed");
  return data;
}

// ---------- entry ----------
const input = $("text-input");
const dropzone = $("dropzone");

function fileToDataURL(file) {
  return new Promise((resolve, reject) => {
    const r = new FileReader();
    r.onload = () => resolve(r.result);
    r.onerror = reject;
    r.readAsDataURL(file);
  });
}

// Downscale + re-encode to JPEG so phone photos (huge, sometimes HEIC)
// become a payload the vision API always accepts.
function normalizeImage(dataUrl, maxEdge = 1800) {
  return new Promise((resolve, reject) => {
    const img = new Image();
    img.onload = () => {
      const scale = Math.min(1, maxEdge / Math.max(img.width, img.height));
      if (scale === 1 && dataUrl.startsWith("data:image/jpeg")) return resolve(dataUrl);
      const canvas = document.createElement("canvas");
      canvas.width = Math.round(img.width * scale);
      canvas.height = Math.round(img.height * scale);
      canvas.getContext("2d").drawImage(img, 0, 0, canvas.width, canvas.height);
      resolve(canvas.toDataURL("image/jpeg", 0.92));
    };
    img.onerror = () => reject(new Error("That file isn't an image this browser can read"));
    img.src = dataUrl;
  });
}

async function handleFiles(files) {
  const file = [...files].find((f) => f.type.startsWith("image/") || /\.(heic|heif)$/i.test(f.name));
  if (!file) return;
  try {
    const raw = await fileToDataURL(file);
    const dataUrl = await normalizeImage(raw);
    startAnalyze(dataUrl);
  } catch (err) {
    toast(err.message, true);
  }
}

$("btn-upload").addEventListener("click", () => $("file-input").click());
$("file-input").addEventListener("change", (e) => {
  handleFiles(e.target.files);
  e.target.value = "";
});

["dragover", "dragenter"].forEach((ev) =>
  document.body.addEventListener(ev, (e) => {
    e.preventDefault();
    dropzone.classList.add("dragover");
  })
);
["dragleave", "drop"].forEach((ev) =>
  document.body.addEventListener(ev, (e) => {
    e.preventDefault();
    dropzone.classList.remove("dragover");
  })
);
document.body.addEventListener("drop", (e) => handleFiles(e.dataTransfer.files));
document.addEventListener("paste", (e) => {
  if (e.clipboardData.files.length) handleFiles(e.clipboardData.files);
});

function revealAnalysis() {
  const p = state.pendingReveal;
  if (!p) return false;
  state.pendingReveal = null;
  setEyeState(null);
  show($("thumb-wrap"), false);
  enterStage();
  setImage(p.images[0]);
  setGallery(p.images);
  resetPanels(p.keepRouting);
  renderFindings(p.result, "Why this works");
  return true;
}

// ---------- recent gallery: every finished read is kept and replayable ----------
async function loadRecent() {
  try {
    const res = await fetch("/api/gallery").then((r) => r.json());
    const items = res.items || [];
    const track = $("recent-track");
    track.innerHTML = "";
    if (!items.length) { show($("recent"), false); return; }
    items.forEach((item) => {
      const tile = document.createElement("button");
      tile.className = "recent-tile";
      tile.innerHTML = `<img alt="" loading="lazy"><span class="tile-grade"></span>`;
      tile.addEventListener("click", () => openStored(item));
      track.appendChild(tile);
      fetch(item.meta + "?v=" + Date.now()).then((r) => r.json()).then((meta) => {
        tile.querySelector("img").src = item.thumb || meta.thumb || "";
        const g = tile.querySelector(".tile-grade");
        g.textContent = meta.grade || "?";
        g.style.color = meta.grade
          ? (GRADE_COLORS[meta.grade[0].toUpperCase()] || "#fff") : "#fff";
        tile.title = meta.subject || "";
      }).catch(() => tile.remove());
    });
    show($("recent"));
  } catch { /* the gallery is a nice-to-have; never block the entry */ }
}

async function openStored(item) {
  setLoading(true, "Pulling that one back up…");
  try {
    const rec = await fetch(item.data + "?v=" + Date.now()).then((r) => r.json());
    if (!rec.images || !rec.images.length) throw new Error("empty record");
    state.lastAnalysis = { images: rec.images, context: rec.context };
    state.savedId = item.id;
    enterStage();
    setImage(rec.images[0]);
    setGallery(rec.images);
    resetPanels();
    renderFindings(rec.result, "Why this works");
  } catch {
    toast("Couldn't load that analysis", true);
  } finally {
    setLoading(false);
  }
}

// Square center-crop for the gallery tile. A remote image with no CORS
// headers taints the canvas — fall back to storing its URL untouched.
function squareThumb(src) {
  return new Promise((resolve) => {
    const img = new Image();
    img.crossOrigin = "anonymous";
    img.onload = () => {
      try {
        const s = Math.min(img.width, img.height), out = 320;
        const c = document.createElement("canvas");
        c.width = c.height = out;
        c.getContext("2d").drawImage(
          img, (img.width - s) / 2, (img.height - s) / 2, s, s, 0, 0, out, out);
        resolve(c.toDataURL("image/jpeg", 0.78));
      } catch { resolve(src); }
    };
    img.onerror = () => resolve(src);
    img.src = src;
  });
}

async function saveAnalysis(result) {
  try {
    const { images, context } = state.lastAnalysis || {};
    if (!images || !images.length) return;
    const thumb = await squareThumb(images[0]);
    const out = await api("/api/save", { thumb, images, context, result, id: state.savedId });
    if (out.id) state.savedId = out.id;
  } catch { /* persistence is best-effort */ }
}

const URL_RE = /^(https?:\/\/|www\.)\S+$/i;

async function startAnalyzeFromUrl(url) {
  setEyeState("loading"); // the eye reads while we go get the creative
  try {
    const res = await api("/api/fetch", { url });
    const raw = (res.images && res.images.length ? res.images : [res.image]);
    const images = await Promise.all(raw.map((u) => normalizeImage(u)));
    input.value = "";
    startAnalyze(images, { context: res.text });
  } catch (err) {
    setEyeState(null);
    toast(err.message, true);
  }
}

function submitText() {
  if (revealAnalysis()) return; // a finished read is waiting behind the eye
  const text = input.value.trim();
  if (!text) { input.focus(); return; }
  if (URL_RE.test(text)) { startAnalyzeFromUrl(text); return; }
  startGenerate({ prompt: text });
}
$("btn-go").addEventListener("click", submitText);
$("lets-go").addEventListener("click", () => revealAnalysis());
input.addEventListener("keydown", (e) => { if (e.key === "Enter") submitText(); });

// ---------- stage ----------
function enterStage() {
  show($("entry"), false);
  show($("stage"));
  show($("tray"));
  show($("btn-restart"));
  document.body.classList.add("staged");
  window.scrollTo(0, 0); // the stage always opens at the top
}

function resetToEntry() {
  document.body.classList.remove("staged");
  show($("stage"), false);
  show($("tray"), false);
  show($("btn-restart"), false);
  show($("entry"));
  show($("overall"), false);
  show($("findings-panel"), false);
  show($("sharpen-note"), false);
  show($("routing-note"), false);
  show($("btn-analyze-result"), false);
  $("findings").innerHTML = "";
  $("ad-img").removeAttribute("src");
  setGallery([]);
  input.value = "";
  input.focus();
  loadRecent();
}
$("btn-restart").addEventListener("click", resetToEntry);
$("brand").addEventListener("click", () => {
  if (document.body.classList.contains("staged")) resetToEntry();
});
$("brand-head").addEventListener("click", () => {
  $("brand-card").classList.toggle("open");
});

function setImage(dataUrl) {
  state.currentImage = dataUrl;
  $("ad-img").src = dataUrl;
}

function setGallery(images) {
  const strip = $("gallery-strip");
  strip.innerHTML = "";
  if (!images || images.length < 2) { show(strip, false); return; }
  images.forEach((src, i) => {
    const t = document.createElement("img");
    t.src = src;
    if (i === 0) t.classList.add("active");
    t.addEventListener("click", () => {
      setImage(src);
      strip.querySelectorAll("img").forEach((el) => el.classList.remove("active"));
      t.classList.add("active");
    });
    strip.appendChild(t);
  });
  show(strip);
}

const GRADE_COLORS = { A: "#4ade80", B: "#5b9bff", C: "#ffd02f", D: "#ff8a3c", F: "#ff6b4a" };

function renderGrade(result) {
  const card = $("grade-card");
  if (!result.grade) { show(card, false); return; }
  const color = GRADE_COLORS[result.grade[0].toUpperCase()] || "#fff";
  card.innerHTML = `
    <button class="grade-head">
      <span class="grade-letter" style="color:${color}"></span>
      <span class="grade-text">
        <span class="grade-label">The verdict</span>
        <span class="grade-reason"></span>
      </span>
      <svg class="chev" viewBox="0 0 12 12" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M3 4.5l3 3 3-3"/></svg>
    </button>
    <div class="grade-body">
      <p class="grade-detail"></p>
      <p class="improve-label">How to raise it</p>
      <ul class="improve-list"></ul>
    </div>`;
  card.querySelector(".grade-letter").textContent = result.grade;
  card.querySelector(".grade-reason").textContent = result.grade_reason || "";
  card.querySelector(".grade-detail").textContent = result.grade_detail || "";
  const ul = card.querySelector(".improve-list");
  (result.improve || []).forEach((idea) => {
    const li = document.createElement("li");
    li.textContent = idea;
    ul.appendChild(li);
  });
  card.querySelector(".grade-head").addEventListener("click", () => card.classList.toggle("open"));
  card.classList.remove("open");
  show(card);
}

const CATEGORY_LABELS = {
  "photo": "Photo",
  "print-ad": "Print ad",
  "social-ad": "Social media ad",
  "banner": "Display banner",
  "packaging": "Packaging",
  "social-post": "Social media post",
  "ui-web": "UI / web design",
  "logo": "Logo",
  "layout": "Layout / graphic",
  "other": "Visual",
};

function renderWhat(result) {
  const card = $("what-card");
  if (!result.subject && !result.category) { show(card, false); return; }
  $("what-type").textContent = CATEGORY_LABELS[result.category] || "Visual";
  $("what-desc").textContent = result.subject || "";
  buildTypeMenu(result.category);
  show(card);
}

// clicking the type chip lets the user correct the classification;
// the critic then re-reads the work against the corrected category's bar
function buildTypeMenu(current) {
  const menu = $("type-menu");
  menu.innerHTML = `<span class="menu-note">Judge it as…</span>`;
  Object.entries(CATEGORY_LABELS).forEach(([key, label]) => {
    if (key === current) return;
    const b = document.createElement("button");
    b.textContent = label;
    b.addEventListener("click", (e) => {
      e.stopPropagation();
      show(menu, false);
      reclassify(key, label);
    });
    menu.appendChild(b);
  });
}

async function reclassify(categoryKey, label) {
  if (!state.lastAnalysis) { toast("Nothing to re-read yet"); return; }
  setLoading(true, `Re-reading this as a ${label.toLowerCase()}…`);
  try {
    const result = await api("/api/analyze", {
      images: state.lastAnalysis.images,
      context: state.lastAnalysis.context,
      force_category: categoryKey,
    });
    renderFindings(result, "Why this works");
    saveAnalysis(result); // update the stored record with the corrected read
    toast(`Re-judged as ${label}`);
  } catch (err) {
    toast(err.message, true);
  } finally {
    setLoading(false);
  }
}

$("what-type").addEventListener("click", (e) => {
  e.stopPropagation();
  $("type-menu").classList.toggle("hidden");
});
document.addEventListener("click", () => show($("type-menu"), false));

function renderBrand(brand) {
  const card = $("brand-card");
  if (!brand || !brand.name) { show(card, false); return; }
  if (brand.logo) $("brand-logo").src = brand.logo;
  else $("brand-logo").removeAttribute("src");
  $("brand-name").textContent = brand.name;
  $("brand-bio-text").textContent = brand.bio || "No further background on this brand.";
  card.classList.remove("open");
  show(card);
}

function renderFindings(result, panelLabel) {
  renderWhat(result);
  renderBrand(result.brand);
  $("panel-label").textContent = panelLabel;
  $("overall-text").textContent = result.overall_read || "";
  show($("overall"), !!result.overall_read);
  $("sharpen-note").textContent = result.sharpen || "";
  show($("sharpen-note"), !!result.sharpen);
  renderGrade(result);

  const wrap = $("findings");
  wrap.innerHTML = "";
  (result.findings || []).forEach((f) => {
    const dim = DIMS[f.dimension] || { label: f.dimension, color: "#fff" };
    const card = document.createElement("div");
    card.className = "finding";
    card.innerHTML = `
      <button class="finding-head">
        <span class="dim-icon" style="color:${dim.color}">${ICONS[f.dimension] || ""}</span>
        <span class="head-text">
          <span class="dim-name" style="color:${dim.color}">${dim.label}</span>
          <span class="gist"></span>
        </span>
        <svg class="chev" viewBox="0 0 12 12" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M3 4.5l3 3 3-3"/></svg>
      </button>
      <div class="finding-body">
        <p class="explain"></p>
        <div class="chip-row">
          <button class="chip" style="background:${dim.color}"></button>
          <span class="add-hint">tap to add</span>
        </div>
      </div>`;
    card.querySelector(".gist").textContent = f.gist || f.fragment;
    card.querySelector(".explain").textContent = f.explanation;
    const chip = card.querySelector(".chip");
    chip.textContent = f.fragment;
    chip.addEventListener("click", (e) => {
      e.stopPropagation();
      addToTray(f.dimension, f.fragment);
      chip.classList.add("added");
      card.querySelector(".add-hint").textContent = "added";
    });
    card.querySelector(".finding-head").addEventListener("click", () => {
      card.classList.toggle("open");
    });
    wrap.appendChild(card);
  });
  show($("findings-panel"));
}

// ---------- analyze flow ----------
function resetPanels(keepRouting) {
  show($("overall"), false);
  show($("findings-panel"), false);
  show($("grade-card"), false);
  show($("brand-card"), false);
  show($("what-card"), false);
  show($("sharpen-note"), false);
  if (!keepRouting) show($("routing-note"), false);
  show($("btn-analyze-result"), false);
  $("findings").innerHTML = "";
}

// Bloodshot ramp tracks real progress: elapsed time vs a learned estimate of
// how long analysis actually takes on this machine (running average).
const EST_KEY = "cd_analyze_ms";
function analyzeEstimate() { return Number(localStorage.getItem(EST_KEY)) || 12000; }
function recordAnalyzeTime(ms) {
  localStorage.setItem(EST_KEY, Math.round(analyzeEstimate() * 0.7 + ms * 0.3));
}

let fillLoop = null;
function setEyeState(cls) {
  const eye = document.querySelector(".eye-btn");
  const fill = $("bar-fill");
  eye.classList.remove("loading", "done");
  cancelAnimationFrame(fillLoop);
  if (cls) eye.classList.add(cls);
  input.classList.toggle("loading", cls === "loading");
  if (cls === "loading") {
    input.placeholder = "Uploading and analyzing…";
  } else if (cls === "done") {
    input.placeholder = ""; // the bar goes quiet; "Let's go!" does the talking
  } else {
    input.placeholder = "Drop an image, paste a link, or type a concept…";
  }
  show($("lets-go"), cls === "done");
  if (cls === "loading") {
    // the bar fills left-to-right toward the eye, tracking real progress
    fill.style.opacity = "1";
    fill.style.width = "0%";
    const start = performance.now();
    const tau = analyzeEstimate() * 0.55;
    const tick = (now) => {
      const p = 1 - Math.exp(-(now - start) / tau);
      fill.style.width = (p * 100).toFixed(2) + "%";
      fillLoop = requestAnimationFrame(tick);
    };
    fillLoop = requestAnimationFrame(tick);
  } else if (cls === "done") {
    fill.style.opacity = "1";
    fill.style.width = "100%"; // it reaches the eye — which turns blue
  } else {
    fill.style.opacity = "0";
    fill.style.width = "0%";
  }
}

async function startAnalyze(dataUrlOrImages, opts = {}) {
  state.mode = "analyze";
  const images = Array.isArray(dataUrlOrImages) ? dataUrlOrImages : [dataUrlOrImages];
  state.lastAnalysis = { images, context: opts.context }; // kept for reclassification
  state.savedId = null; // a fresh read gets its own gallery record
  const fromEntry = !$("entry").classList.contains("hidden");
  if (fromEntry) {
    state.analyzeController = new AbortController();
    $("entry-thumb").src = images[0];
    show($("thumb-wrap")); // tiny preview of what the eye is reading
    setEyeState("loading"); // the eye stares straight, pulsates, goes bloodshot
  } else {
    enterStage();
    setImage(images[0]);
    setGallery(images);
    resetPanels(opts.keepRouting);
    setLoading(true, "Reading the work like a creative director…");
  }
  const t0 = performance.now();
  try {
    const result = await api("/api/analyze", { images, context: opts.context },
      fromEntry ? state.analyzeController.signal : undefined);
    recordAnalyzeTime(performance.now() - t0);
    saveAnalysis(result); // fire-and-forget into the gallery
    if (fromEntry) {
      // The eye boings big, stays red and shiny, and waits for a click.
      setEyeState("done");
      state.pendingReveal = { result, images, keepRouting: opts.keepRouting };
      return;
    }
    renderFindings(result, "Why this works");
  } catch (err) {
    if (fromEntry) { setEyeState(null); show($("thumb-wrap"), false); }
    if (err.name !== "AbortError") toast(err.message, true);
  } finally {
    setLoading(false);
    state.analyzeController = null;
  }
}

$("thumb-x").addEventListener("click", () => {
  if (state.analyzeController) state.analyzeController.abort();
  state.pendingReveal = null;
  setEyeState(null);
  show($("thumb-wrap"), false);
  toast("Upload canceled");
});

// ---------- generate flow ----------
async function startGenerate(payload) {
  state.mode = "generate";
  enterStage();
  show($("overall"), false);
  show($("findings-panel"), false);
  show($("sharpen-note"), false);
  show($("routing-note"), false);
  $("findings").innerHTML = "";
  setLoading(true, "Composing the prompt, then rendering…");
  try {
    const result = await api("/api/generate", payload);
    setImage(result.image);
    setGallery([]);
    $("overall-text").textContent = result.prompt_used;
    $("routing-note").textContent = result.routing;
    show($("overall"));
    show($("routing-note"));
    const btn = $("btn-analyze-result");
    show(btn);
    show($("findings-panel"));
    $("panel-label").textContent = "Generated with gpt-image-1";
    btn.onclick = () => startAnalyze(result.image, { keepRouting: true });
  } catch (err) {
    toast(err.message, true);
  } finally {
    setLoading(false);
  }
}

// ---------- tray ----------
function addToTray(dimension, fragment) {
  if (state.tray.some((t) => t.fragment === fragment)) return;
  state.tray.push({ dimension, fragment });
  renderTray();
}

function removeFromTray(fragment) {
  state.tray = state.tray.filter((t) => t.fragment !== fragment);
  renderTray();
  document.querySelectorAll(".chip.added").forEach((chip) => {
    if (chip.textContent === fragment) {
      chip.classList.remove("added");
      chip.closest(".finding").querySelector(".add-hint").textContent = "tap to add";
    }
  });
}

function renderTray() {
  const wrap = $("tray-chips");
  wrap.innerHTML = "";
  if (!state.tray.length) {
    wrap.innerHTML = `<span class="tray-empty">Tap a colored chip on the techniques you like — they become your prompt.</span>`;
  } else {
    state.tray.forEach((t) => {
      const dim = DIMS[t.dimension] || { color: "#fff" };
      const chip = document.createElement("button");
      chip.className = "tray-chip";
      chip.style.background = dim.color;
      chip.innerHTML = `<span class="frag"></span><span class="x">×</span>`;
      chip.querySelector(".frag").textContent = t.fragment;
      chip.addEventListener("click", () => removeFromTray(t.fragment));
      wrap.appendChild(chip);
    });
  }
  const covered = new Set(state.tray.map((t) => t.dimension)).size;
  $("tray-count").textContent = `· ${covered} of 6 dimensions`;
  show($("compiled"), false);
}

$("btn-copy").addEventListener("click", async () => {
  if (!state.tray.length) { toast("Add some fragments first"); return; }
  const btn = $("btn-copy");
  btn.disabled = true;
  btn.textContent = "Composing…";
  try {
    const out = await api("/api/compile", { fragments: state.tray.map((t) => t.fragment) });
    await navigator.clipboard.writeText(out.prompt);
    const c = $("compiled");
    c.textContent = out.prompt;
    show(c);
    toast("Copied — paste it into Ad Studio");
  } catch (err) {
    toast(err.message, true);
  } finally {
    btn.disabled = false;
    btn.textContent = "Copy for Ad Studio";
  }
});

$("btn-generate").addEventListener("click", () => {
  if (!state.tray.length) { toast("Add some fragments first"); return; }
  startGenerate({ fragments: state.tray.map((t) => t.fragment) });
});

// ---------- build the photo-real eye from the layered renders ----------
// eye-sclera.png = bare ball; eye-straight.png = source for the iris disc.
(() => {
  const BALL = { cx: 0.507, cy: 0.5, r: 0.388 };   // ball geometry in eye-sclera.png
  const IRIS = { cx: 0.508, cy: 0.486, r: 0.208 }; // iris geometry in eye-straight.png

  function load(src) {
    return new Promise((res, rej) => {
      const i = new Image();
      i.onload = () => res(i);
      i.onerror = rej;
      i.src = src;
    });
  }

  function circleCrop(img, cx, cy, r, feather) {
    const S = img.width;
    const d = Math.round(2 * r * S);
    const c = document.createElement("canvas");
    c.width = d; c.height = d;
    const ctx = c.getContext("2d");
    ctx.drawImage(img, cx * S - r * S, cy * S - r * S, d, d, 0, 0, d, d);
    // radial alpha mask (soft edge so the layer melts into what's beneath)
    const g = ctx.createRadialGradient(d / 2, d / 2, d / 2 * (1 - feather), d / 2, d / 2, d / 2);
    g.addColorStop(0, "rgba(0,0,0,1)");
    g.addColorStop(1, "rgba(0,0,0,0)");
    ctx.globalCompositeOperation = "destination-in";
    ctx.fillStyle = g;
    ctx.fillRect(0, 0, d, d);
    return c.toDataURL("image/png");
  }

  Promise.all([load("/eye-sclera.png"), load("/eye-straight.png")]).then(([sclera, straight]) => {
    const scleraURL = circleCrop(sclera, BALL.cx, BALL.cy, BALL.r, 0.02);
    const irisURL = circleCrop(straight, IRIS.cx, IRIS.cy, IRIS.r, 0.1);
    const eye = document.querySelector(".eye-btn .eye");
    const iris = document.querySelector(".eye-btn .iris");
    eye.classList.add("photo");
    eye.style.backgroundImage = `url(${scleraURL})`;
    iris.style.backgroundImage = `url(${irisURL})`;
    const irisFrac = IRIS.r / BALL.r; // iris diameter as a fraction of the ball
    const eyePx = eye.getBoundingClientRect().width || 40;
    const d = Math.round(eyePx * irisFrac);
    iris.style.width = d + "px";
    iris.style.height = d + "px";
    iris.style.margin = (-d / 2) + "px 0 0 " + (-d / 2) + "px";
  }).catch(() => {}); // CSS-drawn eye remains as the fallback
})();

// ---------- the eyeball follows the mouse ----------
(() => {
  const iris = document.querySelector(".eye-btn .iris");
  if (!iris) return;
  document.addEventListener("mousemove", (e) => {
    const eye = iris.closest(".eye").getBoundingClientRect();
    const cx = eye.left + eye.width / 2;
    const cy = eye.top + eye.height / 2;
    const dx = e.clientX - cx;
    const dy = e.clientY - cy;
    const dist = Math.hypot(dx, dy) || 1;
    const reach = Math.min(1, dist / 240) * 7; // max 7px travel
    iris.style.transform = `translate(${(dx / dist) * reach}px, ${(dy / dist) * reach}px)`;
  });
})();

// ---------- anonymous feedback ----------
$("btn-feedback").addEventListener("click", () => {
  show($("feedback-modal"));
  $("fb-text").focus();
});
$("fb-cancel").addEventListener("click", () => show($("feedback-modal"), false));
$("feedback-modal").addEventListener("click", (e) => {
  if (e.target === $("feedback-modal")) show($("feedback-modal"), false);
});
$("fb-send").addEventListener("click", async () => {
  const message = $("fb-text").value.trim();
  if (!message) { $("fb-text").focus(); return; }
  const btn = $("fb-send");
  btn.disabled = true;
  btn.textContent = "Sending…";
  try {
    const out = await api("/api/feedback", { message });
    show($("feedback-modal"), false);
    $("fb-text").value = "";
    toast(`Feedback ${out.number} sent — thank you`);
  } catch (err) {
    toast(err.message, true);
  } finally {
    btn.disabled = false;
    btn.textContent = "Send";
  }
});

// ---------- sign-in gate ----------
// The gate is in the markup already, so the app never flashes before auth.
function gateStatus(msg, isError) {
  const el = $("gate-status");
  el.textContent = msg || "";
  el.classList.toggle("error", !!isError);
  show(el, !!msg);
}

function lock(msg) {
  show($("gate"));
  show($("btn-signout"), false);
  gateStatus(msg || "", !!msg);
}

function unlock(me) {
  show($("gate"), false);
  const out = $("btn-signout");
  out.title = "Sign out of " + (me.email || "Creadir");
  show(out);
  fetch("/api/status")
    .then((r) => r.json())
    .then((s) => { if (!s.openai) toast("No OPENAI_API_KEY configured", true); })
    .catch(() => {});
  loadRecent();
  input.focus();
}

// Google's script loads async and fires no ready event, so watch for it.
function whenGoogleReady(cb, waited = 0) {
  if (window.google && window.google.accounts && window.google.accounts.id) return cb();
  if (waited > 8000) {
    gateStatus("Google sign-in didn't load. Check your connection and reload.", true);
    return;
  }
  setTimeout(() => whenGoogleReady(cb, waited + 100), 100);
}

async function onCredential(response) {
  gateStatus("Signing you in…");
  try {
    const res = await fetch("/api/auth", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ credential: response.credential }),
    });
    const data = await res.json();
    if (!res.ok) throw new Error(data.error || "sign-in failed");
    gateStatus("");
    unlock(data);
  } catch (err) {
    gateStatus(err.message, true);
  }
}

function renderSignIn(me) {
  if (!me.client_id) {
    gateStatus("Sign-in isn't configured on this deployment yet.", true);
    return;
  }
  whenGoogleReady(() => {
    google.accounts.id.initialize({
      client_id: me.client_id,
      callback: onCredential,
      auto_select: false,
      cancel_on_tap_outside: true,
    });
    google.accounts.id.renderButton($("gate-btn"), {
      theme: "filled_black", size: "large", shape: "pill",
      text: "signin_with", logo_alignment: "center", width: 260,
    });
    gateStatus("");
  });
}

$("btn-signout").addEventListener("click", async () => {
  try {
    await fetch("/api/auth", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ action: "signout" }),
    });
    if (window.google && google.accounts) google.accounts.id.disableAutoSelect();
  } catch { /* signing out locally is what matters */ }
  location.reload();
});

// ---------- boot ----------
(async function boot() {
  let me = { authenticated: false, client_id: "" };
  try {
    me = await fetch("/api/me", { cache: "no-store" }).then((r) => r.json());
  } catch {
    gateStatus("Couldn't reach the server. Reload to try again.", true);
    return;
  }
  if (me.authenticated) { unlock(me); return; }
  lock();
  renderSignIn(me);
})();
