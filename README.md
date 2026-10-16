# Blitz.cloud Daily Login
*powered by ConfigFars™*

ورود روزانهٔ مجاز به حساب خودتان در داشبورد Blitz.cloud با Google Chrome + Playwright روی GitHub Actions.

> این پروژه تضمینی برای جلوگیری از Sleep، توقف Worker یا عبور از محدودیت‌های پلن نیست. CAPTCHA/2FA دور زده نمی‌شود.

## راه‌اندازی
1. مخزن را در GitHub بسازید و این فایل‌ها را در شاخهٔ پیش‌فرض (main) Push کنید.
2. `Settings → Secrets and variables → Actions → New repository secret`
   - `EMAIL` = ایمیل حساب
   - `PAS` = رمز عبور حساب
3. تب **Actions** را باز کنید و در صورت درخواست، Workflow ها را Enable کنید.
4. برای تست: `Actions → Blitz.cloud Daily Login → Run workflow`.

## زمان‌بندی
هر روز ۰۰:۰۰ به وقت تهران (`cron: "0 0 * * *"` با `timezone: "Asia/Tehran"`). فقط روی شاخهٔ پیش‌فرض فعال است و ممکن است چند دقیقه تأخیر داشته باشد. GitHub بعد از ۶۰ روز بی‌فعالیتی مخزن، زمان‌بندی را غیرفعال می‌کند.

## نتیجه (در لاگ مرحلهٔ Run login)
| وضعیت | Exit code | معنی |
|---|---|---|
| `LOGIN_CONFIRMED` | 0 | فرم ورود نیست و روی دامنهٔ blitz.cloud هستیم |
| `LOGIN_FAILED` | 1 | فرم هنوز نمایش داده می‌شود / خطا |
| `LOGIN_UNCONFIRMED` | 2 | CAPTCHA، 2FA، ناپیدایی فرم یا وضعیت نامشخص |
| (Secret ناقص) | 3 | EMAIL یا PAS تنظیم نشده |

Job فقط در حالت CONFIRMED سبز می‌شود.

## عیب‌یابی
- Secret ها دقیقاً `EMAIL` و `PAS` نام‌گذاری شوند.
- اگر UNCONFIRMED شد، یک بار دستی وارد حساب شوید و بررسی کنید CAPTCHA/تأیید دومرحله‌ای فعال نشده باشد.
- اگر ظاهر صفحهٔ ورود تغییر کرد، برچسب‌های `Email address`، `Password` و دکمهٔ `Sign in` را در `login.py` به‌روز کنید.
