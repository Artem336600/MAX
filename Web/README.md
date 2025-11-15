Я разделю на логические блоки: Структура сайта → Главные страницы и компоненты → Панель пользователя (Dashboard) и виджеты → Управление модулями (библиотека, создание, настройка) → Редактор модулей (no-code / Python / LLM) → Система переменных и событий → Чат и интерактивные элементы на сайте → Уведомления, логика фоновых задач, расписания → Права и безопасность → Администрирование, аналитика и оплата → Нефункциональные требования (производительность, доступность, локализация) → Приложение: примеры сценариев и макеты страниц.

1. Общая структура сайта

Главная архитектурная раскладка (уровни интерфейса):

/ (Landing)  
/dashboard  — персональная панель
/chat       — встроенный чат / помощник
/modules    — библиотека модулей
/module/new — конструктор модуля (выбор: No-code / Python / LLM)
/module/:id — детальная страница модуля / настройки
/variables  — глобальные переменные и их история
/integrations — внешние сервисы / API keys
/settings   — профиль, приватность, подписки
/admin      — админская консоль (для операторов системы)


Каждая страница динамически адаптируется под установленные у пользователя модули.

2. Landing / Главная страница

Цель: быстро объяснить продукт и дать пути входа — зарегистрироваться или попробовать демо.

Компоненты:

Короткий заголовок, USP (что делает Eidos).

Секция “Как это работает” (инфографика): модули → переменные → чат/UI.

Примеры виджетов/панелей (скриншоты) — кликабельные демо.

Блок “Библиотека модулей” — популярные карточки (демо данных).

CTA: Зарегистрироваться / Попробовать демо.

Footer: политика, контакты, документация, API.

3. Onboarding / Первый запуск

Цель: максимально быстро дать полезную персонализированную панель.

Поток:

Короткий опрос (3–6 вопросов) — интересы: сон, работа, учёба, финансы, спорт.

Рекомендация начального набора модулей (авто-установка одного кликом).

Краткая демонстрация чата + тур по Dashboard.

Опция “экспертный режим” для разработчиков.

UX-детали:

Возможность пропустить любой шаг.

Подсказки (tooltip) и “почему это важно”.

Предзаполнение глобальных переменных при разрешении доступа к календарю/фитнесу.

4. Dashboard (Панель пользователя) — самая важная страница
4.1 Структура Dashboard

Header: имя пользователя, быстрый поиск (по командам и модулям), глобальный статус (онлайн/оффлайн).

Левое меню: Chat, Modules, Variables, Integrations, Settings.

Центр: Grid из виджетов (добавляемые модулями).

Right Sidebar: Контекстные действия, быстрые команды, истории уведомлений.

4.2 Виджеты (Widgets)

Любой модуль может предоставить один или несколько виджетов. Виджеты — композиционные блоки:

типы: график, список, карта, карусель, таймер, кнопка действия, форма.

каждый виджет имеет:

title, subtitle

data endpoint (read-only or read-write)

actions (кнопки, модальные окна)

настройки видимости (role, device, schedule)

Возможность drag&drop; сохранение layout per-user.

4.3 Примеры виджетов

Календарь дня — события (модуль календаря).

Качество сна (график) — sleep module.

Финансы (диаграмма расходов).

Ежедневные цели (карточки с чекбоксами).

Quick Actions — динамические кнопки, которые добавляют модули.

4.4 Поведение

Виджеты обновляются realtime при изменениях переменных.

Виджеты можно скрыть/удалить, настроить разрешения.

Переключатели для “показывать на мобильных” и “показывать в чате”.

5. Раздел «Модули» — библиотека и управление
5.1 Библиотека модулей — каталог

Фильтры: категория, тип (no-code/python/llm/integration), рейтинг, популярность, автор.

Карточка модуля (кратко): иконка, рейтинг, installs, краткое описание, переменные (read/write), кнопки Install / Preview / Source (если open).

Детальная карточка: docs, примеры использования, требования к переменным, screenshots, CHANGELOG, зависимости, manifest.json preview.

5.2 Установка модуля

Права доступа: диалог показывает, какие переменные и разрешения требует модуль.

Sandbox-проверка: симуляция установки и потенциальных конфликтов (static analysis).

После установки: модуль регистрируется в Plugin Manager, создаёт виджеты и команды.

5.3 Управление собственными модулями

Список установленных модулей с версиями, статусом (enabled/disabled), логом запуска.

Кнопки: Edit, Disable, Update, Uninstall, Export (пакет).

Конфликты: UI показывает конфликтующие переменные/действия и предлагает приоритеты.

6. Конструктор модулей — No-code / Low-code / Code
6.1 Общие принципы

Три режима: No-code (визуально), Script (Python), LLM (Prompt+Adapter).

Манифест модуля (JSON/YAML) редактируется автоматически.

Автоматическая проверка разрешений переменных.

Версионирование: версия модуля, bump, rollback.

6.2 No-code (Rule builder)

Интерфейс: визуальный блок-схемный редактор (drag&drop):

Nodes: Trigger (intent/event/cron/variable_change), Condition (операторы), Action (set_var, notify, schedule_event, call_http, open_ui).

Примеры: IF sleep_quality < 6 THEN notify + set sleep_recommendations.

Встроенные тесты: прогнать набор тестовых переменных и увидеть результат.

6.3 Python-редактор (сандбокс)

Фичи:

Syntax highlighting, LSP-style автодополнение, snippets.

Подсказки Eidos API (self.var, self.set, self.schedule).

Запуск unit-test в тестовом окружении с mock переменными.

Линтер и security scanner (находят os/requests/subprocess и запрещают).

Manifest panel (попап с разрешениями).

One-click publish → submission to library (if user desires).

Безопасность:

Каждый Python-модуль исполняется в изолированном sandbox (container / WASM / restricted interpreter).

Ограничение таймаута, memory, network access (через allowlist).

Логи выполнения, метрики времени/памяти.

6.4 LLM-модуль (Prompt module)

Форма: Prompt template + input mapping + output parsing rules.

Mapping: какие переменные вставить в prompt ({{sleep_duration}}, etc).

Post-processing: парсер JSON/markdown → to variables.

Provider selection: выбрать связку LLM, Embeddings, Vector DB.

Safety checks: запрет на запросы личных данных без согласия.

7. Переменные (Variables) и события (Events)
7.1 Каталог глобальных переменных

Таблица: name, type (number/string/boolean/list/object), owner (system/module), readable_by, writable_by, notifiable, description, last_value, last_updated.

Поиск и фильтр.

История значений: timeline с who/when/change.

Политика ретенции (сколько хранить истории).

7.2 Создание новой переменной

UI для создания с формой: имя, тип, default, access control, notify_on_change, validation rules (min/max, regex).

7.3 События (Event Bus)

Лог событий: event_type, payload, origin_module, timestamp.

Подписки: модули могут subscribe / unsubscribe.

Event replay: админ может реплейнуть события для отладки.

8. Chat на сайте — UI и поведение
8.1 Главное окно чата

Большое поле ввода, поддержка команд и естественной речи.

Автокомплит команд (в зависимости от модулей).

Блок подсказок: быстрые команды (dynamic Quick Actions).

История чата сохраняется per-user и per-session.

8.2 Распознавание намерения и маршрутизация

При вводе текст → intent router → candidate modules (ranked).

UI показывает источник ответа: какой модуль ответил / LLM / core.

В ответ входит: текст + actions (кнопки) + changes (переменные обновлённые) + suggested modules.

8.3 UI-элементы в сообщениях

Кнопки: execute action (например, /reschedule)

Формы: inline form для быстрого ввода (например, добавить трату)

Карточки с данными (карточка события, карточка бюджетной рекомендации)

Rich media: графики, таблицы (мини-виджеты)

8.4 Персональные команды и синтаксис

Команды автоматически доступны, если модуль их объявил.

Команды видны в автодополнении и в справке чата.

Пользователь может переопределить ключевые привязки команд.

9. Notifications / Уведомления
9.1 Типы уведомлений

In-app (toast, badge)

Email

Push (mobile/web)

Messenger (Telegram, WhatsApp)

Webhooks (для интеграций)

9.2 Настройка уведомлений

Глобальные правила и per-module overrides.

Priority levels (low/normal/high/critical).

Quiet hours / do-not-disturb.

Notification templates (модули могут отправлять шаблонные сообщения).

10. Интеграции и внешние API
10.1 Integrations page

Список сервисов: Google Calendar, Apple Health, Fitbit, Stripe, Telegram, Slack, OAuth providers.

Подключение сервисов через OAuth / API keys.

Scopes: какие переменные можно читать/писать.

Logs: audit of external calls.

10.2 Webhooks & API endpoints

Пользователь может создать endpoint для своего модуля.

Примеры: incoming webhook для трекера привычек, outgoing webhook при изменении переменной.

Поддержка HMAC signatures для безопасности.

11. Permissions, Privacy и безопасность
11.1 Model доступа

Роли: owner, admin (team), collaborator, viewer.

Разрешения модулей к переменным — explicit allowlist.

Пользователь подтверждает доступ при установке модуля.

11.2 Audit / Logs

Все изменения переменных, вызовы модулей, network-запросы логируются.

UI для аудита с фильтрами (module, variable, date, action).

11.3 Data privacy

Возможность scrub personal data (GDPR Right to be forgotten).

Data export (JSON/CSV) per-user.

Retention policy controls.

11.4 Security features

CSP, XSS protection, rate limits, auth (JWT/OAuth2), 2FA support.

Sandbox execution for code modules (no direct FS or OS access).

Allowed domains list для внешних HTTP-запросов.

12. Admin / Управление платформой
12.1 Admin dashboard

Список установленных модулей (global), мониторинг здоровья системы, очереди задач, usage metrics.

Механизм review/publish модулей (для публичной библиотеки).

Инструменты rollback / kill-switch для проблемных модулей.

12.2 Moderation

Жалобы пользователей, автоматические проверки модулей (недопустимый контент).

Статусы модулей: draft / private / public / flagged.

13. Billing, Subscriptions и Marketplace
13.1 Модель монетизации

Freemium: базовый функционал бесплатно, платные tiers для LLM-credits, storage, integrations.

Marketplace: платные модули, revenue share с авторами.

Credits: покупаемые для LLM calls / heavy compute tasks.

13.2 UI оплаты

Billing page: invoices, payment methods, usage dashboard.

License keys для корпоративных клиентов.

14. Analytics, Telemetry и A/B
14.1 Пользовательская аналитика

Metrics: active modules, events per user, avg response time, LLM tokens used.

Dashboards per user (for power users) и global.

14.2 A/B и feature flags

Возможность включать / отключать новые фичи для % пользователей.

Experiment tracking.

15. Нефункциональные требования
15.1 Производительность

Realtime updates via WebSocket / server-sent events.

Caching for variable reads (Redis).

Horizontal scaling: stateless web layer; stateful services (DB, vector DB).

15.2 Надёжность

SLA для core APIs.

Backups: daily snapshots + point-in-time recovery.

15.3 Доступность

WCAG 2.1 AA

Keyboard navigation, ARIA labels, color contrast.

15.4 Локализация

Интерфейс multilingual (i18n keys).

Форматы даты/времени и локальные правила.

16. Технические детали и API (кратко)
16.1 Основные internal API endpoints (пример)

POST /api/v1/modules/install — установить модуль

GET /api/v1/modules — список доступных модулей

POST /api/v1/variables/get — получить переменную

POST /api/v1/variables/set — установить переменную

POST /api/v1/events/publish — опубликовать событие

POST /api/v1/modules/:id/execute — вызвать модуль вручную (для debug)

GET /api/v1/logs — получить логи (admin)

16.2 Webhook security

HMAC signature, timestamp, replay window.

16.3 Extensibility

Plugin hooks: onModuleInstall, onVariableChange, onIntentRecognized.

17. Dev UX: документация и SDK

Документация (дока сайдбар) с примерами модулей.

SDKs: JavaScript, Python, CLI (для локальной разработки модулей).

Templates repo: collection of sample modules (sleep, finance, study).

Marketplace guide: как упаковать модуль, тесты, security checklist.

18. Примеры сценариев (как выглядят страницы и поведение)
Пример 1 — Страница модуля (детальная)

Header: Название, рейтинг, версия, автор.

Tabs: Overview | Variables | UI Preview | Code | Tests | Changelog | Permissions.

Кнопки: Install / Install for Team / Fork / Report.

In-page preview: мини-виджеты, chat-sim.

Пример 2 — Создать Python-модуль

Стартовая страница: выбрать template.

Editor: код + manifest + tests.

Sandbox: кнопка Run test → видно какие переменные поменялись.

Publish flow: security scan → add docs → submit.

Пример 3 — Variables page

Таблица переменных + filter.

Просмотр конкретной переменной: timeline, who changed, modules reading/writing.

Edit: change ACL, TTL, default.

19. UX-детали: удобство для обычных пользователей

Система шаблонов: готовые модули “для сна”, “для учёбы”, “финансы” — 1 клик установить.

Понятные подсказки при установке (какие переменные поменяются).

“Safe mode” для новичков: никакие модули не имеют автоматических write-разрешений пока пользователь не подтвердит.

Marketplace review: отмечены модератором и с рейтингом безопасности.

“Undo” для важных изменений (rollback recent change).

20. Итог — что будет на сайте (коротко)

Динамический Dashboard, собирающий виджеты от установленных модулей.

Полнофункциональная библиотека модулей с установкой в 1 клик.

Мощный конструктор модулей: No-code, Python (sandbox), LLM (prompt modules).

Полный каталог глобальных переменных и event bus.

Интегрированный чат с адаптивными командами и UI-элементами.

Система уведомлений и интеграций (webhooks, OAuth).

Админка, аналитика, биллинг и marketplace.

Безопасность, права и аудит на всех уровнях.