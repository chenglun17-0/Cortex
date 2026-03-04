import { spawn } from 'node:child_process';
import { setTimeout as sleep } from 'node:timers/promises';
import path from 'node:path';
import process from 'node:process';
import { pathToFileURL } from 'node:url';

const FRONTEND_DIR = path.resolve('/Users/jal/school/Cortex/cortex-frontend');
const APP_URL = 'http://127.0.0.1:4173';
const PLAYWRIGHT_MODULE_URL = pathToFileURL(
  path.join(FRONTEND_DIR, 'node_modules/playwright/index.mjs')
).href;

function startDevServer() {
  const child = spawn('npm', ['run', 'dev', '--', '--host', '127.0.0.1', '--port', '4173'], {
    cwd: FRONTEND_DIR,
    stdio: ['ignore', 'pipe', 'pipe'],
  });

  const waitUntilReady = new Promise((resolve, reject) => {
    const timeout = setTimeout(() => {
      reject(new Error('Timed out waiting for Vite dev server'));
    }, 30000);

    child.stdout.on('data', (chunk) => {
      const text = chunk.toString();
      if (text.includes('Local:') || text.includes('ready in')) {
        clearTimeout(timeout);
        resolve(undefined);
      }
    });

    child.stderr.on('data', (chunk) => {
      const text = chunk.toString();
      if (text.toLowerCase().includes('error')) {
        clearTimeout(timeout);
        reject(new Error(`Vite server error: ${text.trim()}`));
      }
    });

    child.on('exit', (code) => {
      clearTimeout(timeout);
      if (code !== 0) {
        reject(new Error(`Vite dev server exited with code ${code}`));
      }
    });
  });

  return { child, waitUntilReady };
}

function wireApiMocks(page) {
  let userSearchRequested = false;
  const project = {
    id: 1,
    name: 'Cortex Core',
    description: 'Core project',
    owner_id: 1,
    organization_id: 1,
    members: [{ id: 1, username: 'alice', email: 'alice@example.com' }],
    created_at: '2026-01-01T00:00:00',
    updated_at: '2026-01-02T00:00:00',
  };

  page.route('**/api/v1/users/me', (route) =>
    route.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify({ id: 1, username: 'alice', email: 'alice@example.com', is_active: true }) })
  );

  page.route('**/api/v1/projects/', (route) => {
    const method = route.request().method();
    if (method === 'GET') {
      return route.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify([project]) });
    }
    if (method === 'POST') {
      return route.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify(project) });
    }
    return route.continue();
  });

  page.route('**/api/v1/projects/1', (route) => {
    const method = route.request().method();
    if (method === 'GET' || method === 'PATCH') {
      return route.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify(project) });
    }
    if (method === 'DELETE') {
      return route.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify({ message: '项目已删除' }) });
    }
    return route.continue();
  });

  page.route('**/api/v1/tasks/project/1', (route) =>
    route.fulfill({ status: 200, contentType: 'application/json', body: '[]' })
  );

  page.route('**/api/v1/projects/1/members', (route) => {
    const method = route.request().method();
    if (method === 'GET') {
      return route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify([{ id: 1, username: 'alice', email: 'alice@example.com' }]),
      });
    }
    if (method === 'POST') {
      return route.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify({ message: '成员添加成功' }) });
    }
    return route.continue();
  });

  page.route('**/api/v1/projects/1/members/*', (route) =>
    route.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify({ message: '成员已移除' }) })
  );

  page.route('**/api/v1/users/search**', (route) =>
    {
      userSearchRequested = true;
      return route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify([{ id: 2, username: 'john', email: 'john@example.com', is_active: true }]),
      });
    }
  );

  return {
    hasUserSearchRequest() {
      return userSearchRequested;
    },
  };
}

async function assertVisible(locator, label) {
  const isVisible = await locator.first().isVisible({ timeout: 10000 });
  if (!isVisible) {
    throw new Error(`Expected visible: ${label}`);
  }
}

async function run() {
  const { chromium } = await import(PLAYWRIGHT_MODULE_URL);
  const { child: devServer, waitUntilReady } = startDevServer();
  const browser = await chromium.launch({ headless: true });

  try {
    await waitUntilReady;

    const context = await browser.newContext();
    const page = await context.newPage();
    const mockState = wireApiMocks(page);

    await page.addInitScript(() => {
      window.localStorage.setItem('access_token', 'fake-token');
    });

    await page.goto(`${APP_URL}/projects`, { waitUntil: 'networkidle' });
    await assertVisible(page.getByText('我的项目'), 'project page title');
    await assertVisible(page.getByText('Cortex Core'), 'mocked project card');

    await page.getByText('Cortex Core').first().click();
    await page.waitForURL('**/projects/1', { timeout: 10000 });

    await assertVisible(page.getByRole('button', { name: /成员管理/ }), 'member management button');
    await page.getByRole('button', { name: /成员管理/ }).click();
    await assertVisible(page.getByText('项目成员管理'), 'member drawer title');
    await assertVisible(page.getByText('alice'), 'existing member item');

    await page.getByPlaceholder('搜索用户名...').fill('john');
    await page.waitForTimeout(800);
    if (!mockState.hasUserSearchRequest()) {
      throw new Error('Expected user search request to be triggered');
    }

    console.log('Frontend project management smoke test passed.');

    await context.close();
  } finally {
    await browser.close();
    devServer.kill('SIGINT');
    await sleep(1000);
  }
}

run().catch((error) => {
  console.error(error);
  process.exit(1);
});
