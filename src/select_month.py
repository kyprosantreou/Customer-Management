import flet as ft

dropdown = ft.Dropdown(
    width = 250,
    hint_text = "Select Month.",
    options=[
        ft.dropdown.Option("January"),
        ft.dropdown.Option("February"),
        ft.dropdown.Option("March"),
        ft.dropdown.Option("April"),
        ft.dropdown.Option("May"),
        ft.dropdown.Option("June"),
        ft.dropdown.Option("July"),
        ft.dropdown.Option("August"),
        ft.dropdown.Option("September"),
        ft.dropdown.Option("October"),
        ft.dropdown.Option("November"),
        ft.dropdown.Option("December"),
    ],
)

dropdown_year = ft.Dropdown(
    width = 250,
    hint_text = "Select Year.",
    options=[
        ft.dropdown.Option("2020"),
        ft.dropdown.Option("2021"),
        ft.dropdown.Option("2022"),
        ft.dropdown.Option("2023"),
        ft.dropdown.Option("2024"),
        ft.dropdown.Option("2025"),
        ft.dropdown.Option("2026"),
        ft.dropdown.Option("2027"),
        ft.dropdown.Option("2028"),
        ft.dropdown.Option("2029"),
        ft.dropdown.Option("2030"),
    ],
)

