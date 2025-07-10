import matplotlib.pyplot as plt
import matplotlib.patches as patches

def draw_rooftop_layout(
    rooftop_area_m2=None,
    system_size_kw=None,
    panel_width=1.0,    # Standard panel width in meters
    panel_height=1.6,    # Standard panel height in meters
    panel_capacity=0.4,  # kW per panel (typical 400W panel)
    shadow_zone=None,
    output_path="generated_pdfs/rooftop_layout.png"

):
    
    # Calculate dimensions if not provided
    if rooftop_area_m2 is None or system_size_kw is None:
        # Default fallback values
        width_m = 10
        height_m = 7
        num_panels = 12
    else:
        # Calculate roof dimensions (assuming rectangular roof)
        width_m = (rooftop_area_m2 ** 0.5) * 1.2  # Approximate with aspect ratio
        height_m = rooftop_area_m2 / width_m
        
        # Calculate number of panels needed
        num_panels = int(system_size_kw * 1000 / panel_capacity)
    
    fig, ax = plt.subplots(figsize=(8, 6))
    
    # Draw rooftop base
    ax.add_patch(patches.Rectangle(
        (0, 0), width_m, height_m, 
        fill=True, color="#f0f0f0", edgecolor="black",
        label=f"Rooftop Area: {rooftop_area_m2:.1f}m²" if rooftop_area_m2 else None
    ))
    
    # Calculate panel arrangement
    panels_per_row = max(1, int(width_m // (panel_width + 0.3)))
    num_rows = max(1, int(num_panels / panels_per_row))
    
    # Draw solar panels
    panels_drawn = 0
    for row in range(num_rows):
        for col in range(panels_per_row):
            if panels_drawn >= num_panels:
                break
                
            x = 0.5 + col * (panel_width + 0.3)  # 0.5m margin + spacing
            y = height_m - 0.5 - row * (panel_height + 0.3)  # 0.5m margin
            
            if x + panel_width < width_m and y - panel_height > 0:
                panel = patches.Rectangle(
                    (x, y - panel_height),
                    panel_width,
                    panel_height,
                    linewidth=1,
                    edgecolor="#2c7e3a",
                    facecolor="#4CAF50",
                    label=f"{panel_capacity}kW Panel" if panels_drawn == 0 else None
                )
                ax.add_patch(panel)
                panels_drawn += 1

    # Draw shadow zone if provided
    if shadow_zone:
        ax.add_patch(patches.Rectangle(
            (shadow_zone[0], shadow_zone[1]),
            shadow_zone[2],
            shadow_zone[3],
            fill=True,
            color="black",
            alpha=0.3,
            hatch='///',
            label="Shadow Zone"
        ))
    else:
        ax.add_patch(patches.Rectangle(
            (0, 0), width_m, height_m,
            fill=False, edgecolor="gray", linestyle='--',
            label="No Shadow Zone"
        ))
    # Formatting
    ax.set_xlim(0, width_m)
    ax.set_ylim(0, height_m)
    ax.set_aspect('equal')
    ax.set_title(f"Rooftop Layout - {system_size_kw}kW System" if system_size_kw else "Rooftop Layout")
    
    # Add legend if we have labels
    handles, labels = ax.get_legend_handles_labels()
    if handles:
        ax.legend(handles, labels, loc='upper right', bbox_to_anchor=(1.3, 1))
    
    ax.axis('off')
    plt.tight_layout()
    plt.savefig(output_path, bbox_inches='tight', dpi=150)
    plt.close()# Close the plot to free up memory