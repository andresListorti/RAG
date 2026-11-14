const { defineConfig, devices } = require('@playwright/test');

module.exports = defineConfig({
  testDir: './tests/browser',
  timeout: 30000,
  fullyParallel: false,
  workers: 1,
  retries: process.env.CI ? 1 : 0,
  reporter: [['list'], ['html', { open: 'never' }]],
  use: {
    baseURL: process.env.E2E_BASE_URL || 'http://127.0.0.1:8001',
    trace: 'retain-on-failure',
    screenshot: 'only-on-failure',
    colorScheme: 'light',
  },
  projects: [
    { name: 'desktop-chromium', use: { ...devices['Desktop Chrome'] } },
    { name: 'mobile-chromium', use: { ...devices['Pixel 7'] } },
  ],
  webServer: process.env.E2E_BASE_URL ? undefined : {
    command: `${process.platform === 'win32' ? '.venv\\Scripts\\python.exe' : '.venv/bin/python'} -m uvicorn consumidor.api:app --app-dir src --host 127.0.0.1 --port 8001 --no-access-log`,
    url: 'http://127.0.0.1:8001/health',
    reuseExistingServer: false,
    timeout: 60000,
    env: { GENERATION_BACKEND: 'extractive', EMBEDDING_MODEL: '' },
  },
});
