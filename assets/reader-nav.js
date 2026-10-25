/* 长文阅读页：生成幕级目录并跟随阅读位置。无 JS 时正文仍完整可读。 */
(function () {
  if (!document.body.classList.contains("layout-reader")) return;
  var sections = Array.prototype.slice.call(document.querySelectorAll(".wrap > section[id]"));
  if (!sections.length) return;

  var toc = document.createElement("aside");
  toc.className = "reader-toc";
  toc.setAttribute("aria-label", "本页目录");
  var title = document.createElement("div");
  title.className = "reader-toc-title";
  title.textContent = "本篇目录";
  toc.appendChild(title);
  var list = document.createElement("div");
  list.className = "reader-toc-list";
  toc.appendChild(list);

  var links = [];
  sections.forEach(function (section) {
    var heading = section.querySelector("h2");
    if (!heading) return;
    var group = document.createElement("div");
    group.className = "reader-toc-group";
    var link = document.createElement("a");
    link.href = "#" + section.id;
    link.textContent = heading.textContent.replace(/轻剧透|中度剧透|重度剧透/g, "").trim();
    link.dataset.target = section.id;
    group.appendChild(link);
    links.push(link);
    section.querySelectorAll(":scope > .act[id]").forEach(function (act) {
      var sub = document.createElement("a");
      sub.className = "reader-toc-sub";
      sub.href = "#" + act.id;
      sub.textContent = act.getAttribute("data-nav") || act.id;
      sub.dataset.target = act.id;
      group.appendChild(sub);
      links.push(sub);
    });
    list.appendChild(group);
  });

  var main = document.querySelector(".wrap");
  main.parentNode.insertBefore(toc, main);
  document.body.classList.add("has-reader-toc");

  function setActive(id) {
    links.forEach(function (a) {
      var active = a.dataset.target === id;
      a.classList.toggle("active", active);
      if (active) a.setAttribute("aria-current", "location");
      else a.removeAttribute("aria-current");
    });
  }

  if ("IntersectionObserver" in window) {
    var visible = new Map();
    var observer = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        visible.set(entry.target.id, entry.isIntersecting ? entry.intersectionRatio : 0);
      });
      var best = "", ratio = 0;
      visible.forEach(function (value, key) {
        if (value > ratio) { ratio = value; best = key; }
      });
      if (best) setActive(best);
    }, { rootMargin: "-12% 0px -62% 0px", threshold: [0, 0.1, 0.5] });
    sections.concat(Array.prototype.slice.call(document.querySelectorAll(".act[id]"))).forEach(function (el) {
      observer.observe(el);
    });
  }
})();
