// One hat. It falls in at a random spot when the page loads, and you can
// grab and throw it. The physics aim for "feels real": impact-proportional
// bounces, sliding friction, spin coupled to motion, side collisions with
// page elements, resting on surfaces, and tipping off edges. No dependencies.
(function () {
  const G = 2400;            // gravity px/s^2
  const REST = 0.5;          // bounce restitution
  const AIR = 0.12;          // air drag /s
  const SLIDE_FRICTION = 3.2; // ground friction /s (exponential decay)
  const BOUNCE_SPEED = 230;  // below this vertical speed, contact instead of bounce
  const SIZE = 150;

  const img = new Image();
  img.src = "/hat.png";
  img.onload = () => {
    const c = document.createElement("canvas");
    c.width = img.width;
    c.height = img.height;
    const ctx = c.getContext("2d");
    ctx.drawImage(img, 0, 0);
    const d = ctx.getImageData(0, 0, c.width, c.height);
    const p = d.data;
    for (let i = 0; i < p.length; i += 4) {
      const r = p[i], g = p[i + 1], b = p[i + 2];
      if (r < 22 && g < 22 && b < 30) p[i + 3] = 0;
      else if (r < 34 && g < 34 && b < 44) p[i + 3] = Math.round(((r + g + b) / 3) * 6);
    }
    ctx.putImageData(d, 0, 0);
    const keyed = c.toDataURL("image/png");
    document.querySelectorAll(".brand-hat").forEach((el) => { el.src = keyed; });
    boot(keyed);
  };

  function boot(src) {
    const layer = document.createElement("div");
    layer.id = "hat-layer";
    document.body.appendChild(layer);

    const hat = document.createElement("img");
    hat.className = "pile-hat";
    hat.src = src;
    hat.draggable = false;
    hat.style.width = SIZE + "px";
    hat.style.height = SIZE + "px";
    layer.appendChild(hat);

    const bodyW = SIZE * 0.72, bodyH = SIZE * 0.52;
    const s = {
      x: 0, y: -SIZE, vx: 0, vy: 0,
      angle: 0, va: 0,
      grabbed: false, contact: null, // contact: {y,left,right,floor:bool}
      squash: 1, squashV: 0,
    };
    let last = performance.now();
    const trail = [];

    const onEntry = () => !document.body.classList.contains("staged");
    const floorY = () => window.innerHeight - 4;
    const bottom = () => s.y + bodyH / 2;
    const norm = (a) => { a = ((a % 360) + 360) % 360; return a > 180 ? a - 360 : a; };

    function surfaces() {
      const out = [{ y: floorY(), left: -1e9, right: 1e9, floor: true }];
      if (!onEntry()) return out;
      for (const el of [document.querySelector("#entry h1"), document.getElementById("dropzone")]) {
        if (!el) continue;
        const r = el.getBoundingClientRect();
        if (r.width > 0) out.push({ y: r.top + 6, left: r.left + 10, right: r.right - 10, floor: false, rect: r });
      }
      return out;
    }

    function spawn() {
      s.x = 60 + Math.random() * (window.innerWidth - 120);
      s.y = -SIZE;
      s.vx = (Math.random() - 0.5) * 120;
      s.vy = 30;
      s.angle = (Math.random() - 0.5) * 24;
      s.va = (Math.random() - 0.5) * 40;
      s.contact = null;
    }

    function impact(speed) { // squash proportional to how hard it hit
      s.squashV = -Math.min(1.5, speed / 850);
    }

    function integrate(dt) {
      const surfs = surfaces();

      // --- in contact: slide with friction, tilt into the slide, settle ---
      if (s.contact) {
        const c = s.contact;
        const stillThere = c.floor ||
          (onEntry() && s.x > c.left && s.x < c.right);
        if (!stillThere) {
          // overhanging or the surface vanished: tip off naturally
          s.contact = null;
          s.va += (s.x > (c.left + c.right) / 2 ? 1 : -1) * 30;
        } else {
          s.vx *= Math.exp(-SLIDE_FRICTION * dt);
          s.x += s.vx * dt;
          s.y = c.y - bodyH / 2;
          // tilt into the direction of the slide, then settle jaunty
          const target = Math.abs(s.vx) > 14
            ? Math.max(-14, Math.min(14, s.vx * 0.035))
            : (norm(s.angle) >= 0 ? 7 : -7);
          s.angle = norm(s.angle) + (target - norm(s.angle)) * Math.min(1, dt * 9);
          s.va = 0;
          if (Math.abs(s.vx) < 2) s.vx = 0;
          // walls while sliding
          if (s.x < bodyW / 2) { s.x = bodyW / 2; s.vx = Math.abs(s.vx) * 0.4; }
          if (s.x > window.innerWidth - bodyW / 2) {
            s.x = window.innerWidth - bodyW / 2; s.vx = -Math.abs(s.vx) * 0.4;
          }
          return;
        }
      }

      // --- free flight: substeps to keep fast motion stable ---
      const steps = 2;
      const h = dt / steps;
      for (let i = 0; i < steps; i++) {
        const prevBottom = bottom();
        const prevX = s.x;
        s.vy += G * h;
        const drag = Math.exp(-AIR * h);
        s.vx *= drag; s.vy *= drag;
        s.x += s.vx * h;
        s.y += s.vy * h;
        s.angle += s.va * h * 8;
        s.va *= Math.exp(-0.9 * h);

        // ceiling
        if (s.vy < 0 && s.y - bodyH / 2 < 0) {
          s.y = bodyH / 2;
          s.vy = Math.abs(s.vy) * 0.4;
          s.va *= -0.5;
          impact(Math.abs(s.vy));
        }
        // walls
        if (s.x < bodyW / 2) {
          s.x = bodyW / 2; s.vx = Math.abs(s.vx) * 0.45; s.va = -s.va * 0.5 + s.vx * 0.04;
        }
        if (s.x > window.innerWidth - bodyW / 2) {
          s.x = window.innerWidth - bodyW / 2; s.vx = -Math.abs(s.vx) * 0.45; s.va = -s.va * 0.5 + s.vx * 0.04;
        }

        for (const c of surfaces()) {
          // side hits on raised elements (headline, input bar)
          if (!c.floor && c.rect) {
            const r = c.rect;
            const withinY = bottom() > r.top + 10 && s.y - bodyH / 2 < r.bottom;
            if (withinY && prevX + bodyW / 2 <= r.left && s.x + bodyW / 2 > r.left && s.vx > 0) {
              s.x = r.left - bodyW / 2; s.vx = -s.vx * 0.42; s.va += s.vx * 0.06;
            } else if (withinY && prevX - bodyW / 2 >= r.right && s.x - bodyW / 2 < r.right && s.vx < 0) {
              s.x = r.right + bodyW / 2; s.vx = -s.vx * 0.42; s.va += s.vx * 0.06;
            }
          }
          // top landings
          const inSpan = s.x > c.left && s.x < c.right;
          if (s.vy > 0 && inSpan && bottom() >= c.y && prevBottom <= c.y + 10) {
            s.y = c.y - bodyH / 2;
            if (Math.abs(s.vy) > BOUNCE_SPEED) {
              impact(Math.abs(s.vy));
              s.vy = -s.vy * (REST - Math.min(0.18, Math.abs(s.vy) / 6000));
              s.vx *= 0.86;
              // spin from off-center impacts and existing motion
              s.va = s.va * 0.4 + s.vx * 0.07 + (Math.random() - 0.5) * 10;
            } else {
              impact(Math.abs(s.vy) * 0.8);
              s.vy = 0;
              s.contact = c; // enter sliding contact
            }
            break;
          }
        }
      }
      if (s.y > window.innerHeight + SIZE * 3) spawn(); // escaped below: bring it back
    }

    function step(now) {
      const dt = Math.min(0.032, (now - last) / 1000);
      last = now;

      if (s.grabbed) {
        // pendulum tilt from drag velocity, so carrying it feels physical
        const recent = trail[trail.length - 1], older = trail[0];
        if (recent && older && recent.t > older.t) {
          const v = (recent.x - older.x) / ((recent.t - older.t) / 1000);
          const target = Math.max(-22, Math.min(22, v * 0.02));
          s.angle = norm(s.angle) + (target - norm(s.angle)) * Math.min(1, dt * 10);
        }
      } else {
        integrate(dt);
      }

      s.squashV += (1 - s.squash) * 240 * dt;
      s.squashV *= 0.88;
      s.squash += s.squashV * dt * 11;

      hat.style.transform =
        "translate(" + (s.x - SIZE / 2) + "px," + (s.y - SIZE / 2) + "px) " +
        "rotate(" + s.angle + "deg) scale(" + (2 - s.squash) + "," + s.squash + ")";
      requestAnimationFrame(step);
    }

    // ---- grab and throw ----
    hat.addEventListener("pointerdown", (e) => {
      e.preventDefault();
      hat.setPointerCapture(e.pointerId);
      s.grabbed = true;
      s.contact = null;
      s.vx = 0; s.vy = 0; s.va = 0;
      trail.length = 0;
      hat.classList.add("grabbed");
    });
    hat.addEventListener("pointermove", (e) => {
      if (!s.grabbed) return;
      s.x = e.clientX;
      s.y = Math.max(bodyH / 2, e.clientY);
      trail.push({ x: e.clientX, y: e.clientY, t: performance.now() });
      if (trail.length > 6) trail.shift();
    });
    const release = () => {
      if (!s.grabbed) return;
      s.grabbed = false;
      hat.classList.remove("grabbed");
      if (trail.length >= 2) {
        const a = trail[0], b = trail[trail.length - 1];
        const dt = Math.max(0.016, (b.t - a.t) / 1000);
        s.vx = (b.x - a.x) / dt;
        s.vy = (b.y - a.y) / dt;
        s.va = s.vx * 0.055;
      }
    };
    hat.addEventListener("pointerup", release);
    hat.addEventListener("pointercancel", release);

    setTimeout(() => { spawn(); requestAnimationFrame(step); }, 600);
  }
})();
