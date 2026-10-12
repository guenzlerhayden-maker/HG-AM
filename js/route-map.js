/* ============================================================================
   ROUTE MAP
   Hover (or focus, or tap) a station pin to open its log over the chart.
   ========================================================================= */

(function () {
  "use strict";

  var wrap = document.querySelector("[data-route-map]");
  if (!wrap) return;

  var pins = Array.prototype.slice.call(wrap.querySelectorAll(".pa-pin"));
  var logs = Array.prototype.slice.call(wrap.querySelectorAll(".pa-log"));
  var hint = document.querySelector("[data-map-hint]");
  var open = null;

  function show(station) {
    open = station;
    wrap.classList.toggle("has-open", !!station);

    pins.forEach(function (pin) {
      pin.classList.toggle("is-active", pin.dataset.station === station);
      pin.setAttribute("aria-expanded", pin.dataset.station === station ? "true" : "false");
    });

    logs.forEach(function (log) {
      log.classList.toggle("is-open", log.dataset.station === station);
    });

    if (hint) hint.hidden = !!station;
  }

  pins.forEach(function (pin) {
    var station = pin.dataset.station;

    pin.addEventListener("mouseenter", function () { show(station); });
    pin.addEventListener("mouseleave", function () { show(null); });
    pin.addEventListener("focus", function () { show(station); });
    pin.addEventListener("blur", function () { show(null); });

    // Tap toggles — touch devices have no hover, and without this the logs
    // would be unreachable on a phone.
    pin.addEventListener("click", function (e) {
      e.preventDefault();
      show(open === station ? null : station);
    });
  });

  document.addEventListener("keydown", function (e) {
    if (e.key === "Escape" && open) show(null);
  });

  // Draw the route once, the first time the chart is actually looked at.
  // Running it on load would spend the animation while the chart is still
  // below the fold, and the visitor would arrive to a finished line.
  //
  // The class is what the stylesheet animates against, and it is added here
  // rather than being present in the markup so that a visitor without
  // JavaScript keeps a complete chart instead of an empty one.
  (function () {
    var reduced = window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    if (reduced || !("IntersectionObserver" in window)) {
      wrap.classList.add("is-drawn");
      return;
    }
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (!entry.isIntersecting) return;
        wrap.classList.add("is-drawn");
        io.disconnect();            // once, not every time it scrolls past
      });
    }, { threshold: 0.35 });
    io.observe(wrap);
  })();
})();
