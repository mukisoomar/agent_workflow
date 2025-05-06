# TAL Technical Specifications: inventory_system

## 1. Program Description

The `inventory_system` program provides a basic, interactive command-line interface for managing a simple product inventory. It allows users to perform common inventory operations such as adding, deleting, updating, and querying items, as well as generating a basic report. The program utilizes global variables, structures, arrays, pointers, and subprocedures to organize its data and logic. It also demonstrates interaction with external procedures for tasks like transaction logging. Error handling is implemented to provide feedback on invalid operations or system issues.

## 2. Input Parameters

The main program entry point (`main_proc`) does not accept command-line arguments. Input is primarily handled interactively through the `read_command` subprocedure, which (in a complete implementation) would read user input from the terminal to select menu options.

**Subprocedure Input Parameters:**

*   **`read_command(INT REF cmd_code)`**:
    *   `cmd_code` (Integer, Reference): An integer variable passed by reference, which will be updated by the procedure to contain the numeric command code entered by the user.
*   **`write_line(STRING line; INT len)`**:
    *   `line` (String, Value): The string data to be written to the output device.
    *   `len` (Integer, Value): The number of characters from the `line` string to write.
*   **`write(STRING line; INT len)`**:
    *   `line` (String, Value): The string data to be written to the output device.
    *   `len` (Integer, Value): The number of characters from the `line` string to write.
*   **`log_transaction(INT cmd; INT count)`** (External):
    *   `cmd` (Integer, Value): The command code being logged.
    *   `count` (Integer, Value): The current transaction count.

## 3. Return Value

The `main_proc` procedure returns an integer status code to the operating system upon completion.

*   **`success` (0)**: Indicates successful execution and normal termination.
*   Other values could potentially be returned in error scenarios, although the current implementation primarily returns `success`.

## 4. Core Logic/Processing Steps

1.  **Initialization**:
    *   The global string pointer `buffer` is allocated and initialized with spaces (`buffer_size` characters).
    *   The `initialize_inventory` subprocedure is called to populate the global `inventory` array with predefined sample item records and set the initial `inventory_count`.
2.  **Main Command Loop**:
    *   The program enters a `WHILE` loop that continues as long as the user command (`cmd`) is not equal to 6 (EXIT).
    *   **Display Menu**: The `display_menu` subprocedure is called to print the available command options (ADD, DELETE, UPDATE, QUERY, REPORT, EXIT) to the user, using the `command_codes` and `command_names` arrays.
    *   **Read Command**: The `read_command` subprocedure is called to obtain the user's desired command code (currently a stub that defaults to 6).
    *   **Process Command**: A `CASE` statement evaluates the entered `cmd`:
        *   Commands 1-5 call the corresponding stub procedures: `add_item`, `delete_item`, `update_item`, `query_item`, `generate_report`.
        *   Command 6 does nothing, causing the `WHILE` loop condition to become false on the next iteration.
        *   Any other command value sets the global `error_code` to `error_invalid_input` and calls `print_error` to display the error message.
    *   **Log Transaction**: If the command was not EXIT (6), the global `transaction_count` is incremented, and the external procedure `log_transaction` is called with the command code and new transaction count.
3.  **Cleanup/Termination**:
    *   After the loop terminates (command 6 entered), the address of the global `error_code` is assigned to the global pointer `error_ptr`.
    *   A check is performed (though somewhat redundant in this context) to see if `error_ptr` is non-null.
    *   If `error_code` is not `success` (0), the `print_error` procedure is called one last time.
    *   A demonstration block shows accessing fields via a structure pointer (`current_customer`) and manipulating bit fields (`is_active`, `tax_exempt`, `reserved`) if the inventory is not empty. (Note: `current_customer` is not explicitly allocated or assigned to a specific record in this sample).
    *   The program returns the `success` status code (0).

## 5. Dependencies

**Internal Subprocedures Called:**

*   `initialize_inventory`: Populates initial inventory data.
*   `display_menu`: Shows the user menu.
*   `read_command`: Reads user command input (stub).
*   `add_item`: Placeholder for adding inventory items (stub).
*   `delete_item`: Placeholder for deleting inventory items (stub).
*   `update_item`: Placeholder for updating inventory items (stub).
*   `query_item`: Placeholder for querying inventory items (stub).
*   `generate_report`: Placeholder for generating an inventory report (stub).
*   `print_error`: Displays error messages based on `error_code`.
*   `write_line`: Writes a string line to output (stub).
*   `write`: Writes a string to output without newline (stub).

**External Procedures Called:**

*   `log_transaction`: Assumed to log transaction details externally.

**External Procedures Declared (Not Called):**

*   `fetch_customer_data`

**Global Variables Used:**

*   `error_code`: Stores the last error status.
*   `error_messages`: Array of error message strings.
*   `transaction_count`: Counter for processed transactions.
*   `inventory`: Array storing `item_record` structures.
*   `inventory_count`: Current number of items in the `inventory` array.
*   `error_ptr`: Pointer intended to hold the address of `error_code`.
*   `current_customer`: Pointer to a `customer_record` structure.
*   `buffer`: General-purpose string buffer pointer.
*   `command_codes`: Array of numeric command codes for the menu.
*   `command_names`: Array of string command names for the menu.
*   `last_error`: Equivalence (alias) for `error_code`.
*   `buffer_length`: Equivalence for a system global location (example).
*   `inventory_io`: Block structure (declared, not used).

**Data Structures Defined:**

*   `item_record`: Structure defining inventory item attributes.
*   `customer_record`: Structure defining customer attributes.

**Literals Defined:**

*   `max_items`, `max_customers`, `buffer_size`, `success`, `error_file_not_found`, `error_invalid_input`, `error_system`.

**System Globals Declared (Not Used):**

*   `system_time`

## 6. Usage Examples or Edge Cases

*   **Standard Usage**: The user runs the program, sees the menu, enters a number (1-6), and the corresponding action (or stub message) is executed. Entering 6 exits the program.
*   **Stub Functionality**: Most core inventory operations (`add`, `delete`, `update`, `query`, `report`) and I/O (`read_command`, `write_line`, `write`) are implemented as stubs. They print a message indicating they were called but do not perform the actual logic.
*   **Input Validation**: Basic input validation exists in the main loop's `CASE` statement. Entering a number outside the 1-6 range triggers an "Invalid input" error message via `print_error`. The `read_command` stub itself does not perform input validation.
*   **Error Handling**: Errors are signaled by setting the global `error_code`. The `print_error` procedure looks up the corresponding message in the `error_messages` array. Unknown error codes result in a generic message.
*   **Fixed Array Size**: The inventory is stored in a fixed-size array (`inventory[0:max_items-1]`). The program does not handle cases where the inventory becomes full if `add_item` were fully implemented.
*   **Pointer Usage**: The code demonstrates assigning the address of a variable to a pointer (`error_ptr := @error_code`) and accessing structure fields via a pointer (`current_customer.is_active`). Note that `current_customer` is used without explicit memory allocation or assignment to a specific customer instance in this example, which would be required in a real application.
*   **Bit Manipulation**: The `customer_record` structure and the example code demonstrate packing boolean flags (`is_active`, `has_credit`, `tax_exempt`) into single bits within an integer word.
*   **External Calls**: The program relies on an external `log_transaction` procedure, which must be available and linked for the program to run completely.
*   **Default Exit**: The `read_command` stub currently defaults the command code to 6 (EXIT). This prevents the program from looping indefinitely if run as-is but means the other command stubs won't be reached without modifying the `read_command` stub.