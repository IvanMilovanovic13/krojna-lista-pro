# -*- coding: utf-8 -*-
from __future__ import annotations


def render_elements_tab(
    ui,
    state,
    tr_fn,
    sidebar_content,
    render_canvas_toolbar,
    nacrt_render,
    main_content_refresh,
    set_view_mode,
    set_show_grid,
    set_grid_mm,
    set_show_bounds,
    set_ceiling_filler,
    render_kitchen_elements_scene_3d,
    wall_len_h,
    zone_baseline_and_height,
    get_zone_depth_standard,
    reset_3d_camera_home=None,
    set_3d_camera_preset=None,
) -> None:
    """Renderuje ceo 'Elementi' tab (UI layout only)."""
    if not hasattr(state, 'element_canvas_mode'):
        setattr(state, 'element_canvas_mode', '2D')
    if not hasattr(state, 'elements_sidebar_collapsed'):
        setattr(state, 'elements_sidebar_collapsed', False)

    def _set_sidebar_collapsed(value: bool) -> None:
        setattr(state, 'elements_sidebar_collapsed', value)
        main_content_refresh()

    sidebar_collapsed = bool(getattr(state, 'elements_sidebar_collapsed', False))

    # Keep canvas fully visible under top toolbar/tab strip; prevent bottom clipping.
    with ui.row().classes('w-full h-[calc(100vh-72px)] gap-0 min-h-0 overflow-hidden'):
        if sidebar_collapsed:
            with ui.column().classes(
                'left-panel-compact w-[52px] border-r border-gray-200 h-full min-h-0 flex flex-col '
                'items-center overflow-hidden bg-white shrink-0 py-2 gap-2'
            ):
                ui.button(
                    icon='chevron_right',
                    on_click=lambda: _set_sidebar_collapsed(False),
                ).props('flat round dense').tooltip(tr_fn('sidebar.expand'))
                ui.label(tr_fn('sidebar.collapsed_label')).classes(
                    'text-[10px] font-semibold uppercase tracking-wide text-gray-500 text-center px-1'
                )
        else:
            with ui.column().classes(
                'left-panel-compact w-[220px] border-r border-gray-200 h-full min-h-0 flex flex-col '
                'overflow-hidden bg-white shrink-0'
            ):
                with ui.row().classes(
                    'w-full items-center justify-end px-2 py-1 bg-gray-50 border-b border-gray-200 shrink-0'
                ):
                    ui.button(
                        icon='chevron_left',
                        on_click=lambda: _set_sidebar_collapsed(True),
                    ).props('flat round dense').tooltip(tr_fn('sidebar.collapse'))
                sidebar_content()

        with ui.column().classes(
            'flex-1 h-full min-h-0 overflow-hidden flex flex-col bg-gray-100 relative'
        ):
            render_canvas_toolbar()

            @ui.refreshable
            def scene_kitchen_3d() -> None:
                render_kitchen_elements_scene_3d(
                    ui=ui,
                    state=state,
                    main_content_refresh=main_content_refresh,
                    wall_len_h=wall_len_h,
                    zone_baseline_and_height=zone_baseline_and_height,
                    get_zone_depth_standard=get_zone_depth_standard,
                )

            with ui.element('div').classes('flex-1 min-h-0 w-full relative overflow-visible'):
                with ui.element('div').classes(
                    'absolute inset-0 overflow-hidden p-2 flex items-center justify-center'
                ):
                    if str(getattr(state, 'element_canvas_mode', '2D')).upper() == '3D':
                        scene_kitchen_3d()
                    else:
                        nacrt_render()

                # Kontrole kamere — vidljivo samo u 3D modu
                if str(getattr(state, 'element_canvas_mode', '2D')).upper() == '3D':
                    with ui.element('div').classes(
                        'absolute bottom-4 right-4 z-10 flex flex-col gap-1 items-end'
                    ):
                        # Info o kontrolama — ikona sa tooltip-om
                        ui.icon('info_outline').classes(
                            'text-gray-400 text-lg cursor-help'
                        ).tooltip(
                            'Rotacija: levi klik + vuci\n'
                            'Pan (pomeri pogled): desni klik + vuci  ili  Shift + levi klik\n'
                            'Strelice ↑↓←→: pomeri centar pogleda\n'
                            'Zum: skrol točkić'
                        )
                        # Preset pogledi
                        with ui.element('div').classes('flex flex-col gap-1'):
                            if set_3d_camera_preset is not None:
                                ui.button(
                                    icon='vertical_align_top',
                                    on_click=lambda: set_3d_camera_preset(ui, 'top'),
                                ).props('round dense').classes(
                                    'bg-white text-gray-700 shadow border border-gray-200'
                                ).tooltip('Odozgo')
                                ui.button(
                                    icon='chevron_left',
                                    on_click=lambda: set_3d_camera_preset(ui, 'left'),
                                ).props('round dense').classes(
                                    'bg-white text-gray-700 shadow border border-gray-200'
                                ).tooltip('Leva strana')
                                ui.button(
                                    icon='chevron_right',
                                    on_click=lambda: set_3d_camera_preset(ui, 'right'),
                                ).props('round dense').classes(
                                    'bg-white text-gray-700 shadow border border-gray-200'
                                ).tooltip('Desna strana')
                        # Reset / Home dugme
                        if reset_3d_camera_home is not None:
                            ui.button(
                                icon='home',
                                on_click=lambda: reset_3d_camera_home(ui),
                            ).props('round dense').classes(
                                'bg-gray-800 text-white shadow-md border border-gray-700'
                            ).tooltip('Početni pogled')
