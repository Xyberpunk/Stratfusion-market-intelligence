const state = {
  marketData: [],
  lastPipeline: null,
};

const els = {
  gatewayUrl: document.querySelector("#gatewayUrl"),
  checkStatus: document.querySelector("#checkStatus"),
  runPipeline: document.querySelector("#runPipeline"),
  loadNews: document.querySelector("#loadNews"),
  loadStrategies: document.querySelector("#loadStrategies"),
  symbol: document.querySelector("#symbol"),
  capital: document.querySelector("#capital"),
  risk: document.querySelector("#risk"),
  headline: document.querySelector("#headline"),
  gatewayStatus: document.querySelector("#gatewayStatus"),
  adaptiveStatus: document.querySelector("#adaptiveStatus"),
  algoStatus: document.querySelector("#algoStatus"),
  newsStatus: document.querySelector("#newsStatus"),
  newsTable: document.querySelector("#newsTable"),
  strategyTable: document.querySelector("#strategyTable"),
  weightsList: document.querySelector("#weightsList"),
  sentimentMetric: document.querySelector("#sentimentMetric"),
  regimeMetric: document.querySelector("#regimeMetric"),
  anomalyMetric: document.querySelector("#anomalyMetric"),
  bullishMetric: document.querySelector("#bullishMetric"),
  bearishMetric: document.querySelector("#bearishMetric"),
  actionMetric: document.querySelector("#actionMetric"),
  riskMetric: document.querySelector("#riskMetric"),
  entryPrice: document.querySelector("#entryPrice"),
  stopLoss: document.querySelector("#stopLoss"),
  targetPrice: document.querySelector("#targetPrice"),
  riskReward: document.querySelector("#riskReward"),
  explanation: document.querySelector("#explanation"),
  canvas: document.querySelector("#marketCanvas"),
};

document.querySelectorAll(".tab").forEach((button) => {
  button.addEventListener("click", () => {
    document.querySelectorAll(".tab").forEach((tab) => tab.classList.remove("active"));
    document.querySelectorAll(".section").forEach((section) => section.classList.remove("active"));
    button.classList.add("active");
    document.querySelector(`#${button.dataset.section}Section`).classList.add("active");
  });
});

els.checkStatus.addEventListener("click", checkStatus);
els.loadNews.addEventListener("click", loadNews);
els.loadStrategies.addEventListener("click", loadStrategies);
els.runPipeline.addEventListener("click", runPipeline);

function gateway() {
  return els.gatewayUrl.value.replace(/\/$/, "");
}

async function request(path, options = {}) {
  const response = await fetch(`${gateway()}${path}`, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });
  if (!response.ok) {
    const text = await response.text();
    throw new Error(`${response.status}: ${text}`);
  }
  return response.json();
}

async function checkStatus() {
  try {
    const status = await request("/platform/status");
    els.gatewayStatus.textContent = status.gateway;
    els.adaptiveStatus.textContent = status.adaptive_ai;
    els.algoStatus.textContent = status.algo_lab;
    els.newsStatus.textContent = status.scraper_news_store;
  } catch (error) {
    els.gatewayStatus.textContent = "unavailable";
    els.adaptiveStatus.textContent = "unknown";
    els.algoStatus.textContent = "unknown";
    els.newsStatus.textContent = "unknown";
  }
}

async function loadNews() {
  try {
    const symbol = encodeURIComponent(els.symbol.value.trim());
    const news = await request(`/news/latest?symbol=${symbol}&limit=20`);
    renderNews(news);
  } catch (error) {
    renderNews([]);
  }
}

async function loadStrategies() {
  try {
    const strategies = await request("/strategies");
    els.strategyTable.innerHTML = strategies.map((item) => `
      <tr>
        <td>${escapeHtml(item.name)}</td>
        <td>Available</td>
        <td>--</td>
        <td>--</td>
        <td>${escapeHtml(item.category)}</td>
      </tr>
    `).join("");
  } catch (error) {
    els.strategyTable.innerHTML = `<tr><td colspan="5">Strategy service unavailable: ${escapeHtml(error.message)}</td></tr>`;
  }
}

async function runPipeline() {
  const payload = await buildPayload();
  drawMarket(state.marketData);
  try {
    const result = await request("/api/pipeline/run", {
      method: "POST",
      body: JSON.stringify(payload),
    });
    state.lastPipeline = result;
    renderPipeline(result);
  } catch (error) {
    els.explanation.textContent = `Pipeline unavailable: ${error.message}`;
  }
}

async function buildPayload() {
  const symbol = els.symbol.value.trim().toUpperCase() || "INFY";
  state.marketData = await loadMarketData(symbol);
  const now = new Date().toISOString();
  return {
    symbol,
    market_data: state.marketData,
    sentiment_events: [
      {
        symbol,
        timestamp: now,
        text: els.headline.value.trim(),
        source: "dashboard",
      },
    ],
    options_chain: [
      {
        symbol,
        timestamp: now,
        pcr: 1.16,
        max_pain: state.marketData[state.marketData.length - 1].close * 0.98,
        iv: 23.4,
        call_oi_change: 820000,
        put_oi_change: 1180000,
        options_volume_call: 450000,
        options_volume_put: 610000,
      },
    ],
    benchmark_data: generateMarketData("NIFTY", 0.18),
    sector_data: generateMarketData("IT", 0.22),
    capital: Number(els.capital.value || 1000000),
    risk_per_trade: Number(els.risk.value || 0.01),
  };
}

async function loadMarketData(symbol) {
  try {
    const result = await request(`/api/symbol/${encodeURIComponent(symbol)}/market-data?timeframe=1m&points=90`);
    if (Array.isArray(result.bars) && result.bars.length) {
      return result.bars;
    }
  } catch (error) {
    // Keep the dashboard usable when live NSEPython data is unavailable.
  }
  return generateMarketData(symbol, 0.32, "dashboard_fallback");
}

function generateMarketData(symbol, drift = 0.32, source = "dashboard_fallback") {
  const rows = [];
  const start = new Date();
  start.setDate(start.getDate() - 89);
  let close = symbol === "NIFTY" ? 22000 : symbol === "IT" ? 35000 : 1500;
  for (let i = 0; i < 90; i += 1) {
    const wave = Math.sin(i / 6) * 0.45;
    const shock = i === 72 ? -1.8 : i === 81 ? 2.2 : 0;
    const change = drift + wave + shock;
    const open = close;
    close = Math.max(10, close + change);
    const high = Math.max(open, close) + 1.2 + Math.abs(wave);
    const low = Math.min(open, close) - 1.1 - Math.abs(wave);
    const timestamp = new Date(start);
    timestamp.setDate(start.getDate() + i);
    rows.push({
      symbol,
      timestamp: timestamp.toISOString(),
      open,
      high,
      low,
      close,
      volume: 120000 + i * 1700 + (i === 88 ? 260000 : 0),
      source,
    });
  }
  return rows;
}

function renderPipeline(result) {
  const sentiment = result.sentiment_outputs?.[0];
  const guidance = result.trading_guidance?.guidance || result.trading_guidance;
  const ensemble = guidance?.ensemble || {};
  const risk = guidance?.risk || {};
  els.sentimentMetric.textContent = sentiment ? `${sentiment.sentiment} ${percent(sentiment.confidence)}` : "neutral";
  els.regimeMetric.textContent = result.regime?.regime || "unknown";
  els.anomalyMetric.textContent = String(result.anomalies?.length || 0);
  els.bullishMetric.textContent = percent(ensemble.bullish_probability);
  els.bearishMetric.textContent = percent(ensemble.bearish_probability);
  els.actionMetric.textContent = guidance?.final_action || ensemble.suggested_action || "--";
  els.riskMetric.textContent = risk.risk_level || ensemble.risk_level || "--";
  els.entryPrice.textContent = number(risk.entry_price);
  els.stopLoss.textContent = number(risk.stop_loss);
  els.targetPrice.textContent = number(risk.target);
  els.riskReward.textContent = number(risk.risk_reward_ratio);
  els.explanation.textContent = guidance?.final_explanation || result.explanation;
  const quality = result.feature_vector?.quality_report;
  if (quality) {
    els.explanation.textContent += ` Feature quality: ${percent(quality.quality_score)}${quality.warnings?.length ? ` (${quality.warnings.slice(0, 2).join("; ")})` : ""}.`;
  }
  renderWeights(result.weighting?.weights || {});
  renderStrategies(ensemble.strategy_breakdown || []);
  renderNews(result.latest_news || []);
}

function renderWeights(weights) {
  const entries = Object.entries(weights).sort((a, b) => b[1] - a[1]);
  els.weightsList.innerHTML = entries.map(([name, value]) => `
    <div class="weight-row">
      <span>${escapeHtml(name)}</span>
      <span class="bar"><span style="width:${Math.round(value * 100)}%"></span></span>
      <strong>${percent(value)}</strong>
    </div>
  `).join("") || "<p>No weights returned.</p>";
}

function renderStrategies(rows) {
  els.strategyTable.innerHTML = rows.map((row) => `
    <tr>
      <td>${escapeHtml(row.strategy_name)}</td>
      <td>${escapeHtml(row.signal)}</td>
      <td>${percent(row.adjusted_weight ?? row.raw_weight)}</td>
      <td>${percent(row.confidence)}</td>
      <td>${escapeHtml(row.reason)}</td>
    </tr>
  `).join("") || "<tr><td colspan=\"5\">No strategy breakdown yet.</td></tr>";
}

function renderNews(news) {
  els.newsTable.innerHTML = news.map((item) => `
    <tr>
      <td>${escapeHtml(item.source || "news")}</td>
      <td><a href="${escapeAttr(item.url || "#")}" target="_blank" rel="noreferrer">${escapeHtml(item.title || "")}</a></td>
      <td>${escapeHtml(formatTime(item.published_at || item.scraped_at))}</td>
      <td>${escapeHtml(item.sentiment || "pending")}</td>
    </tr>
  `).join("") || "<tr><td colspan=\"4\">No news yet. Run the intelligence pipeline or enable scraper MySQL for live ingestion data.</td></tr>";
}

function drawMarket(rows) {
  const canvas = els.canvas;
  const ctx = canvas.getContext("2d");
  ctx.clearRect(0, 0, canvas.width, canvas.height);
  ctx.fillStyle = "#10242a";
  ctx.fillRect(0, 0, canvas.width, canvas.height);
  if (!rows.length) return;
  const closes = rows.map((row) => row.close);
  const min = Math.min(...closes);
  const max = Math.max(...closes);
  const pad = 26;
  ctx.strokeStyle = "rgba(255,255,255,0.12)";
  ctx.lineWidth = 1;
  for (let i = 0; i < 5; i += 1) {
    const y = pad + (i * (canvas.height - pad * 2)) / 4;
    ctx.beginPath();
    ctx.moveTo(pad, y);
    ctx.lineTo(canvas.width - pad, y);
    ctx.stroke();
  }
  ctx.strokeStyle = "#2dd4bf";
  ctx.lineWidth = 3;
  ctx.beginPath();
  rows.forEach((row, index) => {
    const x = pad + (index * (canvas.width - pad * 2)) / (rows.length - 1);
    const y = canvas.height - pad - ((row.close - min) / Math.max(max - min, 1)) * (canvas.height - pad * 2);
    if (index === 0) ctx.moveTo(x, y);
    else ctx.lineTo(x, y);
  });
  ctx.stroke();
  ctx.fillStyle = "#e6fffb";
  ctx.font = "20px Inter, sans-serif";
  const sourceLabel = String(rows[0].source || "market").replaceAll("_", " ");
  ctx.fillText(`${rows[0].symbol} ${sourceLabel} OHLCV path`, pad, 34);
}

function percent(value) {
  if (value === undefined || value === null || Number.isNaN(Number(value))) return "--";
  return `${Math.round(Number(value) * 100)}%`;
}

function number(value) {
  if (value === undefined || value === null || Number.isNaN(Number(value))) return "--";
  return Number(value).toLocaleString(undefined, { maximumFractionDigits: 2 });
}

function formatTime(value) {
  if (!value) return "--";
  return new Date(value).toLocaleString();
}

function escapeHtml(value) {
  return String(value).replace(/[&<>"']/g, (char) => ({
    "&": "&amp;",
    "<": "&lt;",
    ">": "&gt;",
    '"': "&quot;",
    "'": "&#39;",
  }[char]));
}

function escapeAttr(value) {
  return escapeHtml(value).replace(/`/g, "&#96;");
}

state.marketData = generateMarketData("INFY");
drawMarket(state.marketData);
loadMarketData("INFY").then((rows) => {
  state.marketData = rows;
  drawMarket(rows);
});
checkStatus();
