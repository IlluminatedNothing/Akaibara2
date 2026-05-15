# TODO - Prototype auth flow update (Akaibara POS)

## Plan
- [ ] Gather/confirm role storage expectations (custom users table vs current Django Profile model).
- [ ] Update authentication flow:
  - [ ] Allow only Django superuser for first login.
  - [ ] Implement akaibara_login/submit to authenticate via Django auth only.
  - [ ] On success, redirect based on role from custom users data.
- [ ] Implement access control:
  - [ ] Add login_required to all protected views.
  - [ ] Add role_check decorator and enforce allowed roles per page.
  - [ ] Ensure missing role shows error and blocks access.
- [ ] Implement admin account creation:
  - [ ] Admin create-user page assigns role immediately.
  - [ ] Create both Django auth User + custom users table record (incl. role_id).
  - [ ] Admin generates a temporary password and provides it in UI.
- [ ] Rename new-sale -> cashier in templates/links if needed.
- [ ] Wiring/URLs:
  - [ ] Ensure required routes exist: /dashboard/, /cashier/, /item-inspection/, /auth/ login, admin user management.
- [ ] Run migrations/tests (if DB model changes):
  - [ ] makemigrations/migrate
  - [ ] smoke test login and role redirects

