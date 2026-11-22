import {test,expect} from '@playwright/test';
test('protected route redirects to secure login',async({page})=>{await page.goto('/patients');await expect(page).toHaveURL(/\/login/);await expect(page.getByRole('heading',{name:'Welcome back'})).toBeVisible()});
