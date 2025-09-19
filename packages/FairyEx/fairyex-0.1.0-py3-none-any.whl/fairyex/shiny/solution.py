import shiny
from shiny import reactive, render, ui
import shiny.express as shinex

from fairyex import DarkSol


PATH = "/home/harry/Model Base with Losses Solution.zip"


with DarkSol(path) as solution:
    app_ui_sidebar = ui.sidebar(
        ui.input_selectize(
            "phase_", "Phase", choices=solution.query_phase()
        ),
        ui.input_selectize(
            "class_", "Class", choices=solution.query_class()
        ),
        ui.input_selectize("category_", "Category", choices=[]),
        ui.input_selectize("child_", "Child", choices=[], multiple=True),
        ui.input_selectize("property_", "Properties", choices=[], multiple=True),
        ui.input_selectize(
            "sample_", "Samples", choices=solution.query_sample(), multiple=True
        ),
        ui.input_task_button("query_", "Execute"),
        width=360,
    )

    app_ui = ui.page_fillable(
        ui.HTML('<h1 style="color: pink">FairyEx &sext;</h1>'),
        ui.layout_sidebar(
            app_ui_sidebar,
            ui.output_data_frame("summary_data"),
            ui.input_dark_mode(),
        ),
        class_="p-3"
    )

    def server(user_input, screen_output, session):
        @render.data_frame
        @reactive.event(shinex.input.query_)
        def summary_data():
            return solution.queries(
                shinex.input.phase_(),
                "System",
                "System",
                shinex.input.class_(),
                shinex.input.child_(),
                shinex.input.property_(),
                shinex.input.sample_(),
            )

        @reactive.effect
        def update_category():
            class_name = shinex.input.class_()
            ui.update_selectize(
                "category_",
                choices=solution.query_category(class_name)
            )

        @reactive.effect
        def update_child():
            class_name = shinex.input.class_()
            category_name = shinex.input.category_()
            if category_name == '-':
                category_name = None
            ui.update_selectize(
                "child_",
                choices=solution.query_children(class_name, category_name)
            )

        @reactive.effect
        def update_property():
            class_name = shinex.input.class_()
            property_class = class_name.replace('y', "ie") + 's'
            ui.update_selectize(
                "property_",
                choices=solution.query_property(property_class)
            )


    app = shiny.App(app_ui, server)
    shiny.run_app(app)
