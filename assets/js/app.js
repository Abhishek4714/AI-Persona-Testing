
const state = {
  personas: [],
  actions: [],
};

async function loadData() {
  const pj = await fetch("./data/simpersonas.json").then(r=>r.json());
  const csvText = await fetch("./data/simpersona_actions.csv").then(r=>r.text());
  const parsed = Papa.parse(csvText, {header:true,dynamicTyping:true});
  state.personas = pj;
  state.actions = parsed.data.filter(r => r.persona_id); // drop trailing empty row
}

function groupBy(arr, key) {
  return arr.reduce((acc, cur) => {
    const k = cur[key];
    (acc[k] ||= []).push(cur);
    return acc;
  }, {});
}

function avg(nums){ return nums.length? nums.reduce((a,b)=>a+b,0)/nums.length : 0; }

function renderPersonaCards() {
  const wrap = document.querySelector("#persona-cards");
  wrap.innerHTML = "";
  state.personas.forEach(p => {
    const card = document.createElement("div");
    card.className = "persona-card";
    const img = document.createElement("img");
    img.src = `./data/persona_cards/${p.id}.png`;
    img.alt = p.label;
    const body = document.createElement("div");
    body.style.padding = "12px 12px 14px 12px";
    body.innerHTML = `
      <div class="badge">${p.label}</div>
      <div class="kv"><div>Age</div><div>${p.demographics.age}</div></div>
      <div class="kv"><div>Occupation</div><div>${p.demographics.occupation}</div></div>
      <div class="kv"><div>Tech comfort</div><div>${p.demographics.tech_comfort}</div></div>
      <div class="small">${p.behavior.description}</div>
    `;
    card.appendChild(img);
    card.appendChild(body);
    wrap.appendChild(card);
  });
}

function renderTables() {
  const tbody = document.querySelector("#logs-body");
  tbody.innerHTML = "";
  state.actions.slice(0,200).forEach(r => {
    const tr = document.createElement("tr");
    tr.innerHTML = `
      <td>${r.persona_label}</td>
      <td>${r.task_label}</td>
      <td>${r.steps_count}</td>
      <td>${r.errors}</td>
      <td>${r.success ? "Yes" : "No"}</td>
      <td><span class="small">${r.actions}</span></td>
    `;
    tbody.appendChild(tr);
  });
}

let charts = {};
function renderCharts() {
  // Destroy if re-render
  Object.values(charts).forEach(c => c.destroy && c.destroy());

  // Average steps per persona per task (grouped)
  const tasks = [...new Set(state.actions.map(r=>r.task_label))];
  const personas = [...new Set(state.actions.map(r=>r.persona_label))];

  const datasets1 = personas.map(pl => {
    return {
      label: pl,
      data: tasks.map(tl => {
        const subset = state.actions.filter(r=>r.persona_label===pl && r.task_label===tl);
        return +(avg(subset.map(s=>Number(s.steps_count)||0)).toFixed(2));
      }),
    };
  });
  charts.steps = new Chart(document.getElementById("chart-steps"), {
    type: "bar",
    data: { labels: tasks, datasets: datasets1 },
    options: { responsive:true, plugins:{ legend:{position:"bottom"}, title:{display:true, text:"Average Steps per Persona per Task"}}}
  });

  // Average errors per persona
  const avgErr = personas.map(pl => {
    const subset = state.actions.filter(r=>r.persona_label===pl);
    return +(avg(subset.map(s=>Number(s.errors)||0)).toFixed(2));
  });
  charts.errors = new Chart(document.getElementById("chart-errors"), {
    type: "bar",
    data: { labels: personas, datasets: [{ label: "Errors", data: avgErr }] },
    options: { responsive:true, plugins:{ legend:{display:false}, title:{display:true, text:"Average Errors per Persona (across tasks)"}}}
  });

  // Success rate by persona
  const succPct = personas.map(pl => {
    const subset = state.actions.filter(r=>r.persona_label===pl);
    const rate = 100 * (avg(subset.map(s=>Number(s.success)||0)));
    return +rate.toFixed(1);
  });
  charts.success = new Chart(document.getElementById("chart-success"), {
    type: "bar",
    data: { labels: personas, datasets: [{ label: "Success Rate (%)", data: succPct }] },
    options: { responsive:true, plugins:{ legend:{display:false}, title:{display:true, text:"Success Rate by Persona (%)"}}}
  });
}

function wireTabs() {
  const links = document.querySelectorAll(".nav a");
  links.forEach(a => a.addEventListener("click", (e)=>{
    e.preventDefault();
    const target = a.getAttribute("href").replace("#","");
    document.querySelectorAll(".view").forEach(v => v.style.display="none");
    document.getElementById(target).style.display="block";
    links.forEach(l => l.classList.remove("active"));
    a.classList.add("active");
  }));
}

async function main() {
  wireTabs();
  await loadData();
  renderPersonaCards();
  renderTables();
  renderCharts();
  // default view
  document.querySelector('.nav a[href="#dashboard"]').click();
}
document.addEventListener("DOMContentLoaded", main);
