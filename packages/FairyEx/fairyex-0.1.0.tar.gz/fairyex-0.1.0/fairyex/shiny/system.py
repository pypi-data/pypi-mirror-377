import shiny
import shiny.express as shinex
from shiny import App, reactive, render, ui

from fairyex.darktype import DarkSys


darksys = DarkSys.from_ods("/home/harry/Téléchargements/system.ods")


nav_objects = ui.sidebar(
    ui.layout_columns(
        ui.card_header("System"),
        ui.input_dark_mode(),
    ),
    ui.input_selectize("children_class", "Class", choices=darksys.query_class()),
    ui.input_selectize("category", "Category", choices=[]),
    ui.input_checkbox_group(
        "reverse",
        "Select all",
        ["objects", "properties"],
        inline=True,
    ),
    ui.input_selectize("children_name", "Objects", choices=[], multiple=True),
    ui.input_selectize("prop", "Properties", choices=[], multiple=True),
)
view_objects = ui.card(
    ui.card_header("Object"),
    ui.output_data_frame("objects"),
    full_screen=True,
)
view_attributes = ui.card(
    ui.card_header("Attribute"),
    ui.output_data_frame("attributes"),
    full_screen=True,
)
view_memberships = ui.card(
    ui.card_header("Membership"),
    ui.output_data_frame("memberships"),
    full_screen=True,
)
view_properties = ui.card(
    ui.card_header("Property"),
    ui.output_data_frame("properties"),
    full_screen=True,
)

app_ui = ui.page_fillable(
    ui.HTML('<h1 style="color: pink">FairyEx &sext;</h1>'),
    ui.layout_sidebar(
        nav_objects,
        ui.layout_columns(view_objects, view_attributes, view_memberships),
        ui.layout_columns(view_properties),
    ),
)


def server(input_controller, output_view, session_model):
    @render.data_frame
    def objects():
        class_name = shinex.input.children_class()
        objects_name = shinex.input.children_name()
        return render.DataGrid(darksys.extract_objects(class_name, objects_name))

    @render.data_frame
    def attributes():
        class_name = shinex.input.children_class()
        objects_name = shinex.input.children_name()
        return render.DataGrid(darksys.extract_attributes(class_name, objects_name))

    @render.data_frame
    def memberships():
        class_name = shinex.input.children_class()
        objects_name = shinex.input.children_name()
        return render.DataGrid(darksys.extract_memberships(class_name, objects_name))

    @render.data_frame
    def properties():
        class_name = shinex.input.children_class()
        category = shinex.input.category()
        category = category if category and category != "-" else None
        objects_name = shinex.input.children_name()
        prop = shinex.input.prop()
        return render.DataGrid(darksys.extract_properties(class_name, objects_name, prop))

    @reactive.effect
    def update_category():
        class_name = shinex.input.children_class()
        ui.update_selectize(
            "category",
            choices=["-"] + darksys.query_category(class_name),
            selected="-",
        )

    @reactive.effect
    def update_children():
        class_name = shinex.input.children_class()
        category = shinex.input.category()
        category = category if category and category != "-" else None
        kwargs = (
            dict(selected=darksys.query_children(class_name, category=category))
            if "objects" in shinex.input.reverse() else dict()
        )
        ui.update_selectize(
            "children_name",
            choices=darksys.query_children(class_name, category=category),
            **kwargs,
        )

    @reactive.effect
    def update_property():
        class_name = shinex.input.children_class()
        kwargs = (
            dict(selected=darksys.query_property(class_name))
            if "properties" in shinex.input.reverse() else dict()
        )
        ui.update_selectize("prop", choices=darksys.query_property(class_name), **kwargs)


app = App(app_ui, server)
app.run()
