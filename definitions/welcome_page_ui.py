from shiny import ui
from shinywidgets import output_widget

from faicons import icon_svg
from definitions.terms_and_styles import placeholder_panel

from .welcome_page_backend import reporter_colors
page_id = 'welcome'

def information_about_wave():
    return ui.div(
        ui.span("Information about",
        style="""
        font-size:12px;
        margin:0;
        """),

        *[
            ui.div(
                ui.span("●", style=f"""
                color:{color};
                font-size:20px;
                """),
                ui.span(key),
                style="""
                display:flex; 
                align-items:center; 
                gap:4px;
                """
            )
            for key, color in reporter_colors.items()
        ],
        style="""
        display:flex; 
        align-items:center; 
        gap:12px;
        """
    )

def welcome_page(tab_name):

    return ui.nav_panel(' Welcome!',
                        placeholder_panel('This *Timeline* plot is a placeholder, the age spans and assessment ids need to be cleaned and updated with additional info.' \
                            '&ensp;A **sample size overlap tool** based on the same data is also currently under development'),
                        ui.page_fluid(

                            ui.div(
                                ui.div("1",
                                        style="""
                                        width:32px;
                                        height:32px;

                                        border-radius:50%;

                                        background-color:#F3F0FF;

                                        display:flex;
                                        align-items:center;
                                        justify-content:center;

                                        font-size:14px;
                                        font-weight:600;
                                        """),
                                ui.div(
                                    ui.h2("Explore the timeline",
                                    style="""
                                    font-size:22px;
                                    color:#2c3c94;
                                    margin:0;
                                    """),
                                    ui.p("Select a wave to inspect its metadata and associated files")
                                ),

                                style="""
                                display:flex;
                                gap:16px;
                                align-items:flex-start;
                                """
                            ),
                            ui.hr(
                                style="""
                                border:none;
                                border-top:1px solid;
                                margin-top:4px;
                                margin-bottom:6px;
                                """
                            ),
                            information_about_wave(),
                            output_widget("timeline", fillable=True)),
                        icon=icon_svg('gamepad'),
                        value=tab_name)