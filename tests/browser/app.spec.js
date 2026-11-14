const { test, expect } = require('@playwright/test');
const AxeBuilder = require('@axe-core/playwright').default;

test('source metadata, warranty query, citations, trace and full articles', async ({ page }) => {
  const errors = [];
  page.on('pageerror', error => errors.push(error.message));
  await page.goto('/');
  await expect(page.locator('#article-count')).toHaveText('75');
  if (process.env.CAPTURE_PORTFOLIO === '1') {
    const mobile = test.info().project.name.startsWith('mobile');
    await page.screenshot({ path: `docs/images/demo-${mobile ? 'mobile' : 'desktop'}.png`, fullPage: true, scale: 'css' });
  }
  await page.getByRole('button', { name: 'Garantía de un producto' }).click();
  await expect(page.getByLabel('¿Qué querés buscar?')).not.toBeEmpty();
  await page.getByRole('button', { name: /Explorar la ley/ }).click();
  await expect(page.locator('#results')).toBeVisible();
  await expect(page.locator('#claims .claim')).toHaveCount(5);
  await expect(page.locator('#claims')).toContainText('Art. 11');
  await expect(page.locator('#trace')).toContainText('search');
  await expect(page.locator('#trace')).toContainText('extractive');
  await page.getByText('Ver artículos completos recuperados').click();
  await expect(page.locator('#evidence')).toContainText('SEIS');
  for (const link of await page.locator('#claims a').all()) {
    await expect(link).toHaveAttribute('href', 'https://www.argentina.gob.ar/normativa/nacional/ley-24240-638/actualizacion');
  }
  expect(errors).toEqual([]);
  expect(await page.evaluate(() => document.documentElement.scrollWidth > innerWidth)).toBe(false);
});

test('out-of-scope questions abstain and replace prior results', async ({ page }) => {
  await page.goto('/');
  await page.getByLabel('¿Qué querés buscar?').fill('¿Qué garantía legal tiene un producto?');
  await page.getByRole('button', { name: /Explorar la ley/ }).click();
  await expect(page.locator('#claims .claim')).toHaveCount(5);
  await page.getByLabel('¿Qué querés buscar?').fill('¿Cómo calculo la órbita de Marte?');
  await page.getByRole('button', { name: /Explorar la ley/ }).click();
  await expect(page.locator('#result-message')).toContainText('fuera del alcance');
  await expect(page.locator('#claims .claim')).toHaveCount(0);
});

test('provider text is displayed as text, never executable markup', async ({ page }) => {
  const response = await page.request.post('/api/ask', { data: { question: 'garantía legal' } });
  const data = await response.json();
  data.claims[0].statement = '<img src=x onerror="window.injected=true">';
  await page.route('**/api/ask', route => route.fulfill({ json: data }));
  await page.goto('/');
  await page.getByLabel('¿Qué querés buscar?').fill('garantía legal');
  await page.getByRole('button', { name: /Explorar la ley/ }).click();
  await expect(page.locator('#claims')).toContainText('<img src=x');
  await expect(page.locator('#claims img')).toHaveCount(0);
  expect(await page.evaluate(() => window.injected)).toBeUndefined();
});

test('429 errors remain usable and do not discard the question', async ({ page }) => {
  await page.route('**/api/ask', route => route.fulfill({ status: 429, json: { detail: 'busy' } }));
  await page.goto('/');
  await page.getByLabel('¿Qué querés buscar?').fill('garantía legal');
  await page.getByRole('button', { name: /Explorar la ley/ }).click();
  await expect(page.getByRole('alert')).toContainText('ocupada');
  await expect(page.getByRole('button', { name: /Explorar la ley/ })).toBeEnabled();
  await expect(page.getByLabel('¿Qué querés buscar?')).toHaveValue('garantía legal');
});

test('WCAG 2.2 AA automated audit before and after search', async ({ page }) => {
  await page.goto('/');
  let audit = await new AxeBuilder({ page }).withTags(['wcag2a', 'wcag2aa', 'wcag21aa', 'wcag22aa']).analyze();
  expect(audit.violations).toEqual([]);
  await page.getByLabel('¿Qué querés buscar?').fill('¿Qué garantía legal tiene un producto?');
  await page.getByRole('button', { name: /Explorar la ley/ }).click();
  await expect(page.locator('#results')).toBeVisible();
  audit = await new AxeBuilder({ page }).withTags(['wcag2a', 'wcag2aa', 'wcag21aa', 'wcag22aa']).analyze();
  expect(audit.violations).toEqual([]);
});

test('keyboard access and mobile layout', async ({ page }) => {
  await page.goto('/');
  const question = page.getByLabel('¿Qué querés buscar?');
  await question.focus();
  await expect(question).toBeFocused();
  await page.keyboard.type('garantia legal');
  await page.keyboard.press('Tab');
  await expect(page.getByRole('button', { name: /Explorar la ley/ })).toBeFocused();
  await page.keyboard.press('Enter');
  await expect(page.locator('#results')).toBeVisible();
  expect(await page.evaluate(() => document.documentElement.scrollWidth > innerWidth)).toBe(false);
});
