# Mobile Testing Checklist (360px - 640px)

## Auth Flows
- [ ] **Login** - Email input, password input, "Sign In" button all visible and tappable
- [ ] **Registration** - User type toggle works, all fields visible, form submits correctly
- [ ] **Error messages** - Red error boxes appear below inputs, text readable (0.85rem)
- [ ] **Loading state** - Button text changes to "Signing In..." or "Creating Account...", disabled state visible

## Patient Dashboard (360px viewport)
- [ ] **Header** - Logo, notification bell, profile dropdown visible, hamburger menu appears
- [ ] **Stat cards** - Shows in 1x1 layout (not 3 columns), text not cut off, readable font (1.6rem)
- [ ] **Appointment list** - Doctor names truncated with ellipsis, date cards horizontal or stacked, status badge readable
- [ ] **Quick actions** - Grid shows 1 column on mobile, buttons tappable (25px border-radius visible)
- [ ] **Mobile menu** - Hamburger click opens menu, menu shows all nav items, close works

## Doctor Dashboard (360px viewport)
- [ ] **Stat cards** - Shows 1 per row at 600px, scales from 44px icons at 900px → 40px at 600px
- [ ] **Schedule link** - Visible and tappable
- [ ] **Appointment summary** - Cards don't overflow, time slots readable

## Appointments Booking (360px viewport)
- [ ] **Doctor filter** - Dropdown works, specialty filter appears
- [ ] **Calendar** - Days clickable, no horizontal scroll forced, dates readable (calendar shows but scrolls if needed)
- [ ] **Time slots** - Grid shows 2 columns (not 1), slots tappable at 0.8rem font
- [ ] **Booking summary** - Summary card shows selected doctor/date/time without overflow
- [ ] **Submit button** - "Next" button visible, disables during submission, shows "Booking appointment..." text

## Profile Page (360px viewport)
- [ ] **Header section** - Avatar, name, email visible
- [ ] **Form fields** - Input padding 0.6rem, font 0.9rem, labels 0.85rem
- [ ] **Edit/Save buttons** - Visible, tappable, no overflow
- [ ] **Password section** - Layout works on mobile, password input visible
- [ ] **Delete account** - Warning modal shows, buttons tappable

## Notifications Page (360px viewport)
- [ ] **Dropdown (in header)** - Positions from left (1rem offset), width uses viewport width calc, max-height 70vh
- [ ] **Dropdown items** - Title and message truncate with ellipsis, time readable (0.7rem)
- [ ] **Notifications page** - List items stack vertically, no horizontal scroll
- [ ] **Filters** - Tab buttons work on mobile, border-left indicator visible

## Doctor Schedule (360px viewport)
- [ ] **Calendar grid** - Shows with 50px time label width (down from 80px), 7-day columns still visible
- [ ] **Horizontal scroll** - Calendar allows scroll if needed (min-width 450px on <640px), scroll smooth
- [ ] **Time cells** - Font 0.6rem readable, cell padding 0.2rem, gap 0.5px
- [ ] **Today highlight** - Teal border or background visible on correct day

## Responsive Breakpoints Verification
- [ ] **360px** - All elements readable, no horizontal scroll (except calendar overflow-x: auto)
- [ ] **480px** - Forms still work, appointment cards readable
- [ ] **600px** - Layout transition point, stat cards change from 2-col → 1-col at 600px
- [ ] **640px** - Header padding 1.2rem, logo 1.4rem, no jumps from 600px
- [ ] **768px** - Doctor Schedule shows 2-col quick actions, hamburger still visible

## Text Truncation Verification
- [ ] **Doctor names** - Long names show ellipsis (text-overflow: ellipsis, white-space: nowrap)
- [ ] **Specialty names** - Truncated, not wrapped to next line
- [ ] **Time text** - All readable, not cut off

## Accessibility on Mobile
- [ ] **Touch targets** - All buttons ≥44x44px for tappable areas
- [ ] **Contrast** - Error text (#991b1b on #fee2e2), stat labels (#6b7280) readable
- [ ] **Form fields** - Can zoom to 200% without horizontal scroll
- [ ] **Focus indicators** - Visible on form inputs when tapped

## Payment Flow (if applicable)
- [ ] **Payment button** - Sends to Stripe/payment processor
- [ ] **Confirmation page** - Appointment confirmed, details visible

## Notes
- Test on Chrome DevTools mobile emulation (360x800, 480x800, 640x1024)
- Test on real device if available (iPhone SE ~375px, iPhone 12 390px, iPhone 14 Pro ~430px)
- Verify no console errors in DevTools
- Test with network throttling (3G) for loading indicators

## Build Info
- Last build: 508.81 kB (JS) + 149.11 kB (CSS)
- Frontend: Vite 7.3.1, React 19
- All media queries added: 640px, 768px, 900px, 1200px
