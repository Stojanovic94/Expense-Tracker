import os  # Module for interacting with the operating system
import csv  # Module for reading and writing CSV files
import tkinter as tk  # Tkinter module for creating the GUI
from tkinter import ttk  # Module for themed widgets
from tkcalendar import DateEntry  # Widget for date selection
from datetime import datetime  # Module for date and time manipulations
from collections import defaultdict  # For category totals

# Global variable to track the sort order of the columns in the treeview
sort_order = {
    'date': False,  # False means ascending order; True means descending order
    'category': False,
    'amount': False
}

# Create a dictionary to hold category totals and averages
category_totals = defaultdict(float)  # Total amount per category
category_counts = defaultdict(int)      # Count of expenses per category

def validate_amount_input(P):
    """ Validate the input for the amount entry field.
    Allow empty input, integers, or floats with one decimal point. """
    if P == "" or P.isdigit() or (P.count('.') < 2 and P.replace('.', '').isdigit()):
        return True  # Valid input
    else:
        return False  # Invalid input

def add_expense():
    """ Add a new expense to the CSV file and refresh the displayed list. """
    date = date_entry.get()  # Get date from the date entry
    category = category_combobox.get()  # Get selected category
    amount = amount_entry.get()  # Get amount from the entry

    if date and category and amount:
        # Append the new expense to the CSV file
        with open("finances.csv", "a", newline="") as file:
            writer = csv.writer(file)
            writer.writerow([date, category, amount])  # Write the new row

        # Update category totals and counts immediately after adding the expense
        category_totals[category] += float(amount)  # Update the total for the category
        category_counts[category] += 1  # Increment count for the category

        status_label.config(text="Expense added successfully!", fg="green")  # Update status
        clear_entries()  # Clear the input fields
        view_expenses()  # Refresh the expense list
        update_category_summary()  # Update category totals and averages
    else:
        status_label.config(text="Please fill all the fields!", fg="red")  # Error message
        
def delete_expense():
    """ Delete the selected expense from the CSV file and refresh the list. """
    selected_item = expenses_tree.selection()  # Get the selected item in the treeview
    if selected_item:
        item_text = expenses_tree.item(selected_item, "values")  # Get values of the selected item
        date, category, amount = item_text  # Unpack the values
        # Read current expenses and write back to the CSV without the deleted entry
        with open("finances.csv", "r") as file:
            lines = file.readlines()  # Read all lines in the CSV
        with open("finances.csv", "w", newline="") as file:
            for line in lines:
                if not line.startswith(f"{date},{category},{amount}"):  # Exclude the line to delete
                    file.write(line)  # Write back the remaining lines
        status_label.config(text="Expense deleted successfully!", fg="green")  # Update status
        view_expenses()  # Refresh the expense list
    else:
        status_label.config(text="Please select an expense to delete!", fg="red")  # Error message

def edit_expense():
    """ Load selected expense data into the input fields for editing. """
    selected_item = expenses_tree.selection()  # Get selected item in the treeview
    if selected_item:
        item_text = expenses_tree.item(selected_item, "values")  # Get values of the selected item
        date, category, amount = item_text  # Unpack values
        date_entry.set_date(date)  # Set date in the date entry
        category_combobox.set(category)  # Set selected category
        amount_entry.delete(0, tk.END)  # Clear amount entry
        amount_entry.insert(0, amount)  # Insert the amount
        expenses_tree.delete(selected_item)  # Temporarily remove the item from the treeview
        add_button.config(text="Update Expense", command=lambda: update_expense(date, category))  # Change button to update

def update_expense(old_date, old_category):
    """ Update the expense with new values. """
    date = date_entry.get()  # Get new date
    category = category_combobox.get()  # Get new category
    amount = amount_entry.get()  # Get new amount

    if date and category and amount:
        with open("finances.csv", "r") as file:
            lines = file.readlines()  # Read all lines in the CSV

        with open("finances.csv", "w", newline="") as file:
            for line in lines:
                if line.startswith(f"{old_date},{old_category}"):  # Match old entry
                    writer = csv.writer(file)
                    writer.writerow([date, category, amount])  # Write updated values
                else:
                    file.write(line)  # Write back the remaining lines

        status_label.config(text="Expense updated successfully!", fg="green")  # Update status
        clear_entries()  # Clear the input fields
        add_button.config(text="Add Expense", command=add_expense)  # Reset the button
        view_expenses()  # Refresh the expense list
    else:
        status_label.config(text="Please fill all the fields!", fg="red")  # Error message

def clear_entries():
    """ Clear all input fields. """
    date_entry.set_date(datetime.now().date())  # Reset date to today
    category_combobox.set('')  # Clear selected category
    amount_entry.delete(0, tk.END)  # Clear amount entry

def view_expenses():
    """ Display all expenses in the treeview and update total expenses and averages. """
    global expenses
    expenses_tree.delete(*expenses_tree.get_children())  # Clear the treeview
    expenses = []  # Reset expenses list
    category_totals.clear()  # Clear previous totals
    category_counts.clear()  # Clear previous counts

    if os.path.exists("finances.csv"):  # Check if the file exists
        with open("finances.csv", "r") as file:
            reader = csv.reader(file)
            next(reader, None)  # Skip header
            for row in reader:
                if len(row) == 3:  # Ensure there are three columns
                    date, category, amount = row
                    expenses.append(row)  # Add row to expenses list
                    expenses_tree.insert("", tk.END, values=row)  # Insert into the treeview

                    # Update category totals and counts
                    category_totals[category] += float(amount)  # Add to total for the category
                    category_counts[category] += 1  # Increment count for the category

    update_total_expenses()  # Update total expenses display
    update_category_summary()  # Update category totals and averages
    
def update_total_expenses():
    """ Calculate and display the total amount of expenses. """
    total = sum(float(expense[2]) for expense in expenses if expense[2].replace('.', '', 1).isdigit())  # Calculate total
    if total_label.winfo_exists():  # Check if total_label still exists
        total_label.config(text=f"Total Expenses: ${total:.2f}")  # Update total label
        
def update_category_summary():
    """ Calculate and display the total and average amount of expenses per category. """
    summary_text.config(state=tk.NORMAL)  # Allow editing
    summary_text.delete(1.0, tk.END)  # Clear previous summary
    summary_text.insert(tk.END, "Category Summary:\n--------------------\n")  # Insert header
    for category, total in category_totals.items():
        avg = total / category_counts[category] if category_counts[category] > 0 else 0  # Calculate average
        summary_text.insert(tk.END, f"{category}:\n  Average = ${avg:.2f}\n  Total = ${total:.2f}\n--------------------\n")  # Insert new summary text
    summary_text.config(state=tk.DISABLED)  # Make the text box read-only

def sort_treeview(col):
    """ Sort the treeview by the specified column. """
    global sort_order, expenses
    sort_order[col] = not sort_order[col]  # Toggle sort order

    # Sort expenses based on the column and current sort order
    if col == 'date':
        expenses.sort(key=lambda x: datetime.strptime(x[0], "%Y-%m-%d"), reverse=sort_order[col])
    elif col == 'category':
        expenses.sort(key=lambda x: x[1], reverse=sort_order[col])
    elif col == 'amount':
        expenses.sort(key=lambda x: float(x[2]), reverse=sort_order[col])

    # Clear the treeview and reinsert sorted data
    expenses_tree.delete(*expenses_tree.get_children())
    for row in expenses:
        expenses_tree.insert("", tk.END, values=row)

# Create the main application window
root = tk.Tk()
root.title("Expense Tracker")  # Set the window title
root.resizable(False, False)  # Disable window resizing

# Create labels and entries for adding expenses
date_label = tk.Label(root, text="Date:")
date_label.grid(row=0, column=0, padx=5, pady=5)  # Place date label in the grid

date_entry = DateEntry(root, date_pattern="yyyy-mm-dd", width=12)  # Date entry field
date_entry.grid(row=0, column=1, padx=5, pady=5)  # Place date entry in the grid

category_label = tk.Label(root, text="Category:")
category_label.grid(row=0, column=2, padx=5, pady=5)  # Place category label in the grid

category_combobox = ttk.Combobox(root, values=[
    "Food: Groceries",
    "Food: Dining",
    "Housing: Rent",
    "Housing: Utils",
    "Transport: Fuel",
    "Transport: Public",
    "Transport: Car Maint",
    "Health: Insurance",
    "Health: Medical",
    "Health: Fitness",
    "Entertainment: Movies",
    "Entertainment: Subs",
    "Entertainment: Hobbies",
    "Clothing: Apparel",
    "Education: Tuition",
    "Education: Supplies",
    "Personal Care: Hair",
    "Misc: Gifts",
    "Savings: Retirement",
    "Savings: Emergency"
])  # Category selection  # Category selection
category_combobox.grid(row=0, column=3, padx=5, pady=5)  # Place category combobox in the grid

amount_label = tk.Label(root, text="Amount:")
amount_label.grid(row=0, column=4, padx=5, pady=5)  # Place amount label in the grid

amount_entry = tk.Entry(root, validate="key")  # Amount entry field
amount_entry['validatecommand'] = (amount_entry.register(validate_amount_input), '%P')  # Validate input
amount_entry.grid(row=0, column=5, padx=5, pady=5)  # Place amount entry in the grid

add_button = tk.Button(root, text="Add Expense", command=add_expense)  # Button to add expense
add_button.grid(row=0, column=6, padx=5, pady=5)  # Place button in the grid

edit_button = tk.Button(root, text="Edit Expense", command=edit_expense)  # Button to edit expense
edit_button.grid(row=0, column=7, padx=5, pady=5)  # Place button in the grid

delete_button = tk.Button(root, text="Delete Expense", command=delete_expense)  # Button to delete expense
delete_button.grid(row=0, column=8, padx=5, pady=5)  # Place button in the grid

# Create a status label to display messages
status_label = tk.Label(root, text="", fg="red")  # Error messages in red
status_label.grid(row=1, column=0, columnspan=8, padx=5, pady=5)  # Place status label in the grid

# Create a treeview to display expenses
columns = ("date", "category", "amount")  # Define treeview columns
expenses_tree = ttk.Treeview(root, columns=columns, show="headings", height=10)  # Create treeview
expenses_tree.grid(row=2, column=0, columnspan=9, padx=5, pady=5, sticky="nsew")  # Place treeview in the grid

# Create a vertical scrollbar for the treeview
scrollbar = ttk.Scrollbar(root, orient="vertical", command=expenses_tree.yview)  # Vertical scrollbar
scrollbar.grid(row=2, column=9, sticky='ns')  # Place scrollbar in the grid
expenses_tree.configure(yscroll=scrollbar.set)  # Link scrollbar to treeview

# Set headings and command for sorting
expenses_tree.heading("date", text="Date", command=lambda: sort_treeview('date'))  # Sort by date
expenses_tree.heading("category", text="Category", command=lambda: sort_treeview('category'))  # Sort by category
expenses_tree.heading("amount", text="Amount", command=lambda: sort_treeview('amount'))  # Sort by amount

# Create a label for displaying total expenses
total_label = tk.Label(root, text="Total Expenses: $0.00")  # Label for total expenses
total_label.grid(row=3, column=0, columnspan=9, padx=5, pady=5)  # Place label in the grid

# Create a text box for displaying category totals and averages
summary_text = tk.Text(root, height=10, width=30)  # Text box for category summary
summary_text.grid(row=4, column=0, columnspan=9, padx=5, pady=5, sticky='nsew')  # Place text box in the grid
summary_text.config(state=tk.NORMAL)  # Allow editing (optional)
summary_text.insert(tk.END, "Category Summary:\n--------------------\n")  # Insert initial text
summary_text.config(state=tk.DISABLED)  # Make the text box read-only

# Set up grid weights for proper resizing
root.grid_rowconfigure(2, weight=1)  # Allow row 2 (treeview) to resize
root.grid_columnconfigure(0, weight=1)  # Allow column 0 to resize
root.grid_columnconfigure(9, weight=0)  # Scrollbar does not need to resize

view_expenses()  # Load expenses when the application starts

# Run the application
root.mainloop()
