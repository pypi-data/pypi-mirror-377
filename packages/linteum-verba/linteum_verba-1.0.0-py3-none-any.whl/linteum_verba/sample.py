"""
Linteum Verba - Sample Python Code
This file demonstrates syntax highlighting and code folding
"""
from typing import List


class SampleClass:
    """A sample class to demonstrate syntax highlighting and folding"""

    def __init__(self, name: str, value: int = 42):
        self.name = name
        self.value = value
        self.items = []
        
        # Initialize with some default items
        for i in range(5):
            self.items.append(f"Item {i}")

    def process_items(self) -> List[str]:
        """Process all items in the collection"""
        result = []
        
        # This block can be folded
        for item in self.items:
            # Process each item
            processed = item.upper()
            if len(processed) > 10:
                # Truncate long items
                processed = processed[:10] + "..."
            result.append(processed)
            
        return result

    def calculate_value(self, multiplier: float) -> float:
        """Calculate a new value based on the multiplier"""
        # Simple calculation with a string representation
        new_value = self.value * multiplier
        
        if new_value > 100:
            # This block can be folded
            print(f"Warning: Value {new_value} exceeds 100")
            new_value = 100
        elif new_value < 0:
            # This block can also be folded
            print(f"Warning: Value {new_value} is negative")
            new_value = 0
            
        return new_value


def main():
    """Main function to demonstrate the sample class"""
    # Create an instance of the sample class
    sample = SampleClass("Example", 50)
    
    # Process items
    processed_items = sample.process_items()
    print(f"Processed items: {processed_items}")

    # Calculate values with different multipliers
    values = []
    for mult in [0.5, 1.0, 2.0, 3.0]:
        value = sample.calculate_value(mult)
        values.append(value)
        
    print(f"Calculated values: {values}")

    # Create a simple GUI to display the results
    def create_gui():
        """Create a simple GUI to display results"""
        import tkinter as tk
        root = tk.Tk()
        root.title("Sample Results")

        # Create a frame for the results
        frame = tk.Frame(root, padx=10, pady=10)
        frame.pack(fill="both", expand=True)

        # Add labels for the results
        tk.Label(frame, text="Processed Items:").grid(row=0, column=0, sticky="w")
        for i, item in enumerate(processed_items):
            tk.Label(frame, text=f"  {item}").grid(row=i + 1, column=0, sticky="w")

        tk.Label(frame, text="Calculated Values:").grid(row=0, column=1, sticky="w")
        for i, value in enumerate(values):
            tk.Label(frame, text=f"  {value}").grid(row=i + 1, column=1, sticky="w")

        # Start the GUI
        root.mainloop()

    # Uncomment to run the GUI
    # create_gui()


if __name__ == "__main__":
    main()
