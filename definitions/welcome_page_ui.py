from shiny import ui
from shinywidgets import output_widget

from faicons import icon_svg
from definitions.terms_and_styles import placeholder_panel

from .welcome_page_backend import reporter_colors
page_id = 'welcome'


def timeline_header():
    return(ui.div(
        ui.div("1",
        class_="timeline-header-div"),
         ui.div(
            ui.h2("Explore the timeline",
            class_="timeline-header-title"),
            ui.p("Select a wave to inspect its metadata and associated files")
            ),
            class_="timeline-header-undertitle"),
            ui.hr(
            class_="timeline-hr"),
            )

def information_about_wave():
    return ui.div(
        ui.span("Information about",
        class_="timeline-information-about-span"),
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
        class_="timeline-information-about-div"
    )

def welcome_page(tab_name):

    return ui.nav_panel(' Welcome!',
                        placeholder_panel('This *Timeline* plot is a placeholder, the age spans and assessment ids need to be cleaned and updated with additional info.' \
                            '&ensp;A **sample size overlap tool** based on the same data is also currently under development'),
                        ui.page_fluid(
                            timeline_header(),
                            information_about_wave(),
                            output_widget("timeline", fillable=True)),
                        icon=icon_svg('gamepad'),
                        value=tab_name)