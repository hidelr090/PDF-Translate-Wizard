import { test, expect } from '@playwright/test';

test('deve carregar o aplicativo', async ({ page }) => {
  await page.goto('http://localhost:5123');
  await expect(page.locator('h1')).toContainText('PDF Translate Wizard');
});

test('deve exibir mensagem de boas-vindas', async ({ page }) => {
  await page.goto('http://localhost:5123');
  const welcomeText = page.locator('p');
  await expect(welcomeText).toContainText('Tradutore de PDF');
});

test('deve ter título da aplicação', async ({ page }) => {
  await page.goto('http://localhost:5123');
  await expect(page).toHaveTitle('PDF Translate Wizard');
});
