// Renders the entire page from data/data.json.
// To update the site: edit data/data.json and reload. No build step required.

const DATA_URL = "data/data.json";

function el(tag, opts = {}, children = []) {
  const node = document.createElement(tag);
  if (opts.className) node.className = opts.className;
  if (opts.text !== undefined) node.textContent = opts.text;
  if (opts.html !== undefined) node.innerHTML = opts.html;
  for (const child of [].concat(children)) {
    if (child) node.appendChild(child);
  }
  return node;
}

function linkLabel(key) {
  const labels = {
    scholar: "Google Scholar",
    github: "GitHub",
    linkedin: "LinkedIn",
    twitter: "X",
    cv: "CV (PDF)",
    arxiv: "arXiv",
    project: "Project Page",
    code: "Code",
    pdf: "PDF",
  };
  return labels[key] || (key[0].toUpperCase() + key.slice(1));
}

function renderHeader(data) {
  document.title = data.name || "Homepage";
  document.getElementById("name").textContent = data.name || "";
  document.getElementById("tagline").textContent = data.tagline || "";
  document.getElementById("bio").textContent = data.bio || "";

  if (data.photo) {
    const photo = document.getElementById("photo");
    photo.src = data.photo;
    photo.alt = data.name || "";
    photo.hidden = false;
    photo.onerror = () => { photo.hidden = true; };
  }

  const contactParts = [];
  if (data.email) contactParts.push(data.email);
  if (data.phone) contactParts.push(data.phone);
  document.getElementById("contact").textContent = contactParts.join(" | ");

  const linksNav = document.getElementById("links");
  linksNav.innerHTML = "";
  for (const [key, url] of Object.entries(data.links || {})) {
    if (!url) continue;
    linksNav.appendChild(el("a", { text: linkLabel(key) }, []).also(a => {
      a.href = url;
      a.target = "_blank";
      a.rel = "noopener";
    }));
  }
}

// small helper so we can chain attribute-setting inline above
Object.defineProperty(Node.prototype, "also", {
  value: function (fn) { fn(this); return this; },
  enumerable: false,
});

function bolded(authors, selfMatches) {
  return authors
    .map(a => (selfMatches.includes(a.replace(/†$/, "")) ? `<span class="self">${a}</span>` : a))
    .join(", ");
}

function section(title) {
  const wrap = el("section", { className: "section" });
  wrap.appendChild(el("h2", { text: title }));
  return wrap;
}

function renderSimpleList(title, items, formatEntry) {
  if (!items || items.length === 0) return null;
  const wrap = section(title);
  for (const item of items) {
    wrap.appendChild(formatEntry(item));
  }
  return wrap;
}

function entryHeader(titleText, orgText, dates) {
  const row = el("div", { className: "entry-row" });
  const left = el("span", { className: "entry-title", text: titleText });
  row.appendChild(left);
  if (dates) row.appendChild(el("span", { className: "entry-dates", text: dates }));
  const wrap = el("div", {}, [row]);
  if (orgText) wrap.appendChild(el("div", { className: "entry-org", text: orgText }));
  return wrap;
}

function renderEducation(data) {
  return renderSimpleList("Education", data.education, (e) => {
    const entry = el("div", { className: "entry" }, [
      entryHeader(e.degree, e.institution, e.dates),
    ]);
    if (e.details && e.details.length) {
      const ul = el("ul", {}, e.details.map(d => el("li", { text: d })));
      entry.appendChild(el("div", { className: "entry-details" }, [ul]));
    }
    return entry;
  });
}

function renderHonors(data) {
  return renderSimpleList("Awards & Honors", data.honors, (h) => {
    const row = el("div", { className: "entry-row" }, [
      el("span", { text: h.title }),
      h.dates ? el("span", { className: "entry-dates", text: h.dates }) : null,
    ]);
    return el("div", { className: "entry entry-tight" }, [row]);
  });
}

function renderResearchExperience(data) {
  return renderSimpleList("Research Experience", data.research_experience, (r) => {
    const entry = el("div", { className: "entry" }, [
      entryHeader(r.role, r.org, r.dates),
    ]);
    if (r.description) entry.appendChild(el("p", { className: "entry-details", text: r.description }));
    return entry;
  });
}

function renderPublications(data) {
  const selfMatches = data.self_author_matches || [];
  return renderSimpleList("Publications", data.publications, (p) => {
    const entry = el("div", { className: "entry" });
    entry.appendChild(el("div", { className: "entry-title", text: p.title }));

    let authorsHtml = bolded(p.authors || [], selfMatches);
    if (p.note) authorsHtml += ` (${p.note})`;
    entry.appendChild(el("p", { className: "pub-authors", html: authorsHtml }));

    const venueText = [p.venue, p.year].filter(Boolean).join(", ");
    if (venueText) entry.appendChild(el("p", { className: "pub-venue", text: venueText }));

    const links = Object.entries(p.links || {}).filter(([, url]) => url);
    if (links.length) {
      const linksWrap = el("div", { className: "pub-links" });
      for (const [key, url] of links) {
        linksWrap.appendChild(el("a", { text: linkLabel(key) }).also(a => {
          a.href = url;
          a.target = "_blank";
          a.rel = "noopener";
        }));
      }
      entry.appendChild(linksWrap);
    }
    return entry;
  });
}

function renderTeaching(data) {
  return renderSimpleList("Teaching", data.teaching, (t) => {
    const courseTitle = t.course_number ? `${t.course} (${t.course_number})` : t.course;
    return el("div", { className: "entry" }, [
      entryHeader(`${t.role} — ${courseTitle}`, t.org, t.dates),
    ]);
  });
}

function renderProjects(data) {
  return renderSimpleList("Academic Projects", data.projects, (p) => {
    const entry = el("div", { className: "entry" }, [
      entryHeader(p.title, p.org, p.dates),
    ]);
    if (p.description) entry.appendChild(el("p", { className: "entry-details", text: p.description }));
    const links = Object.entries(p.links || {}).filter(([, url]) => url);
    if (links.length) {
      const linksWrap = el("div", { className: "pub-links" });
      for (const [key, url] of links) {
        linksWrap.appendChild(el("a", { text: linkLabel(key) }).also(a => {
          a.href = url;
          a.target = "_blank";
          a.rel = "noopener";
        }));
      }
      entry.appendChild(linksWrap);
    }
    return entry;
  });
}

function renderOtherExperience(data) {
  return renderSimpleList("Other Experience", data.other_experience, (o) => {
    const entry = el("div", { className: "entry" }, [
      entryHeader(o.role, o.org, o.dates),
    ]);
    if (o.description) entry.appendChild(el("p", { className: "entry-details", text: o.description }));
    return entry;
  });
}

// Publications lead (right after the bio) since this page has no news
// section to put them below -- publications are the most important thing.
const SECTION_RENDERERS = [
  renderPublications,
  renderEducation,
  renderHonors,
  renderResearchExperience,
  renderTeaching,
  renderProjects,
  renderOtherExperience,
];

async function main() {
  let data;
  try {
    const res = await fetch(DATA_URL, { cache: "no-cache" });
    data = await res.json();
  } catch (err) {
    const isFileProtocol = location.protocol === "file:";
    document.getElementById("name").textContent = isFileProtocol
      ? "Can't load data.json when opened as a local file"
      : "Failed to load data.json";
    document.getElementById("tagline").textContent = isFileProtocol
      ? "Browsers block fetch() for file:// pages. Run a local server instead, e.g. `python3 -m http.server` in this folder, then open http://localhost:8000/."
      : "";
    console.error(err);
    return;
  }

  renderHeader(data);

  const main = document.getElementById("sections");
  for (const renderer of SECTION_RENDERERS) {
    const node = renderer(data);
    if (node) main.appendChild(node);
  }
}

main();
