import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer } from 'recharts';
import './App.css';

const API = 'http://localhost:8000';

const STOCKS = [
  'HDFCBANK.NS', 'ICICIBANK.NS', 'TCS.NS', 'INFY.NS',
  'WIPRO.NS', 'AXISBANK.NS', 'KOTAKBANK.NS', 'TECHM.NS',
  'HCLTECH.NS', 'SBIN.NS'
];

function SignalBadge({ signal }) {
  const colors = { BUY: '#00c853', SELL: '#d50000', HOLD: '#ff6d00' };
  return (
    <span style={{
      background: colors[signal] || '#666',
      color: 'white',
      padding: '4px 12px',
      borderRadius: '20px',
      fontWeight: 'bold',
      fontSize: '12px'
    }}>
      {signal}
    </span>
  );
}

function StockCard({ ticker, onSelect, selected }) {
  const [data, setData] = useState(null);

  useEffect(() => {
    axios.get(`${API}/signal/${ticker}`)
      .then(r => setData(r.data))
      .catch(() => {});
  }, [ticker]);

  if (!data) return (
    <div className="card loading" onClick={() => onSelect(ticker)}>
      <p>{ticker}</p><p>Loading...</p>
    </div>
  );

  return (
    <div className={`card ${selected ? 'selected' : ''}`} onClick={() => onSelect(ticker)}>
      <div className="card-header">
        <h3>{ticker.replace('.NS', '')}</h3>
        <SignalBadge signal={data.signal} />
      </div>
      <p className="price">₹{data.latest_close}</p>
      <div className="metrics">
        <span>Conf: {data.confidence}%</span>
        <span>RSI: {data.rsi}</span>
        <span>Risk: {data.risk}</span>
      </div>
      <div className="sentiment-bar">
        <div style={{
          width: `${(data.sentiment + 1) / 2 * 100}%`,
          background: data.sentiment > 0 ? '#00c853' : '#d50000',
          height: '4px', borderRadius: '2px'
        }} />
      </div>
      <small>Sentiment: {data.sentiment}</small>
    </div>
  );
}

function DetailPanel({ ticker }) {
  const [signal, setSignal] = useState(null);

  useEffect(() => {
    if (!ticker) return;
    axios.get(`${API}/signal/${ticker}`)
      .then(r => setSignal(r.data))
      .catch(() => {});
  }, [ticker]);

  if (!ticker) return (
    <div className="detail-panel empty">
      <p>Select a stock to see details</p>
    </div>
  );

  if (!signal) return <div className="detail-panel"><p>Loading...</p></div>;

  const chartData = [
    { name: 'MA20', value: signal.ma_20 },
    { name: 'Close', value: signal.latest_close },
  ];

  return (
    <div className="detail-panel">
      <h2>{ticker} — <SignalBadge signal={signal.signal} /></h2>
      <div className="detail-grid">
        <div className="detail-item">
          <label>Confidence</label>
          <value>{signal.confidence}%</value>
        </div>
        <div className="detail-item">
          <label>Risk</label>
          <value>{signal.risk}</value>
        </div>
        <div className="detail-item">
          <label>RSI</label>
          <value>{signal.rsi}</value>
        </div>
        <div className="detail-item">
          <label>QS Score</label>
          <value>{signal.qs_score}</value>
        </div>
        <div className="detail-item">
          <label>Sentiment</label>
          <value>{signal.sentiment}</value>
        </div>
        <div className="detail-item">
          <label>MA 20</label>
          <value>₹{signal.ma_20}</value>
        </div>
      </div>
      <ResponsiveContainer width="100%" height={200}>
        <LineChart data={chartData}>
          <XAxis dataKey="name" stroke="#888" />
          <YAxis stroke="#888" domain={['auto', 'auto']} />
          <Tooltip />
          <Line type="monotone" dataKey="value" stroke="#00c853" strokeWidth={2} dot={true} />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}

export default function App() {
  const [selected, setSelected] = useState(null);

  return (
    <div className="app">
      <header className="header">
        <h1>⚡ QuantSense</h1>
        <p>AI-Powered Stock Signal Platform</p>
      </header>
      <div className="main">
        <div className="grid">
          {STOCKS.map(t => (
            <StockCard
              key={t}
              ticker={t}
              onSelect={setSelected}
              selected={selected === t}
            />
          ))}
        </div>
        <DetailPanel ticker={selected} />
      </div>
    </div>
  );
}