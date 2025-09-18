from rapidocr import RapidOCR
import numpy as np

def extract_text_from_image(img_path):
    """
    Extract text from an image using OCR.
    
    Args:
        img_path (str): Path to the image file
        
    Returns:
        str: Extracted text with preserved formatting and indentation
    """
    engine = RapidOCR()
    result = engine(img_path)
    
    # if not result or not result.boxes:
    #     return ""
    
    boxes = result.boxes
    txts = result.txts
    
    # Step 1: Compute top y of each box
    y_coords = [box[:,1].min() for box in boxes]
    
    # Step 2: Sort words top-to-bottom
    sorted_indices = sorted(range(len(txts)), key=lambda i: y_coords[i])
    
    # Step 3: Group words into lines
    lines = []
    current_line = []
    current_y = None
    line_threshold = 10  # pixels
    
    for i in sorted_indices:
        top_y = boxes[i][:,1].min()
        if current_y is None:
            current_y = top_y
        
        if abs(top_y - current_y) > line_threshold:
            # New line
            # Sort previous line left-to-right
            current_line_sorted = sorted(current_line, key=lambda idx: boxes[idx][:,0].min())
            lines.append(current_line_sorted)
            current_line = [i]
            current_y = top_y
        else:
            current_line.append(i)
    
    # Add last line
    if current_line:
        current_line_sorted = sorted(current_line, key=lambda idx: boxes[idx][:,0].min())
        lines.append(current_line_sorted)
    
    # Step 4: Build final text with indentation
    final_text_lines = []
    for line_indices in lines:
        if not line_indices:
            continue
        first_word_x = boxes[line_indices[0]][:,0].min()
        indent = " " * int(first_word_x // 20 * 4)  # approximate
        line_text = " ".join([txts[i] for i in line_indices])
        final_text_lines.append(indent + line_text)
    
    return "\n".join(final_text_lines)

if __name__ == "__main__":
    # Example usage - only runs when script is executed directly
    img_path = "screenshot.png"
    final_text = extract_text_from_image(img_path)
    # Write to file
    output_file = "reconstructed_code.txt"
    with open(output_file, "w") as f:
        f.write(final_text)

