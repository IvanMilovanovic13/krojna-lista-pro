# -*- coding: utf-8 -*-
from __future__ import annotations


def render_elements_tab(
    ui,
    state,
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
) -> None:
    """Renderuje ceo 'Elementi' tab (UI layout only)."""
    if not hasattr(state, 'element_canvas_mode'):
        setattr(state, 'element_canvas_mode', '2D')

    # Keep canvas fully visible under top toolbar/tab strip; prevent bottom clipping.
    with ui.row().classes('w-full h-[calc(100vh-72px)] gap-0 min-h-0 overflow-hidden'):
        with ui.column().classes(
            'left-panel-compact w-[260px] border-r border-gray-200 h-full min-h-0 flex flex-col '
            'overflow-hidden bg-white shrink-0'
        ):
            sidebar_content()

        with ui.column().classes(
            'flex-1 h-full min-h-0 overflow-hidden flex flex-col bg-gray-100 relative'
        ):
            render_canvas_toolbar(
                ui=ui,
                state=state,
                nacrt_refresh=nacrt_render.refresh,
                main_content_refresh=main_content_refresh,
                set_view_mode=set_view_mode,
                set_show_grid=set_show_grid,
                set_grid_mm=set_grid_mm,
                set_show_bounds=set_show_bounds,
                set_ceiling_filler=set_ceiling_filler,
            )

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
