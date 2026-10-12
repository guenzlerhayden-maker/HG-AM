/* ============================================================================
   SPLIT-FLAP
   Settles the data cells the way a Solari departure board does: each character
   runs through intermediate glyphs and drops onto its value, left to right,
   then the whole row re-runs on a five second cycle.

   Opt in from the markup with data-flap on the element holding the value.

   Three things make this read as a board rather than as noise:

     - The value font is Courier Prime, a monospace. In a proportional face the
       cells would jitter sideways as glyphs of different widths cycled and the
       whole row would wobble.
     - Characters land in order, each taking a few more flaps than the one to
       its left, which is what a real board does. Landing them together reads
       as a slot machine.
     - The cells are staggered against each other too, so the row resolves
       across rather than all at once.
   ========================================================================= */

(function () {
  "use strict";

  var targets = Array.prototype.slice.call(document.querySelectorAll("[data-flap]"));
  if (!targets.length) return;

  // Nothing is rebuilt under reduced motion. The markup already holds the
  // final value, so doing nothing at all is the correct finished state.
  var reduced = window.matchMedia &&
                window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  if (reduced) return;

  var DIGITS = "0123456789";
  var LETTERS = "ABCDEFGHIJKLMNOPQRSTUVWXYZ";

  // A real Solari board flips fast and for a while. The first pass of this was
  // too settled: the leftmost character landed after 8 flaps and the row then
  // sat still for roughly 4.5 of every 5 seconds, which read as slow even
  // though each individual flap was quick. More flaps, held for less time
  // each, and a shorter gap between passes.
  var STEP = 36;          // ms a single flap is held  (~28 a second)
  var BASE = 18;          // flaps before the leftmost character lands
  var PER_CHAR = 8;       // each character to the right runs this many more
  var CELL_STAGGER = 120; // between one cell and the next
  var PERIOD = 4200;      // start of one pass to the start of the next

  function glyphsFor(ch) {
    if (/[0-9]/.test(ch)) return DIGITS;
    if (/[A-Za-z]/.test(ch)) return LETTERS;
    return null;          // spaces and punctuation are printed on the frame
  }

  function pick(set) { return set.charAt(Math.floor(Math.random() * set.length)); }

  // Rebuild each value as one span per character, keeping the real text for
  // assistive technology. Without this a screen reader would announce whatever
  // nonsense the board happens to be showing mid-flap, and would re-announce
  // it on every cycle.
  function build(el) {
    var text = el.textContent;
    el.textContent = "";

    var spoken = document.createElement("span");
    spoken.className = "visually-hidden";
    spoken.textContent = text;
    el.appendChild(spoken);

    var board = document.createElement("span");
    board.setAttribute("aria-hidden", "true");

    var cells = [];
    for (var i = 0; i < text.length; i++) {
      var ch = text.charAt(i);
      var set = glyphsFor(ch);
      var node = document.createElement("span");
      node.className = "pa-flap";
      // Start on a wrong glyph, not the answer, or the value is readable for a
      // frame before the board starts and the effect is spoiled.
      node.textContent = set ? pick(set) : ch;
      board.appendChild(node);
      cells.push({ node: node, target: ch, set: set });
    }

    el.appendChild(board);
    return cells;
  }

  var boards = targets.map(function (el, i) {
    return { el: el, cells: build(el), delay: i * CELL_STAGGER, visible: false };
  });

  function longest() {
    return boards.reduce(function (max, b) {
      var chars = b.cells.filter(function (c) { return c.set; }).length;
      return Math.max(max, b.delay + (BASE + (chars - 1) * PER_CHAR) * STEP);
    }, 0);
  }

  // Driven by elapsed time inside one rAF loop rather than a chain of
  // setTimeouts. A chained timeout drifts and gets throttled, so the flap
  // count never finished and characters were left showing whatever glyph they
  // happened to stop on. Working from a clock means every cell lands on its
  // value no matter how many frames were dropped along the way.
  function pass() {
    boards.forEach(function (b) {
      b.cells.forEach(function (c) { c.landed = false; c.step = -1; c.node.classList.remove("is-set"); });
    });

    var started = null;

    function frame(now) {
      if (started === null) started = now;
      var elapsed = now - started;
      var pending = false;

      boards.forEach(function (b) {
        var t = elapsed - b.delay;

        b.cells.forEach(function (cell, i) {
          if (!cell.set || cell.landed) return;

          var duration = (BASE + i * PER_CHAR) * STEP;

          if (t >= duration) {
            cell.node.textContent = cell.target;
            cell.node.classList.add("is-set");
            cell.landed = true;
            return;
          }

          pending = true;
          if (t < 0) return;

          var step = Math.floor(t / STEP);
          if (step !== cell.step) {
            cell.step = step;
            cell.node.textContent = pick(cell.set);
          }
        });
      });

      if (pending) requestAnimationFrame(frame);
    }

    requestAnimationFrame(frame);
  }

  // Re-runs only while the row is actually on screen. rAF already idles in a
  // background tab, but this also stops the cycle for someone who has scrolled
  // well past it, and restarts it when they come back.
  var anyVisible = false;
  var timer = null;

  function schedule() {
    clearTimeout(timer);
    if (!anyVisible) return;
    timer = setTimeout(function () {
      pass();
      schedule();
    }, PERIOD);
  }

  function start() {
    pass();
    schedule();
  }

  if (!("IntersectionObserver" in window)) {
    anyVisible = true;
    start();
    return;
  }

  var begun = false;
  var io = new IntersectionObserver(function (entries) {
    entries.forEach(function (entry) {
      var match = boards.filter(function (b) { return b.el === entry.target; })[0];
      if (match) match.visible = entry.isIntersecting;
    });

    anyVisible = boards.some(function (b) { return b.visible; });

    if (anyVisible && !begun) { begun = true; start(); }
    else if (anyVisible) schedule();
    else clearTimeout(timer);
  }, { threshold: 0.6 });

  boards.forEach(function (b) { io.observe(b.el); });
})();
