import { test, expect } from '@playwright/test';

test('GET / returns welcome message', async ({ request }) => {
  const res = await request.get('/');
  expect(res.status()).toBe(200);
  const body = await res.json();
  expect(body.message).toBe('Hello from Flask!');
});

test('POST /echo returns same data', async ({ request }) => {
  const payload = { foo: 'bar' };
  const res = await request.post('/echo', { data: payload });
  expect(res.status()).toBe(200);
  const body = await res.json();
  expect(body).toEqual(payload);
});

test('GET /health returns healthy', async ({ request }) => {
  const res = await request.get('/health');
  expect(res.status()).toBe(200);
  const body = await res.json();
  expect(body.status).toBe('healthy');
});
