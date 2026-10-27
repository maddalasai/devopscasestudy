// Minimal JavaScript: live cover preview on the Add a Book page + gentle reveal on scroll.
(function () {
  var title = document.getElementById("title");
  var author = document.getElementById("author");
  var status = document.getElementById("status");
  var pt = document.getElementById("preview-title");
  var pa = document.getElementById("preview-author");
  var total = document.getElementById("total_pages");
  var read = document.getElementById("pages_read");

  if (title && pt) {
    title.addEventListener("input", function () { pt.textContent = title.value || "Your next story"; });
    author.addEventListener("input", function () { pa.textContent = author.value || "Author"; });
    // Fill pages read automatically for finished / unread books
    function syncPages() {
      if (status.value === "Completed" && total.value) { read.value = total.value; }
      if (status.value === "Want to Read") { read.value = 0; }
    }
    status.addEventListener("change", syncPages);
    total.addEventListener("input", syncPages);
  }

  if ("IntersectionObserver" in window) {
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (e) { if (e.isIntersecting) { e.target.classList.add("in"); io.unobserve(e.target); } });
    }, { threshold: 0.08 });
    document.querySelectorAll(".book-card, .mood, .feature, .goal-book, .finished-book").forEach(function (el) {
      el.classList.add("reveal"); io.observe(el);
    });
  }
})();
