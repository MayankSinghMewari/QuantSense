import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid, AreaChart, Area } from 'recharts';
import './App.css';

const API = 'http://localhost:8000';

const STOCKS = [
  "HDFCBANK.NS", "ICICIBANK.NS", "SBIN.NS", "KOTAKBANK.NS", "AXISBANK.NS",
  "TCS.NS", "INFY.NS", "WIPRO.NS", "HCLTECH.NS", "TECHM.NS",
  "RELIANCE.NS", "ONGC.NS", "POWERGRID.NS", "NTPC.NS", "BPCL.NS",
  "HINDUNILVR.NS", "ITC.NS", "NESTLEIND.NS", "BRITANNIA.NS", "DABUR.NS",
  "MARUTI.NS", "BAJAJ-AUTO.NS", "EICHERMOT.NS", "HEROMOTOCO.NS",
  "SUNPHARMA.NS", "DRREDDY.NS", "CIPLA.NS", "DIVISLAB.NS", "APOLLOHOSP.NS",
  "MPHASIS.NS", "LTIM.NS", "PERSISTENT.NS", "COFORGE.NS", "TATAELXSI.NS",
  "BAJAJFINSV.NS", "MUTHOOTFIN.NS", "CHOLAFIN.NS", "MANAPPURAM.NS", "SBILIFE.NS",
  "MOTHERSON.NS", "BALKRISIND.NS", "BHARATFORG.NS", "ESCORTS.NS", "TIINDIA.NS",
  "LT.NS", "ADANIPORTS.NS", "IRCTC.NS", "BEL.NS", "HAL.NS",
  "PIDILITIND.NS", "AARTIIND.NS", "DEEPAKNTR.NS", "TATACHEM.NS", "GNFC.NS",
  "DLF.NS", "GODREJPROP.NS", "ULTRACEMCO.NS", "AMBUJACEM.NS", "SHREECEM.NS",
  "TRENT.NS", "DMART.NS", "NYKAA.NS", "TITAN.NS", "JUBLFOOD.NS",
  "DATAPATTNS.NS", "COCHINSHIP.NS", "MAZDOCK.NS",
  "ADANIGREEN.NS", "TATAPOWER.NS", "CESC.NS", "SJVN.NS", "NHPC.NS",
  "PAYTM.NS", "POLICYBZR.NS", "NAUKRI.NS", "INDIAMART.NS",
  "NAVINFLUOR.NS", "FINEORG.NS", "VINATIORGA.NS", "SUDARSCHEM.NS",
  "BANKBARODA.NS", "CANBK.NS", "FEDERALBNK.NS", "AUBANK.NS", "IDFCFIRSTB.NS",
  "MAXHEALTH.NS", "FORTIS.NS", "METROPOLIS.NS", "THYROCARE.NS",
  "DELHIVERY.NS", "BLUEDART.NS", "INDIGO.NS", "IRFC.NS",
  "BAJFINANCE.NS", "HDFCLIFE.NS", "ICICIPRULI.NS", "ICICIGI.NS", "LTTS.NS",
];

const GLOBAL_INDICES = [
  "^GSPC", "^DJI", "^IXIC", "^N225",
  "^NSEI", "^BSESN", "GC=F", "CL=F", "USDINR=X"
];

const ALL = { "Indian Stocks": STOCKS, "Global Indices": GLOBAL_INDICES };

function SignalBadge({ signal }) {
  const colors = { BUY: '#00e676', SELL: '#ff1744', HOLD: '#ff9100' };
  return (
    <span style={{
      background: `${colors[signal] || '#666'}22`,
      color: colors[signal] || '#666',
      border: `1px solid ${colors[signal]}`,
      padding: '2px 10px',
      borderRadius: '6px',
      fontWeight: '800',
      fontSize: '11px',
      textTransform: 'uppercase'
    }}>
      {signal}
    </span>
  );
}

function StockCard({ ticker, onSelect, selected }) {
  const [data, setData] = useState(null);

  useEffect(() => {
    axios.get(`${API}/signal/${ticker}`).then(r => setData(r.data)).catch(() => { });
  }, [ticker]);

  if (!data) return <div className="card loading"><p>{ticker}</p></div>;

  return (
    <div className={`card ${selected ? 'selected' : ''}`} onClick={() => onSelect(ticker)}>
      <div className="card-header">
        <span className="ticker-name">{ticker.replace('.NS', '')}</span>
        <SignalBadge signal={data.signal} />
      </div>
      <div className="card-body">
        <div className="price-row">
          <span className="price">₹{data.latest_close.toLocaleString()}</span>
          <span className={`risk-tag ${data.risk.toLowerCase()}`}>{data.risk} RISK</span>
        </div>
        <div className="mini-metrics">
          <span>RSI: <b>{data.rsi}</b></span>
          <span>Conf: <b>{data.confidence}%</b></span>
        </div>
        <div className="sentiment-container">
          <div className="sentiment-track">
            <div style={{
              width: `${(data.sentiment + 1) / 2 * 100}%`,
              background: data.sentiment > 0 ? '#00e676' : '#ff1744'
            }} className="sentiment-fill" />
          </div>
        </div>
      </div>
    </div>
  );
}

function DetailPanel({ ticker }) {
  const [signal, setSignal] = useState(null);
  const [history, setHistory] = useState([]);

  useEffect(() => {
    if (!ticker) return;
    setSignal(null);
    axios.get(`${API}/signal/${ticker}`).then(r => setSignal(r.data)).catch(() => { });
  }, [ticker]);
  useEffect(() => {
    if (!ticker) return;
    axios.get(`${API}/price-history/${ticker}?days=60`)
      .then(r => setHistory(r.data.data))
      .catch(() => { });
  }, [ticker]);

  if (!ticker) return <div className="detail-panel empty"><div className="empty-state">Select a Ticker to Analyze</div></div>;
  if (!signal) return <div className="detail-panel loading-state">Fetching Real-time Intelligence...</div>;

  const chartData = [
    { name: 'BB Lower', value: signal.bb_lower, color: '#ff9100' },
    { name: 'MA 50', value: signal.ma_50, color: '#2979ff' },
    { name: 'MA 20', value: signal.ma_20, color: '#f50057' },
    { name: 'Price', value: signal.latest_close, color: '#00e676' },
    { name: 'BB Upper', value: signal.bb_upper, color: '#aa00ff' },
  ];

  const prices = history.map(d => d.close).filter(Boolean);
  const minVal = prices.length ? Math.min(...prices) * 0.995 : 'auto';
  const maxVal = prices.length ? Math.max(...prices) * 1.005 : 'auto';

  return (
    <div className="detail-panel">
      <div className="detail-header">
        <div>
          <h1>{ticker}</h1>
          <p className="timestamp">Updated: {new Date().toLocaleTimeString()}</p>
        </div>
        <div className="main-signal-box">
          <label>Ensemble Signal</label>
          <SignalBadge signal={signal.signal} />
        </div>
      </div>

      <div className="stats-grid">
        <div className="stat-card">
          <label>AI Confidence</label>
          <div className="val">{signal.confidence}%</div>
          <div className="progress-mini"><div style={{ width: `${signal.confidence}%` }} /></div>
        </div>
        <div className="stat-card">
          <label>Technical RSI</label>
          <div className="val">{signal.rsi}</div>
          <small>{signal.rsi > 70 ? 'Overbought' : signal.rsi < 30 ? 'Oversold' : 'Neutral'}</small>
        </div>
        <div className="stat-card">
          <label>Quant Score</label>
          <div className="val" style={{ color: '#2979ff' }}>{signal.qs_score}</div>
        </div>
        <div className="stat-card">
          <label>Market Volatility</label>
          <div className="val">{signal.volatility}</div>
        </div>
      </div>

      <div className="chart-section">
        <div className="chart-tabs">
          <span className="chart-title">📈 Price Chart — Last 60 Days</span>
          <div className="chart-legend">
            {chartData.map(d => (
              <div key={d.name} className="legend-item">
                <span className="dot" style={{ background: d.color }} />
                <span className="label">{d.name}</span>
                <span className="price">₹{d.value?.toFixed(2)}</span>
              </div>
            ))}
          </div>
        </div>

        <ResponsiveContainer width="100%" height={300}>
          <LineChart data={history} margin={{ top: 5, right: 20, bottom: 5, left: 10 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#ffffff08" vertical={false} />
            <XAxis
              dataKey="date"
              stroke="#333"
              tick={{ fill: '#444', fontSize: 10 }}
              interval={9}
            />
            <YAxis
              stroke="#333"
              tick={{ fill: '#444', fontSize: 10 }}
              orientation="right"
              domain={[minVal, maxVal]}
            />
            <Tooltip
              contentStyle={{ background: '#0d0d1a', border: '1px solid #2a2a4a', borderRadius: '10px' }}
              labelStyle={{ color: '#888', fontSize: '11px' }}
              itemStyle={{ fontSize: '12px' }}
              formatter={(v, name) => [`₹${v?.toFixed(2)}`, name]}
            />
            <Line type="monotone" dataKey="close" stroke="#00e676" strokeWidth={2} dot={false} name="Price" />
            <Line type="monotone" dataKey="ma_20" stroke="#ff9100" strokeWidth={1.5} dot={false} strokeDasharray="4 2" name="MA 20" />
            <Line type="monotone" dataKey="ma_50" stroke="#2979ff" strokeWidth={1.5} dot={false} strokeDasharray="4 2" name="MA 50" />
            <Line type="monotone" dataKey="bb_upper" stroke="#aa00ff" strokeWidth={1} dot={false} strokeDasharray="2 3" name="BB Upper" />
            <Line type="monotone" dataKey="bb_lower" stroke="#ff1744" strokeWidth={1} dot={false} strokeDasharray="2 3" name="BB Lower" />
          </LineChart>
        </ResponsiveContainer>

        <ResponsiveContainer width="100%" height={80}>
          <AreaChart data={history} margin={{ top: 5, right: 20, bottom: 0, left: 10 }}>
            <defs>
              <linearGradient id="volGrad" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#00b0ff" stopOpacity={0.3} />
                <stop offset="95%" stopColor="#00b0ff" stopOpacity={0} />
              </linearGradient>
            </defs>
            <XAxis dataKey="date" hide />
            <YAxis hide domain={['auto', 'auto']} />
            <Tooltip
              contentStyle={{ background: '#0d0d1a', border: '1px solid #2a2a4a', borderRadius: '10px' }}
              formatter={(v) => [v?.toLocaleString(), 'Volume']}
            />
            <Area type="monotone" dataKey="volume" stroke="#00b0ff" fill="url(#volGrad)" strokeWidth={1} />
          </AreaChart>
        </ResponsiveContainer>
        <div style={{ textAlign: 'center', fontSize: '10px', color: '#333', marginTop: '4px' }}>VOLUME</div>
      </div>

      <div className="intelligence-grid">
        <div className="intel-card">
          <h4>Model Breakdown</h4>
          <div className="intel-row">
            <span>XGBoost Prediction</span>
            <span style={{ color: signal.xgb_signal === 'BUY' ? '#00e676' : '#ff1744' }}>{signal.xgb_signal}</span>
          </div>
          <div className="intel-row">
            <span>XGB Confidence</span>
            <span>{signal.xgb_confidence}%</span>
          </div>
          <div className="intel-row">
            <span>Sentiment Overlay</span>
            <span style={{ color: signal.sentiment > 0 ? '#00e676' : '#ff1744' }}>{signal.sentiment}</span>
          </div>
        </div>
        <div className="intel-card">
          <h4>Risk Management</h4>
          <div className="intel-row">
            <span>Risk Profile</span>
            <span className={`risk-${signal.risk.toLowerCase()}`}>{signal.risk}</span>
          </div>
          <div className="intel-row">
            <span>MA 20 / 50 Cross</span>
            <span>{signal.ma_20 > signal.ma_50 ? 'Bullish' : 'Bearish'}</span>
          </div>
        </div>
      </div>
    </div>
  );
}

export default function App() {
  const [selected, setSelected] = useState(null);
  const [search, setSearch] = useState('');
  const [category, setCategory] = useState('Indian Stocks');

  const filtered = ALL[category].filter(t => t.toLowerCase().includes(search.toLowerCase()));

  return (
    <div className="app">
      <aside className="sidebar">
        <div className="brand">
          <div className="logo">QS</div>
          <div>
            <h2>QuantSense</h2>
            <p>Intelligence v3.0</p>
          </div>
        </div>

        <div className="filter-box">
          <select value={category} onChange={e => { setCategory(e.target.value); setSelected(null); }}>
            {Object.keys(ALL).map(k => <option key={k} value={k}>{k}</option>)}
          </select>
          <input
            type="text"
            placeholder="Search Assets..."
            value={search}
            onChange={e => setSearch(e.target.value)}
          />
        </div>

        <div className="stock-list">
          {filtered.map(t => (
            <StockCard key={t} ticker={t} onSelect={setSelected} selected={selected === t} />
          ))}
        </div>
      </aside>

      <main className="content">
        <DetailPanel ticker={selected} />
      </main>
    </div>
  );
}