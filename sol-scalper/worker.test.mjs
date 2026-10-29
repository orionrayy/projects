import test from 'node:test';
import assert from 'node:assert/strict';
import { ema, rsi, atr, scoreMarket } from './worker.mjs';

test('EMA returns null until enough observations exist', () => {
  assert.equal(ema([1, 2], 3), null);
  assert.ok(ema([1, 2, 3, 4], 3) > 2);
});

test('RSI handles flat, rising, and falling series', () => {
  assert.equal(rsi(Array(20).fill(12), 14), 50);
  assert.equal(rsi(Array.from({length: 20}, (_, i) => i + 1), 14), 100);
  assert.equal(rsi(Array.from({length: 20}, (_, i) => 20 - i), 14), 0);
});

test('ATR produces positive volatility from candle data', () => {
  const candles = Array.from({length: 20}, (_, i) => ({high: 101 + i, low: 99 + i, close: 100 + i}));
  assert.ok(atr(candles, 14) > 0);
  assert.equal(atr(candles.slice(0, 10), 14), null);
});

const goodM = {ema9: 102, ema21: 100, close: 103, rsi14: 58, volumeRatio: 1.5, atrPct: 0.4, atr14: 0.4, closedAt: Date.now() - 10000};
const goodBook = {bid: 102, ask: 102.05, mid: 102.025, spreadBps: 4.9, bidNotionalIdrTop10: 10000, askNotionalIdrTop10: 7000, imbalance: 0.17};
const goodFlow = {buyQuoteIdr: 9000, sellQuoteIdr: 6000, imbalance: 0.2, sampleCount: 80};

test('qualified conditions score as watch-only; execution remains off', () => {
  const out = scoreMarket({m1: goodM, m5: goodM, m15: goodM, book: goodBook, flow: goodFlow, now: Date.now()});
  assert.equal(out.signal, 'BUY_SETUP_WATCH_ONLY');
  assert.equal(out.execution.enabled, false);
  assert.equal(out.execution.ordersSubmitted, false);
  assert.ok(out.blockers.includes('LIVE_EXECUTION_DISABLED'));
});

test('wide spread blocks an otherwise strong setup', () => {
  const out = scoreMarket({m1: goodM, m5: goodM, m15: goodM, book: {...goodBook, spreadBps: 25}, flow: goodFlow, now: Date.now()});
  assert.notEqual(out.signal, 'BUY_SETUP_WATCH_ONLY');
  assert.ok(out.blockers.includes('SPREAD_TOO_WIDE'));
});

test('stale market data never qualifies', () => {
  const staleM1 = {...goodM, closedAt: Date.now() - 500000};
  const out = scoreMarket({m1: staleM1, m5: goodM, m15: goodM, book: goodBook, flow: goodFlow, now: Date.now()});
  assert.notEqual(out.signal, 'BUY_SETUP_WATCH_ONLY');
  assert.ok(out.blockers.includes('DATA_STALE'));
});

test('missing critical close/EMA data never qualifies', () => {
  const malformed = {...goodM, close: null};
  const out = scoreMarket({m1: malformed, m5: goodM, m15: goodM, book: goodBook, flow: goodFlow, now: Date.now()});
  assert.notEqual(out.signal, 'BUY_SETUP_WATCH_ONLY');
});
