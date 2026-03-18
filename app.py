from __future__ import annotations

import logging
from nicegui import ui
from ui_panels import render_toolbar, main_content
GLOBAL_UI_STYLE = '''
<style>
  html, body, .nicegui-content {
    font-family: "Segoe UI", system-ui, -apple-system, "Helvetica Neue", Arial, sans-serif !important;
    font-size: 12px !important;
    overflow-x: hidden !important;
  }

  .q-card,
  .q-expansion-item__container,
  .q-drawer,
  .q-table__container,
  .q-dialog__inner .q-card {
    background: #ffffff !important;
    border: 1px solid #d0d0d0 !important;
    border-radius: 4px !important;
    box-shadow: none !important;
  }

  .q-expansion-item__container > .q-item,
  .q-card > .q-card__section:first-child,
  .q-drawer .q-toolbar {
    background: #f2f4f7 !important;
  }

  .q-card__section,
  .q-item,
  .q-field__control,
  .q-table thead tr th,
  .q-table tbody tr td {
    padding: 8px !important;
  }

  .q-card,
  .q-expansion-item,
  .q-btn,
  .q-field,
  .q-table__container {
    margin: 6px !important;
  }

  .q-btn:not(.q-btn--round):not(.q-btn--fab) {
    min-height: 30px !important;
    height: auto !important;
    padding: 4px 12px !important;
    background: #ffffff !important;
    color: #111111 !important;
    border-radius: 4px !important;
    border: 1px solid #111111 !important;
    box-shadow: none !important;
    text-transform: none !important;
    font-weight: 600 !important;
    line-height: 1.2 !important;
    max-width: 100% !important;
  }

  .q-btn:not(.q-btn--round):not(.q-btn--fab):hover {
    background: #f2f2f2 !important;
  }

  .q-btn:not(.q-btn--round):not(.q-btn--fab):active,
  .q-btn.q-btn--active:not(.q-btn--round):not(.q-btn--fab) {
    border: 2px solid #111111 !important;
  }

  .q-btn:not(.q-btn--round):not(.q-btn--fab) .q-icon,
  .q-btn:not(.q-btn--round):not(.q-btn--fab) .q-btn__content,
  .q-btn:not(.q-btn--round):not(.q-btn--fab) .q-btn__content * {
    color: #111111 !important;
  }

  .q-btn:not(.q-btn--round):not(.q-btn--fab) .q-btn__content {
    display: inline-flex !important;
    align-items: center !important;
    justify-content: center !important;
    gap: 6px !important;
    max-width: 100% !important;
    white-space: nowrap !important;
    overflow: hidden !important;
    text-overflow: ellipsis !important;
    line-height: 1.2 !important;
  }

  .q-chip,
  .q-tab,
  .q-tab__label {
    white-space: nowrap !important;
    overflow: hidden !important;
    text-overflow: ellipsis !important;
    line-height: 1.2 !important;
    max-width: 100% !important;
  }

  .q-field__native,
  .q-field__input,
  .q-item__label,
  .q-select__dropdown-icon {
    line-height: 1.2 !important;
  }

  .q-field,
  .q-input,
  .q-select,
  .q-item,
  .q-card,
  .q-card__section {
    min-width: 0 !important;
    max-width: 100% !important;
  }

  .btn-wrap .q-btn__content {
    white-space: normal !important;
    overflow: visible !important;
    text-overflow: clip !important;
    text-align: center !important;
    line-height: 1.15 !important;
  }

  .btn-wrap {
    min-height: 34px !important;
    height: auto !important;
  }

  .left-tabs-row .left-tab-btn {
    min-height: 24px !important;
    height: auto !important;
    padding: 3px 4px !important;
    margin: 0 !important;
    font-size: 10px !important;
    line-height: 1 !important;
    border-radius: 4px !important;
    border: 1px solid #d0d0d0 !important;
    box-shadow: none !important;
    text-transform: none !important;
    white-space: nowrap !important;
    overflow: hidden !important;
    text-overflow: ellipsis !important;
    min-width: 28% !important;
  }

  .left-tabs-row .left-tab-active {
    background: #ffffff !important;
    color: #111111 !important;
    border: 2px solid #111111 !important;
  }

  /* KL Cut: neutralize blue utility accents used in legacy classes */
  [class*="bg-blue-"] {
    background: #ffffff !important;
    color: #111111 !important;
    border-color: #111111 !important;
  }

  [class*="text-blue-"],
  [class*="border-blue-"] {
    color: #111111 !important;
    border-color: #111111 !important;
  }

  .left-tabs-row .left-tab-inactive {
    background: #ffffff !important;
    color: #111111 !important;
    border-color: #111111 !important;
  }

  .left-tabs-row .q-btn__content {
    white-space: nowrap !important;
    overflow: hidden !important;
    text-overflow: ellipsis !important;
    font-size: 10px !important;
    justify-content: center !important;
  }

  .left-tabs-row .left-tab-disabled,
  .left-tabs-row .left-tab-btn.q-btn--disabled {
    background: #e5e7eb !important;
    color: #6b7280 !important;
    border-color: #d0d0d0 !important;
    opacity: 1 !important;
  }

  .left-panel-compact .q-card,
  .left-panel-compact .q-expansion-item,
  .left-panel-compact .q-field {
    margin: 2px !important;
  }

  .left-panel-compact .q-card__section,
  .left-panel-compact .q-item,
  .left-panel-compact .q-field__control {
    padding: 4px !important;
  }

  .left-panel-compact .q-expansion-item__content > .q-card {
    margin-top: 2px !important;
    margin-bottom: 2px !important;
  }

  .left-panel-body {
    overflow-y: auto !important;
    overflow-x: hidden !important;
  }

  .left-panel-compact,
  .left-panel-compact * {
    max-width: 100% !important;
    box-sizing: border-box !important;
    overflow-wrap: break-word !important;
    word-break: break-word !important;
  }

  .left-panel-compact .q-scrollarea__content,
  .left-panel-compact .q-scrollarea__container,
  .left-panel-compact .q-scrollarea,
  .left-panel-compact .q-field,
  .left-panel-compact .q-select,
  .left-panel-compact .q-input,
  .left-panel-compact .q-btn,
  .left-panel-compact .q-card,
  .left-panel-compact .q-item {
    max-width: 100% !important;
  }

  .nacrt-fit-image {
    width: 100% !important;
    height: auto !important;
    max-width: 100% !important;
    max-height: 100% !important;
    object-fit: contain !important;
    display: block !important;
  }

  .nacrt-fit-image img,
  .nacrt-fit-image .q-img__image {
    width: 100% !important;
    height: auto !important;
    max-width: 100% !important;
    max-height: 100% !important;
    object-fit: contain !important;
    object-position: center center !important;
  }

  .sidebar-sticky-footer {
    background: #ffffff !important;
    border-top: 1px solid #d0d0d0 !important;
    padding: 8px !important;
    overflow-x: hidden !important;
  }

  /* Canvas toolbar: stop global margins/ellipsis from clipping control text */
  .canvas-toolbar .q-field,
  .canvas-toolbar .q-select,
  .canvas-toolbar .q-input,
  .canvas-toolbar .q-btn,
  .canvas-toolbar .q-checkbox {
    margin: 0 !important;
  }

  .canvas-toolbar .q-field__native,
  .canvas-toolbar .q-field__input,
  .canvas-toolbar .q-btn__content {
    white-space: nowrap !important;
    overflow: visible !important;
    text-overflow: clip !important;
  }

  .canvas-toolbar .q-field__control {
    padding: 0 8px !important;
    min-height: 28px !important;
    height: 28px !important;
    align-items: center !important;
  }

  .canvas-toolbar .q-field__native,
  .canvas-toolbar .q-field__input {
    padding: 0 !important;
    min-height: 0 !important;
    height: auto !important;
    line-height: 1.1 !important;
    display: flex !important;
    align-items: center !important;
  }

  .canvas-toolbar .q-select__dropdown-icon {
    align-self: center !important;
    margin-top: 0 !important;
  }

  .canvas-toolbar .q-field__control,
  .canvas-toolbar .q-btn {
    min-height: 28px !important;
    height: 28px !important;
  }

</style>
'''


@ui.page('/')
def index() -> None:
    ui.query('body').style('margin: 0; padding: 0;')
    ui.add_head_html(GLOBAL_UI_STYLE)
    render_toolbar()
    main_content()


def run_app() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
    )
    ui.run(
        title='krojna pista PRO',
        port=8080,
        reload=False,
        workers=0,
    )


if __name__ in {'__main__', '__mp_main__'}:
    run_app()
