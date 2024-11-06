import os
import datetime
import flet as ft
from flet import *
import pandas as pd
import mysql.connector
from openpyxl import *
from greedings import *
from select_month import *
from is_decimal import is_decimal

def main(page: ft.Page):

    greetings = Greedings()

    # Establish a connection to the MySQL database
    try:
        mydb = mysql.connector.connect(
            host="",
            user="",
            password="",
            database=""
        )

        cursor = mydb.cursor()
        # Create the customer table with a case-sensitive collation for relevant columns
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS customer (
                customer_name VARCHAR(255) COLLATE utf8_bin NOT NULL,
                customer_id INT NOT NULL
            )
        ''')

        # Create the management table with a case-sensitive collation for relevant columns
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS management (
                customer_name VARCHAR(255) COLLATE utf8_bin NOT NULL,
                customer_id INT NOT NULL,
                liters FLOAT NOT NULL,
                invoice_number INT NOT NULL,
                invoice_date DATE NOT NULL
            )
        ''')

        mydb.commit()

    except mysql.connector.Error as err:
        print("MySQL Error: {}".format(err))

    def register_new_customer(e):
        customer_name = new_customer_name_textfield.value
        customer_id = new_customer_id_textfield.value

        cursor = mydb.cursor()

        # Check if the customer_id already exists in the database
        cursor.execute("SELECT customer_id FROM customer WHERE customer_id = %s", (customer_id,))
        result = cursor.fetchone()

        if result:
            register_message.value = "This customer or this id is already registered."
        elif new_customer_name_textfield.value == "":
            register_message.value = "Complete all the fields."
        elif not customer_id.isdigit():
            register_message.value = "Customer ID must be a numeric value."
        else:
            try:
                cursor.execute("INSERT INTO customer (customer_name, customer_id) VALUES (%s,%s)", (customer_name, customer_id))
                mydb.commit()
                register_message.value = "Customer registered successfully."
            except mysql.connector.Error as e:
                register_message.value = "An error occurred: " + str(e)
        
        page.update()
    
    def submit(e):
        customer_name = customer_name_textfield.value
        customer_id = customer_id_textfield.value
        liters = liters_textfield.value
        invoice_number = invoice_number_textfield.value
        invoice_date = date_textfield.value

        cursor = mydb.cursor()

        # Check if all fields are filled
        if (customer_name == "" or customer_id == "" 
            or liters == "" or invoice_number == "" 
            or invoice_date == ""):
            submit_message.value = "Complete all the fields."
            page.update()
            return

        # Check if invoice_number consists of only digits
        if not invoice_number.isdigit():
            submit_message.value = "Invoice number must be digits."
            page.update()
            return

        # Check if liters consists of only digits
        if not (liters.isdigit() or is_decimal(liters)):
            submit_message.value = "Liters must be digits."
            page.update()
            return

        if not customer_id.isdigit():
            submit_message.value = "Customer id must be digits."
            page.update()
            return

        try:
            # Parse the date string into a datetime object
            invoice_date_obj = datetime.strptime(invoice_date, "%d/%m/%Y")
            # Format the datetime object into MySQL's date format
            formatted_invoice_date = invoice_date_obj.strftime("%Y-%m-%d")
        except ValueError:
            submit_message.value = "Invalid date format. Please use Y-m-d"
            page.update()
            return

        # Check if the customer_id already exists in the database
        cursor.execute("SELECT customer_name, customer_id FROM customer WHERE BINARY customer_name = %s AND BINARY customer_id = %s", (customer_name, customer_id ))
        result = cursor.fetchone()

        if not result:
            submit_message.value = "Customer not found."
        elif result:
            try:
                cursor.execute("""
                    INSERT INTO management (
                        customer_name, customer_id, 
                        liters, invoice_number, invoice_date
                    ) VALUES (%s, %s, %s, %s, %s)
                    """, 
                    (customer_name, customer_id, liters, invoice_number, formatted_invoice_date)
                )
                mydb.commit()
                submit_message.value = "Details submitted successfully."
            except mysql.connector.Error as e:
                submit_message.value = "An error occurred: " + str(e)

        page.update()

    def export(e):

        try:

            cursor = mydb.cursor()

            selected_month = dropdown.value 
            month_number = datetime.strptime(selected_month, "%B").month

            selected_year = dropdown_year.value
            
            # Query data from the MySQL database
            cursor.execute("SELECT invoice_date, invoice_number, customer_name, customer_id, liters FROM management WHERE MONTH(invoice_date) = %s AND YEAR(invoice_date) = %s", (month_number, selected_year))

            # Fetch all rows
            data = cursor.fetchall()

            if not data:
                export_message.value = f"No data found for {selected_month} {selected_year}."
                page.update()
                return
            else:
                # Extract column names from cursor description
                columns = [i[0] for i in cursor.description]

                # Create a DataFrame
                df = pd.DataFrame(data, columns=['invoice_date', 'invoice_number', 'customer_name', 'customer_id', 'liters'])

                # Convert date column to the desired format
                df['invoice_date'] = pd.to_datetime(df['invoice_date']).dt.strftime('%d/%m/%y')

                # Specify the directory to save the Excel file
                desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")
                directory = os.path.join(desktop_path, "CustomerDataManagement")

                # Check if the directory exists, if not, create it
                if not os.path.exists(directory):
                    os.makedirs(directory)

                # Write the DataFrame to an Excel file
                excel_filename = os.path.join(directory, f"{selected_month}_{selected_year}.xlsx")
                try:
                    with pd.ExcelWriter(excel_filename) as writer:
                        df.to_excel(writer, index=False)
                except PermissionError:
                    export_message.value = "Permission denied: Close the opened Excel file\nor check directory permissions."
                    page.update()
                    return

                export_message.value = f"Data for {selected_month} {selected_year} successfully exported to\nyour desktop in CustomerDataManagement folder."
                page.update()

        except mysql.connector.Error as err:
            print("MySQL Error:", err)

        page.update()

    new_customer_button = ft.ElevatedButton(text = "New customer?",
                                            width = 500, 
                                            color = "White",
                                            style = ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=10)),
                                            on_click=lambda _: page.go("/New Customer"),
                                        )
    
    existing_customer_button = ft.ElevatedButton(text = "Existing customer?",
                                            width = 500, 
                                            color = "White",
                                            style = ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=10)),
                                            on_click=lambda _: page.go("/Existing Customer"),
                                        )

    statements_button = ft.ElevatedButton(text = "Export Statements",
                                            width = 500, 
                                            color = "White",
                                            style = ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=10)),
                                            on_click=lambda _: page.go("/statements"),
                                        )
    
    new_customer_name_textfield = ft.TextField(label="New Customer Name", width = 450)
    new_customer_id_textfield = ft.TextField(label="New Customer ID", width = 450)

    register_new_user_button = ft.ElevatedButton(text = "Register New Customer",
                                                    width = 350, 
                                                    color = "White",
                                                    style = ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=10)),
                                                    on_click = register_new_customer 
                                                )
    
    register_message = ft.Text(visible=True, selectable=True, size=18)
    submit_message = ft.Text(visible=True, selectable=True, size=18)
    export_message = ft.Text(visible=True, selectable=True, size=18)

    customer_name_textfield = ft.TextField(label="Customer Name", width = 250)
    customer_id_textfield = ft.TextField(label="Customer ID", width = 250)
    invoice_number_textfield = ft.TextField(label="Invoice Number", width = 250)
    liters_textfield = ft.TextField(label="Liters", width = 250)

    submit_button = ft.ElevatedButton(text = "Submit",
                                        width = 350, 
                                        color = "White",
                                        style = ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=10)),
                                        on_click = submit,
                                    )

    export_button = ft.ElevatedButton(text = "Export",
                                        width = 350, 
                                        color = "White",
                                        style = ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=10)),
                                        on_click = export,
                                    )
    
    date_textfield = ft.TextField(label="Invoice Date", width = 250,read_only=True)

    def change_date(e):
        date_textfield.value = format_date(date_picker.value)
        page.update()

    def date_picker_dismissed(e):
        print(f"Date picker dismissed, value is {format_date(date_picker.value)}")

    def format_date(date):
        if date is not None:
            return date.strftime("%d/%m/%Y")
        else:
            print("Error: Date object is None")
            return ""

    date_picker = ft.DatePicker(
        on_change = change_date,
        on_dismiss = date_picker_dismissed,
        first_date = datetime(2020, 10, 1),
        last_date = datetime(2030, 10, 1),
    )

    page.overlay.append(date_picker)

    date_button = ft.ElevatedButton(
        "Pick date",
        icon=ft.icons.CALENDAR_MONTH_SHARP,
        on_click=lambda _: date_picker.pick_date(),
        style = ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=2.5)),
        width = 250,
        height = 50,
        color = "White",
    )

    def route_change(route):
        
        page.views.clear()

        page.views.append(
                ft.View(
                    "/",
                    [
                        ft.AppBar(title=ft.Text(f"              {greetings} Boss!",  
                                            weight=ft.FontWeight.BOLD, size=30, color="White"
                                        ), 
                                        bgcolor="#0f2938"
                                ),

                        ft.Divider(height=75,color="transparent"),

                        Row(
                            alignment="center",
                            controls=[
                                ft.Icon(name=ft.icons.PERSON_ROUNDED, color=ft.colors.WHITE,size=45,scale=ft.Scale(4)),
                            ],
                        ),

                        ft.Divider(height=75,color="transparent"),

                        Row(
                            controls=[
                                Column(
                                    [
                                        new_customer_button,
                                        existing_customer_button,
                                        statements_button
                                    ],
                                )
                            ],
                            alignment=ft.MainAxisAlignment.CENTER,
                        ),
                    ],
                )
            )

        if page.route == "/Existing Customer":
            page.views.append(
                ft.View(
                    "/Existing Customer",
                    [
                        ft.AppBar(title=ft.Text("           Existing Customer",
                                                weight=ft.FontWeight.BOLD, 
                                                size=30, 
                                                color="White",
                                                ), 
                                                bgcolor="#0f2938"
                                ),
                        
                        ft.Divider(height=80,color="transparent"),
                        
                        Row(
                            alignment="center",

                            controls=[
                                customer_name_textfield,
                                customer_id_textfield,
                            ],
                        ),

                        Row(
                            alignment="center",
                            controls=[
                                invoice_number_textfield,
                                liters_textfield,
                            ],
                        ),

                        Row(
                            alignment="center",
                            controls=[
                                date_textfield,
                                date_button,
                            ],
                        ),

                        Row(
                            alignment="center",
                            controls=[
                                Column(
                                    [
                                        submit_button,
                                    ],
                                ),
                            ],
                        ),

                        Row(
                            alignment="center",
                            controls=[
                                Column(
                                    [
                                        submit_message,
                                    ],
                                ),
                            ],
                        ),

                    ],
                )
            )

        page.theme_mode = ft.ThemeMode.DARK
        page.update()

        if page.route == "/New Customer":
            page.views.append(
                ft.View(
                    "/New Customer",
                    [
                        ft.AppBar(title=ft.Text("             New Customer",
                                                weight=ft.FontWeight.BOLD, 
                                                size=30, 
                                                color="White",
                                                ), 
                                    bgcolor="#0f2938"
                                ),

                        Row(
                            alignment="center",

                            controls=[
                                ft.Text(visible=True, selectable=True, size=25, weight=FontWeight.W_400,
                                        spans=[
                                        ft.TextSpan(
                                            "Register your new customer.",
                                            ft.TextStyle(decoration=ft.TextDecoration.UNDERLINE),
                                        )
                                    ]
                                )
                                ],
                            ),
                        
                        ft.Divider(height=60,color="transparent"),
                        
                        Row(
                            alignment="center",
                            controls=[
                                Column(
                                    [
                                        new_customer_name_textfield,
                                        new_customer_id_textfield,
                                    ],
                                ),
                            ],
                        ),

                        Row(
                            alignment="center",
                            controls=[
                                Column(
                                    [
                                        register_new_user_button,
                                        register_message,
                                    ],
                                ),
                            ],
                        ),

                    ],
                )
            )

            page.theme_mode = ft.ThemeMode.DARK
            page.update()

        if page.route == "/statements":

            dropdown.value = "January"
            dropdown_year.value = "2024"
            page.update()

            page.views.append(
                ft.View(
                    "/statements",
                    [
                        ft.AppBar(title=ft.Text("           Export Statements",
                                                weight=ft.FontWeight.BOLD, 
                                                size=30, 
                                                color="White",
                                                ), 
                                                bgcolor="#0f2938"
                                ),
                        
                        Row(
                            alignment="center",

                            controls=[
                                ft.Text(visible=True, selectable=True, size=25, weight=FontWeight.W_400,
                                        spans=[
                                        ft.TextSpan(
                                            "Select month and export the statement.",
                                            ft.TextStyle(decoration=ft.TextDecoration.UNDERLINE),
                                        )
                                    ]
                                )
                                ],
                            ),

                        ft.Divider(height=80,color="transparent"),

                        Row(
                            alignment="center",
                            controls=[
                                dropdown,
                                dropdown_year,
                            ],
                        ),

                        Row(
                            alignment="center",
                            controls=[
                                Column(
                                    [
                                        export_button,
                                    ],
                                ),
                            ],
                        ),

                        Row(
                            alignment="center",
                            controls=[
                                Column(
                                    [
                                        export_message,
                                    ],
                                ),
                            ],
                        ),

                    ],
                )
            )

        page.theme_mode = ft.ThemeMode.DARK
        page.update()
        
        if page.route == "/":
            register_message.value = ""
            new_customer_id_textfield.value = ""
            new_customer_name_textfield.value = ""
            customer_id_textfield.value = ""
            customer_name_textfield.value = ""
            invoice_number_textfield.value = ""
            date_textfield.value = ""
            liters_textfield.value = ""
            submit_message.value = ""
            export_message.value = ""
            page.update()

    def view_pop(view):
        
        page.views.pop()
       
        top_view = page.views[-1]
        page.go(top_view.route)

    
    page.on_route_change = route_change
    page.on_view_pop = view_pop
    page.go(page.route)

    page.title = "Customer Management"
    page.window_height = 600
    page.window_width = 600
    page.window_resizable = False
    page.window_maximizable = False
    page.theme_mode = ft.ThemeMode.DARK
    page.window_center()
    
if __name__ == '__main__':
    ft.app(target=main)