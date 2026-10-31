// Google Analytics 4 for insights.voxen.io. Loaded from every page via <script defer src="/assets/analytics.js">.
// Pageviews are auto-sent. Clicks on the article CTAs (cloud.voxen.io link, KakaoTalk, email) are sent as
// `cta_click` {target: cloud|kakao|email|other, slug, href} so the read -> contact funnel is measurable.
(function () {
  var ID = "G-4FLXFLN5GP";
  var s = document.createElement("script");
  s.async = true;
  s.src = "https://www.googletagmanager.com/gtag/js?id=" + ID;
  document.head.appendChild(s);
  window.dataLayer = window.dataLayer || [];
  function gtag() { dataLayer.push(arguments); }
  window.gtag = gtag;
  gtag("js", new Date());
  gtag("config", ID);
  document.addEventListener("click", function (e) {
    var a = e.target.closest && e.target.closest(".cta a, .contact-actions a");
    if (!a) return;
    var h = a.getAttribute("href") || "";
    var target = h.indexOf("cloud.voxen.io") > -1 ? "cloud"
      : h.indexOf("open.kakao.com") > -1 ? "kakao"
      : h.indexOf("mailto:") === 0 ? "email" : "other";
    var m = location.pathname.match(/^\/posts\/([^/]+)/);
    gtag("event", "cta_click", { target: target, slug: m ? m[1] : location.pathname, href: a.href });
  });
})();
