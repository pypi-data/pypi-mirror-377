import colorsys
import os
import streamlit as st
from typing import List

__version__ = "0.1.0"


def split_button(label: str, options: List[str], icon: str | None = None, key: str = None):
    """Create a split button component 
        A split button is a combination of a primary action button and a dropdown menu.

        The primary action button is always visible, while the dropdown menu is hidden until the user interacts with the button.
        The button design is inspired by the Google Material Design 3 design system.
        
            The component returns the label of the button or the selected option from the dropdown menu, or None if no action has been taken.
        
        Args:
            label: The label of the primary action button.
            options: A list of options for the dropdown menu.
            icon: An optional icon to display on the primary action button. Identical to st.button icon parameter.
            key: An optional key to use for the component. If not provided, a default key will be used.
            
        Returns:
            The label of the button or the selected option from the dropdown menu, or None
            
        Raises:
            ValueError: If the options list is empty.
    """
    
    if len(options) == 0:
        raise ValueError("The options list must contain at least one option.")
    
    return_value = None
    key = key or "streamlit-split-button"
    
    main_container = st.container(key=key)
    
    # Extract primary color from theme and calculated derived colors
    # Hover color is decreased lightness by 15%
    # Shadow color is primary color with 50% opacity
    primary_color = st.get_option("theme.primaryColor")
    if primary_color is None:
        primary_color = "#ff4b4b"
    
    # Darken Primary Color
    primary_color_rgb = primary_color.lstrip('#')
    primary_color_rgb = tuple(int(primary_color_rgb[i:i+2], 16) for i in (0, 2, 4))

    h,l,s = colorsys.rgb_to_hls(primary_color_rgb[0]/255, primary_color_rgb[1]/255, primary_color_rgb[2]/255)
    l = max(0, l - 0.15) # Decrease lightness by 15%
    
    r,g,b = colorsys.hls_to_rgb(h, l, s)
    primary_hover_color = '#%02x%02x%02x' % (int(r*255), int(g*255), int(b*255))
    primary_hover_shadow = primary_color + '80' # Add 50% opacity to match
    
    # Apply CSS to style the button and selectbox to look like a split button
    st.html(f"""
    <style>
    .st-key-{key} {{
        display: flex;
        flex-direction: row;
        gap: 2px;
    }}
    
    .st-key-{key} button {{
        width: max-content;
        padding-left: 16px;
        padding-right: 12px;
        padding-top: 4px;
        padding-bottom: 4px;
        margin: 0px;
        border-top-right-radius: 4px;
        border-bottom-right-radius: 4px;
        border-top-left-radius: 20px;
        border-bottom-left-radius: 20px;
    }}
    
    .st-key-{key}-selectbox {{
        width: max-content;
    }}
    
    .st-key-{key}-selectbox > div > div > div {{
        background-color: {primary_color};
        border-color: {primary_color};
        border-top-right-radius: 20px;
        border-bottom-right-radius: 20px;
        border-top-left-radius: 4px;
        border-bottom-left-radius: 4px;
    }}
    
    .st-key-{key}-selectbox > div > div > div:hover {{
        background-color: {primary_hover_color};
        border-color: {primary_hover_color};
    }}
    
    .st-key-{key}-selectbox > div > div > div:active {{
        background-color: {primary_color};
        border-color: {primary_color};
    }}

    .st-key-{key}-selectbox div[data-testid="stSelectbox"]:has(input:focus) > div > div {{
        box-shadow: {primary_hover_shadow} 0px 0px 0px 0.2rem;
        background-color: {primary_hover_color};
    }}
    
    .st-key-{key}-selectbox > div > div > div > div:has(svg) {{
        padding-right: 11px;
        padding-left: 9px;
    }}
    
    .st-key-{key}-selectbox svg {{
        color: #FFFFFF;
    }}
    
    .st-key-{key}-selectbox svg[title="Clear value"]  {{
        display: none;
    }}
    
    .st-key-{key}-selectbox div[data-baseweb="select"] > div > div > div:not(:has(input))  {{
        display: none;
    }}
    
    .st-key-{key}-selectbox div[data-baseweb="select"] > div > div:has(input)  {{
        background-color: red;
        padding: 0px;
        width: 0px;
        min-width: 0px;
        flex-grow: 0;
    }}
    
    div[data-baseweb="popover"] div ul {{
       min-width: 160px;
    }}
    
    .st-key-{key}-selectbox div[data-testid="stSelectbox"]:has(input:disabled) > div > div {{
        background-color: transparent;
        border-color: {primary_hover_color};
    }}
    
    </style>
    """)
    
    # Place button and selectbox in a horizontal container
    with main_container:
        if st.button(label,
                     icon=icon,
                     use_container_width=False,
                     key=f"{key}-button",
                     type="primary"):
            return_value = label
        
        select_value = st.selectbox(label="split-button",
                                    options=options,
                                    key=f"{key}-selectbox",
                                    label_visibility="collapsed",
                                    index=None)

        if not return_value and select_value:
            return_value = select_value

    return return_value


if __name__ == "__main__":
    # If this file is run directly, we can test our component in a simple
    # Streamlit app.
    clicks = split_button(label="Hello",
                          options=["Click Me 1", "Click Me 2", "Click Me 3"])
        
    st.write(f"You clicked the option {clicks}.")
    
    # Test99
    
    clicks = split_button(label="Hello",
                          icon=":material/home:",
                          options=["Click Me 1", "Click Me 2", "Click Me 3"],
                          key="test01")

    st.write(f"You clicked the option {clicks}.")