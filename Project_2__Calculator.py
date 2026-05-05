import tkinter as tk
import math
from datetime import datetime, timedelta

# ================= MAIN WINDOW =================
root = tk.Tk()
root.title("Calculator+ ")
root.geometry("520x760")
root.configure(bg="#1e1e1e")
root.resizable(False, False)

# ================= FRAMES =================
main_frame = tk.Frame(root, bg="#1e1e1e")
second_frame = tk.Frame(root, bg="#1e1e1e")
third_frame = tk.Frame(root, bg="#1e1e1e")

main_frame.pack(fill="both", expand=True)

history_records = []
BTN_PAD_X = 4
BTN_PAD_Y = 4


# ================= SWITCH FUNCTIONS =================
# Switch to scientific frame and hide others so only one calculator is visible at a time.
def show_second():
    main_frame.pack_forget()
    third_frame.pack_forget()
    second_frame.pack(fill="both", expand=True)


# Return to basic frame and hide scientific/programmer frames to avoid overlapping layouts.
def show_main():
    second_frame.pack_forget()
    third_frame.pack_forget()
    main_frame.pack(fill="both", expand=True)


# Switch to programmer frame because it has a different toolset and input flow.
def show_third():
    main_frame.pack_forget()
    second_frame.pack_forget()
    third_frame.pack(fill="both", expand=True)


# Detect active frame from focused widget so keyboard shortcuts can run the correct calculator action.
def widget_in_frame(widget, frame):
    parent = widget
    while parent is not None:
        if parent == frame:
            return True
        parent_name = parent.winfo_parent()
        parent = parent.nametowidget(parent_name) if parent_name else None
    return False


# Route Enter key to the active calculator's evaluate function for consistent '=' keyboard behavior.
def handle_enter(_event=None):
    focused = root.focus_get()
    if focused is None:
        return
    if widget_in_frame(focused, main_frame):
        calculate()
    elif widget_in_frame(focused, second_frame):
        sci_calc()
    elif widget_in_frame(focused, third_frame):
        prog_calc()


# Enforce 24-hour retention policy so history auto-expires without manual cleanup.
def cleanup_history():
    cutoff = datetime.now() - timedelta(hours=24)
    history_records[:] = [
        item for item in history_records if item["timestamp"] >= cutoff
    ]


# Save successful expressions for audit/review and keep list bounded for memory/UI performance.
def add_to_history(expression, result):
    cleanup_history()
    history_records.append(
        {
            "timestamp": datetime.now(),
            "text": f"{expression} = {result}",
        }
    )
    # Keep only the latest 100 records in the 24-hour window
    if len(history_records) > 100:
        history_records[:] = history_records[-100:]


# Show recent calculations in a dedicated scrollable window because history can exceed visible space.
def show_history():
    cleanup_history()

    popup = tk.Toplevel(root)
    popup.title("Calculation History (Last 24 Hours)")
    popup.geometry("420x420")
    popup.configure(bg="#1e1e1e")
    popup.resizable(False, False)

    tk.Label(
        popup,
        text="History (Last 24 Hours)",
        bg="#1e1e1e",
        fg="white",
        font=("Helvetica", 14, "bold"),
    ).pack(pady=(10, 8))

    history_box = tk.Text(
        popup,
        bg="#1E1E2F",
        fg="white",
        font=("Consolas", 11),
        wrap="word",
        bd=0,
        padx=10,
        pady=10,
    )
    scrollbar = tk.Scrollbar(popup, command=history_box.yview)
    history_box.config(yscrollcommand=scrollbar.set)
    history_box.pack(side="left", fill="both", expand=True, padx=(10, 0), pady=(0, 10))
    scrollbar.pack(side="right", fill="y", padx=(0, 10), pady=(0, 10))

    if history_records:
        lines = []
        for item in reversed(history_records):
            stamp = item["timestamp"].strftime("%d-%m-%Y %I:%M:%S %p")
            lines.append(f"{stamp}\n{item['text']}\n")
        history_box.insert("1.0", "\n".join(lines))
    else:
        history_box.insert("1.0", "No calculations in the last 24 hours.")

    history_box.config(state="disabled")


# Reuse one popup style everywhere to keep UI consistent and avoid duplicated popup-building code.
def show_uniform_popup(title, input_text, result_text, geometry="460x260"):
    popup = tk.Toplevel(root)
    popup.title(title)
    popup.geometry(geometry)
    popup.configure(bg="#1e1e1e")
    popup.resizable(False, False)

    tk.Label(
        popup,
        text=title,
        bg="#1e1e1e",
        fg="white",
        font=("Helvetica", 15, "bold"),
    ).pack(anchor="w", padx=12, pady=(12, 8))

    tk.Label(
        popup,
        text=f"Input: {input_text}",
        bg="#1e1e1e",
        fg="#cfe8ff",
        font=("Helvetica", 12),
        justify="left",
        wraplength=430,
    ).pack(anchor="w", padx=12, pady=(0, 8))

    tk.Label(
        popup,
        text=f"Result: {result_text}",
        bg="#1e1e1e",
        fg="white",
        font=("Helvetica", 12, "bold"),
        justify="left",
        wraplength=430,
    ).pack(anchor="w", padx=12)


# Title
tk.Label(
    main_frame,
    text="Basic Calculator",
    bg="#1e1e1e",
    fg="white",
    font=("Helvetica", 18),
).grid(row=0, column=0, columnspan=3, sticky="w", padx=(10, 0))

tk.Button(
    main_frame,
    text="History",
    font=("Helvetica", 11, "bold"),
    bg="#ff9500",
    fg="white",
    bd=0,
    command=show_history,
).grid(row=0, column=3, sticky="e", padx=10, pady=4)

# ================= BASIC CALCULATOR =================
entry = tk.Entry(
    main_frame,
    font=("Segoe UI", 24, "bold"),
    justify="right",
    bg="#1E1E2F",
    fg="white",
    bd=0,
)
entry.grid(row=1, column=0, columnspan=4, sticky="nsew", padx=10, pady=10)


# Append button value to input so keypad and typing follow the same expression-building flow.
def click(value):
    entry.insert(tk.END, str(value))


# Reset input quickly so users can start a new expression without manual deletion.
def clear():
    entry.delete(0, tk.END)


# Allow quick correction of typing mistakes without clearing the whole expression.
def backspace():
    entry.delete(len(entry.get()) - 1)


# Compute basic expression and record it, so users get instant result plus traceable history.
def calculate():
    try:
        expression = entry.get().strip()
        result = eval(expression.replace("%", "/100"))
        entry.delete(0, tk.END)
        entry.insert(0, result)
        add_to_history(expression, result)
    except:
        entry.delete(0, tk.END)
        entry.insert(0, "Error")


# ================= BASIC BUTTONS =================
buttons = [
    ("1", 2, 0),
    ("2", 2, 1),
    ("3", 2, 2),
    ("+", 2, 3),
    ("4", 3, 0),
    ("5", 3, 1),
    ("6", 3, 2),
    ("-", 3, 3),
    ("7", 4, 0),
    ("8", 4, 1),
    ("9", 4, 2),
    ("*", 4, 3),
    ("AC", 5, 0),
    ("0", 5, 1),
    ("⌫", 5, 2),
    ("/", 5, 3),
    (".", 6, 0),
    ("00", 6, 1),
    ("=", 6, 2),
    ("%", 6, 3),
]

for text, r, c in buttons:
    if text == "=":
        cmd = calculate
    elif text == "AC":
        cmd = clear
    elif text == "⌫":
        cmd = backspace
    else:
        cmd = lambda x=text: click(x)

    tk.Button(
        main_frame,
        text=text,
        font=("Helvetica", 18, "bold"),
        bg="#2D2D44" if text not in "+-*/%" else "#ff9500",
        fg="white",
        bd=0,
        command=cmd,
    ).grid(row=r, column=c, sticky="nsew", padx=BTN_PAD_X, pady=BTN_PAD_Y)

# Switch button
tk.Button(main_frame, text="Switch to Scientific Calculator", command=show_second).grid(
    row=8, column=0, columnspan=4, sticky="nsew", padx=10, pady=(6, 3)
)
tk.Button(main_frame, text="Switch to Programmer Calculator", command=show_third).grid(
    row=9, column=0, columnspan=4, sticky="nsew", padx=10, pady=(3, 8)
)

# Grid config
for i in range(10):
    main_frame.grid_rowconfigure(i, weight=1)
for j in range(4):
    main_frame.grid_columnconfigure(j, weight=1)

# ================= SCIENTIFIC CALCULATOR =================

# Title
tk.Label(
    second_frame,
    text="Scientific Calculator",
    bg="#1e1e1e",
    fg="white",
    font=("Helvetica", 18),
).grid(row=0, column=0, columnspan=4, sticky="w", padx=(10, 0))

tk.Button(
    second_frame,
    text="History",
    font=("Helvetica", 11, "bold"),
    bg="#ff9500",
    fg="white",
    bd=0,
    command=show_history,
).grid(row=0, column=4, sticky="e", padx=10, pady=4)

# Entry
sci_entry = tk.Entry(
    second_frame,
    font=("Segoe UI", 24, "bold"),
    justify="right",
    bg="#1E1E2F",
    fg="white",
    bd=0,
)
sci_entry.grid(row=1, column=0, columnspan=5, sticky="nsew", padx=10, pady=10)


# Functions
# Append scientific keypad value into input to build function-based expressions step by step.
def sci_add(val):
    sci_entry.insert(tk.END, str(val))


# Clear scientific input when expression needs a full reset.
def sci_clear():
    sci_entry.delete(0, tk.END)


# Support fine-grained correction while composing long scientific formulas.
def sci_backspace():
    current = sci_entry.get()
    if current:
        sci_entry.delete(len(current) - 1, tk.END)


# Evaluate with a restricted function map to support trig/log/sqrt while limiting unsafe eval access.
def sci_calc():
    try:
        expression = sci_entry.get().strip()
        safe_locals = {
            "sin": lambda x: math.sin(math.radians(x)),
            "cos": lambda x: math.cos(math.radians(x)),
            "tan": lambda x: math.tan(math.radians(x)),
            "log": math.log10,
            "sqrt": math.sqrt,
            "pi": math.pi,
            "e": math.e,
            "math": math,
        }

        result = eval(expression, {"__builtins__": {}}, safe_locals)

        sci_entry.delete(0, tk.END)
        sci_entry.insert(0, result)
        add_to_history(expression, result)

    except Exception as e:
        sci_entry.delete(0, tk.END)
        sci_entry.insert(0, "Error")


# Scientific buttons
sci_buttons = [
    ("sin", 2, 0),
    ("cos", 2, 1),
    ("tan", 2, 2),
    ("log", 2, 3),
    ("AC", 2, 4),
    ("√", 3, 0),
    ("π", 3, 1),
    ("e", 3, 2),
    ("x²", 3, 3),
    ("⌫", 3, 4),
    ("7", 4, 0),
    ("8", 4, 1),
    ("9", 4, 2),
    ("/", 4, 3),
    ("%", 4, 4),
    ("4", 5, 0),
    ("5", 5, 1),
    ("6", 5, 2),
    ("*", 5, 3),
    ("(", 5, 4),
    ("1", 6, 0),
    ("2", 6, 1),
    ("3", 6, 2),
    ("-", 6, 3),
    (")", 6, 4),
    ("00", 7, 0),
    ("0", 7, 1),
    (".", 7, 2),
    ("+", 7, 3),
    ("=", 7, 4),
]

for text, r, c in sci_buttons:
    if text == "=":
        cmd = sci_calc
    elif text == "AC":
        cmd = sci_clear
    elif text == "⌫":
        cmd = sci_backspace
    elif text == "√":
        cmd = lambda: sci_entry.insert(tk.END, "sqrt(")
    elif text == "π":
        cmd = lambda: sci_add(math.pi)
    elif text == "e":
        cmd = lambda: sci_add(math.e)
    elif text == "x²":
        cmd = lambda: sci_entry.insert(tk.END, "**2")
    elif text == "log":
        cmd = lambda: sci_entry.insert(tk.END, "log(")
    elif text in ["sin", "cos", "tan"]:
        cmd = lambda x=text: sci_entry.insert(tk.END, x + "(")
    elif text == "(":
        cmd = lambda: sci_entry.insert(tk.END, "(")
    elif text == ")":
        cmd = lambda: sci_entry.insert(tk.END, ")")
    else:
        cmd = lambda x=text: sci_add(x)

    tk.Button(
        second_frame,
        text=text,
        font=("Helvetica", 14, "bold"),
        bg="#2D2D44" if text not in "+-*/%=AC⌫sincostan√πx²elog()" else "#ff9500",
        fg="white",
        bd=0,
        command=cmd,
    ).grid(row=r, column=c, sticky="nsew", padx=BTN_PAD_X, pady=BTN_PAD_Y)

# Back
tk.Button(second_frame, text="Switch to Basic Calculator", command=show_main).grid(
    row=9, column=0, columnspan=5, sticky="nsew", padx=10, pady=(6, 3)
)
tk.Button(
    second_frame, text="Switch to Programmer Calculator", command=show_third
).grid(row=10, column=0, columnspan=5, sticky="nsew", padx=10, pady=(3, 8))

# Grid config
for i in range(11):
    second_frame.grid_rowconfigure(i, weight=1)
for j in range(5):
    second_frame.grid_columnconfigure(j, weight=1)

# ================= PROGRAMMER CALCULATOR =================

tk.Label(
    third_frame,
    text="Programmer Calculator",
    bg="#1e1e1e",
    fg="white",
    font=("Helvetica", 18),
).grid(row=0, column=0, columnspan=4, sticky="w", padx=(10, 0))

tk.Button(
    third_frame,
    text="History",
    font=("Helvetica", 11, "bold"),
    bg="#ff9500",
    fg="white",
    bd=0,
    command=show_history,
).grid(row=0, column=4, sticky="e", padx=10, pady=4)

prog_entry = tk.Entry(
    third_frame,
    font=("Segoe UI", 20, "bold"),
    justify="right",
    bg="#1E1E2F",
    fg="white",
    bd=0,
)
prog_entry.grid(row=1, column=0, columnspan=5, sticky="nsew", padx=10, pady=8)

prog_second_entry = tk.Entry(
    third_frame,
    font=("Segoe UI", 12),
    justify="right",
    bg="#2B2B3D",
    fg="white",
    bd=0,
)
prog_second_entry.grid(row=2, column=0, columnspan=5, sticky="nsew", padx=10, pady=4)
prog_second_entry.insert(0, "Second value (for AND/OR/XOR)")

bin_var = tk.StringVar(value="BIN: ")
oct_var = tk.StringVar(value="OCT: ")
hex_var = tk.StringVar(value="HEX: ")
dec_var = tk.StringVar(value="DEC: ")
bin_visual_var = tk.StringVar(value="Binary Visualizer: ")


def prog_add(value):
    # Keep programmer input assembly identical to button presses for predictable binary/hex workflows.
    prog_entry.insert(tk.END, str(value))


def prog_clear():
    # Fast reset for programmer calculations and conversions.
    prog_entry.delete(0, tk.END)


def prog_backspace():
    # Fix input typos without losing full number/expression.
    current = prog_entry.get()
    if current:
        prog_entry.delete(len(current) - 1, tk.END)


def update_programmer_outputs(number):
    # Update all base views together so conversion state stays synchronized after every numeric operation.
    bin_var.set(f"BIN: {bin(number)}")
    oct_var.set(f"OCT: {oct(number)}")
    hex_var.set(f"HEX: {hex(number).upper().replace('X', 'x')}")
    dec_var.set(f"DEC: {number}")
    masked = number & 0xFFFFFFFF
    bits = f"{masked:032b}"
    grouped_bits = " ".join(bits[i : i + 4] for i in range(0, 32, 4))
    bin_visual_var.set(f"Binary Visualizer: {grouped_bits}")


def parse_programmer_int(text, base=10):
    # Normalize multiple numeric formats into integers so bitwise/shift logic can run reliably.
    value = text.strip()
    if not value:
        raise ValueError
    if value.lower() == "second value (for and/or/xor)":
        raise ValueError

    # Accept developer-style formats (0b/0o/0x or hex chars) to reduce manual conversion effort.
    lower_value = value.lower()
    if base == 10:
        if lower_value.startswith(("0b", "0o", "0x")):
            return int(lower_value, 0)
        # Treat A-F text as hex even without prefix, matching common programmer calculator behavior.
        if any(ch in "abcdef" for ch in lower_value):
            return int(lower_value, 16)
        # Allow float-looking integers from previous eval results (e.g., 12.0) by coercing to int.
        return int(float(value))

    return int(value, base)


def prog_calc():
    # Evaluate expression then refresh base labels so arithmetic and conversion views remain aligned.
    try:
        expression = prog_entry.get().strip()
        result = eval(expression, {"__builtins__": {}}, {})
        prog_entry.delete(0, tk.END)
        prog_entry.insert(0, result)
        if isinstance(result, (int, float)) and float(result).is_integer():
            update_programmer_outputs(int(result))
        add_to_history(expression, result)
    except:
        prog_entry.delete(0, tk.END)
        prog_entry.insert(0, "Error")


def convert_from_decimal():
    # One-click conversion from decimal to all primary programmer bases.
    try:
        number = parse_programmer_int(prog_entry.get(), 10)
        update_programmer_outputs(number)
        add_to_history(
            f"DEC convert {number}",
            f"BIN:{bin(number)} OCT:{oct(number)} HEX:{hex(number)}",
        )
    except:
        prog_entry.delete(0, tk.END)
        prog_entry.insert(0, "Error")


def convert_to_decimal(base):
    # Convert non-decimal input into decimal and immediately refresh all base labels for comparison.
    try:
        text = prog_entry.get().strip()
        number = parse_programmer_int(text, base)
        prog_entry.delete(0, tk.END)
        prog_entry.insert(0, str(number))
        update_programmer_outputs(number)
        add_to_history(f"Base-{base} {text}", number)
    except:
        prog_entry.delete(0, tk.END)
        prog_entry.insert(0, "Error")


def fibonacci_series():
    # Generate series for educational/algorithmic use and show readable output in a consistent popup format.
    try:
        n = parse_programmer_int(prog_entry.get(), 10)
        if n <= 0:
            raise ValueError
        series = []
        a, b = 0, 1
        for _ in range(n):
            series.append(str(a))
            a, b = b, a + b
        nth_value = int(series[-1])
        result_text = ", ".join(series)
        show_fibonacci_popup(
            str(n),
            f"First {n} Fibonacci terms: {result_text}\nNth term value: {nth_value}",
        )
        add_to_history(f"Fibonacci n={n}", f"Nth={nth_value}")
    except:
        prog_entry.delete(0, tk.END)
        prog_entry.insert(0, "Error")


def bitwise_operation(operator_name):
    # Execute bitwise ops on two operands because these operations require a separate right-hand input.
    try:
        left = parse_programmer_int(prog_entry.get(), 10)
        right_text = prog_second_entry.get().strip()
        right = parse_programmer_int(right_text, 10)
        if operator_name == "AND":
            result = left & right
        elif operator_name == "OR":
            result = left | right
        else:
            result = left ^ right
        prog_entry.delete(0, tk.END)
        prog_entry.insert(0, str(result))
        prog_second_entry.delete(0, tk.END)
        prog_second_entry.insert(0, "Second value (for AND/OR/XOR)")
        update_programmer_outputs(result)
        add_to_history(f"{left} {operator_name} {right}", result)
    except:
        show_uniform_popup(
            "Bitwise Input Error",
            "Left and right values",
            "Enter valid numbers in both fields.\nExamples: Left: 10, Right: 3\nAlso supported: 0b1010, 0x1F, 0o17",
        )


def shift_operation(direction):
    # Apply bit shifts using second box as shift count, mirroring standard programmer calculator UX.
    try:
        number = parse_programmer_int(prog_entry.get(), 10)
        shift_by = parse_programmer_int(prog_second_entry.get(), 10)
        if shift_by < 0:
            raise ValueError
        result = number << shift_by if direction == "LEFT" else number >> shift_by
        prog_entry.delete(0, tk.END)
        prog_entry.insert(0, str(result))
        update_programmer_outputs(result)
        add_to_history(
            f"{number} {'<<' if direction == 'LEFT' else '>>'} {shift_by}", result
        )
    except:
        show_uniform_popup(
            "Shift Input Error",
            "Value and shift count",
            "Enter a value in top box and a non-negative shift count in second box.",
        )


def show_ascii_popup(input_text, result_text):
    # Keep ASCII output popup visually consistent with other tool result windows.
    show_uniform_popup("ASCII Conversion", input_text, result_text, "460x240")


def show_fibonacci_popup(input_text, result_text):
    # Reuse same popup style for Fibonacci to preserve UI consistency across features.
    show_uniform_popup("Fibonacci Conversion", input_text, result_text, "460x260")


def ascii_convert():
    # Support both conversion directions so one button handles practical ASCII lookup scenarios.
    value = prog_entry.get().strip()
    try:
        number = parse_programmer_int(value, 10)
        if 0 <= number <= 1114111:
            char_value = chr(number)
            show_ascii_popup(str(number), char_value)
            add_to_history(f"ASCII from {number}", char_value)
        else:
            raise ValueError
    except:
        if value:
            ascii_codes = [str(ord(ch)) for ch in value]
            result = ", ".join(ascii_codes)
            show_ascii_popup(value, result)
            add_to_history(f"ASCII codes of '{value}'", result)
        else:
            show_uniform_popup(
                "ASCII Convert Error",
                "Top input",
                "Enter a number or text in top input.",
                "460x220",
            )


tk.Label(third_frame, textvariable=bin_var, bg="#1e1e1e", fg="white", anchor="w").grid(
    row=3, column=0, columnspan=5, sticky="ew", padx=10
)
tk.Label(third_frame, textvariable=oct_var, bg="#1e1e1e", fg="white", anchor="w").grid(
    row=4, column=0, columnspan=5, sticky="ew", padx=10
)
tk.Label(third_frame, textvariable=hex_var, bg="#1e1e1e", fg="white", anchor="w").grid(
    row=5, column=0, columnspan=5, sticky="ew", padx=10
)
tk.Label(third_frame, textvariable=dec_var, bg="#1e1e1e", fg="white", anchor="w").grid(
    row=6, column=0, columnspan=5, sticky="ew", padx=10
)
tk.Label(
    third_frame, textvariable=bin_visual_var, bg="#1e1e1e", fg="#9fd3ff", anchor="w"
).grid(row=7, column=0, columnspan=5, sticky="ew", padx=10)

prog_buttons = [
    ("7", 8, 0),
    ("8", 8, 1),
    ("9", 8, 2),
    ("/", 8, 3),
    ("AC", 8, 4),
    ("4", 9, 0),
    ("5", 9, 1),
    ("6", 9, 2),
    ("*", 9, 3),
    ("⌫", 9, 4),
    ("1", 10, 0),
    ("2", 10, 1),
    ("3", 10, 2),
    ("-", 10, 3),
    ("AND", 10, 4),
    ("00", 11, 0),
    ("0", 11, 1),
    (".", 11, 2),
    ("+", 11, 3),
    ("OR", 11, 4),
    ("=", 12, 0),
    ("<<", 12, 1),
    (">>", 12, 2),
    ("XOR", 12, 3),
    ("FIB", 12, 4),
    ("DEC->", 13, 0),
    ("BIN->DEC", 13, 1),
    ("OCT->DEC", 13, 2),
    ("HEX->DEC", 13, 3),
    ("ASCII", 13, 4),
]

for text, r, c in prog_buttons:
    if text == "=":
        cmd = prog_calc
    elif text == "AC":
        cmd = prog_clear
    elif text == "⌫":
        cmd = prog_backspace
    elif text == "DEC->":
        cmd = convert_from_decimal
    elif text == "BIN->DEC":
        cmd = lambda: convert_to_decimal(2)
    elif text == "OCT->DEC":
        cmd = lambda: convert_to_decimal(8)
    elif text == "HEX->DEC":
        cmd = lambda: convert_to_decimal(16)
    elif text == "FIB":
        cmd = fibonacci_series
    elif text == "<<":
        cmd = lambda: shift_operation("LEFT")
    elif text == ">>":
        cmd = lambda: shift_operation("RIGHT")
    elif text == "ASCII":
        cmd = ascii_convert
    elif text in ("AND", "OR", "XOR"):
        cmd = lambda x=text: bitwise_operation(x)
    else:
        cmd = lambda x=text: prog_add(x)

    tk.Button(
        third_frame,
        text=text,
        font=("Helvetica", 12, "bold"),
        bg=(
            "#2D2D44"
            if text not in "+-*/=AC⌫ANDORXOR<<>>DEC->BIN->DECOCT->DECHEX->DECFIBASCII"
            else "#ff9500"
        ),
        fg="white",
        bd=0,
        command=cmd,
    ).grid(row=r, column=c, sticky="nsew", padx=BTN_PAD_X, pady=BTN_PAD_Y)

tk.Button(third_frame, text="Switch to Basic Calculator", command=show_main).grid(
    row=14, column=0, columnspan=5, sticky="nsew", padx=10, pady=(6, 3)
)
tk.Button(
    third_frame, text="Switch to Scientific Calculator", command=show_second
).grid(row=15, column=0, columnspan=5, sticky="nsew", padx=10, pady=(3, 8))

for i in range(16):
    third_frame.grid_rowconfigure(i, weight=1)
for j in range(5):
    third_frame.grid_columnconfigure(j, weight=1)


def on_second_entry_focus_in(_event=None):
    # Remove placeholder text on focus so users can type second operand immediately.
    if prog_second_entry.get().strip() == "Second value (for AND/OR/XOR)":
        prog_second_entry.delete(0, tk.END)


def on_second_entry_focus_out(_event=None):
    # Restore placeholder when field is left empty to communicate expected second-operand input.
    if not prog_second_entry.get().strip():
        prog_second_entry.insert(0, "Second value (for AND/OR/XOR)")


prog_second_entry.bind("<FocusIn>", on_second_entry_focus_in)
prog_second_entry.bind("<FocusOut>", on_second_entry_focus_out)
root.bind("<Return>", handle_enter)

# ================= RUN =================
root.mainloop()
