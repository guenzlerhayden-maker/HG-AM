/* ============================================================================
   REVEAL
   Adds a named class to an element the first time it is scrolled into view.

   The class is named in the markup as data-reveal="whatever", so a section
   opts into its own entrance and this file never learns anything about tickets
   or watches. Adding a third one later is a markup change, not a code change.
   ========================================================================= */

(function () {
  "use strict";

  var targets = Array.prototype.slice.call(document.querySelectorAll("[data-reveal]"));
  if (!targets.length) return;

  function reveal(el) {
    el.classList.add(el.getAttribute("data-reveal"));
  }

  // Reduced motion and a browser without IntersectionObserver resolve the same
  // way: show the finished state at once. The alternative is content that stays
  // hidden forever, which is a far worse failure than a missing animation.
  var reduced = window.matchMedia &&
                window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  if (reduced || !("IntersectionObserver" in window)) {
    targets.forEach(reveal);
    return;
  }

  var io = new IntersectionObserver(function (entries) {
    entries.forEach(function (entry) {
      if (!entry.isIntersecting) return;
      reveal(entry.target);
      io.unobserve(entry.target);          // once each, not on every pass
    });
  }, {
    threshold: 0.15,
    // Hold off until the block is properly on screen rather than firing on the
    // first pixel, so the entrance is not already over when it is looked at.
    rootMargin: "0px 0px -8% 0px"
  });

  targets.forEach(function (el) { io.observe(el); });
})();
